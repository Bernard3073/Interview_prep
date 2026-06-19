"""Incremental Structure-from-Motion driver.

Pipeline (see Week 10 A1.1 for the conceptual walkthrough):
  1. Build feature tracks from verified pairwise matches.
  2. Initialise from the best image pair (most matches): essential matrix ->
     relative pose -> triangulate the shared tracks.
  3. Incrementally register the remaining images: 2D-3D correspondences from
     already-triangulated tracks -> PnP (RANSAC) -> add the camera, then
     triangulate newly-visible tracks against registered neighbours.
  4. Bundle-adjust periodically and once at the end.

This is intentionally compact and readable rather than maximally robust -- it is a
teaching implementation, not COLMAP. The bottlenecks and failure modes it exposes
(degenerate pairs, drift, scale) are exactly the talking points in the notes.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import cv2
import numpy as np

from . import geometry
from .bundle import bundle_adjust
from .camera import Camera
from .features import ImageFeatures
from .matching import PairMatches
from .tracks import Track, build_tracks


@dataclass
class Reconstruction:
    cameras: dict = field(default_factory=dict)        # image_idx -> Camera
    points3d: dict = field(default_factory=dict)       # track_id -> (3,) world point
    colors: dict = field(default_factory=dict)         # track_id -> (3,) RGB uint8

    def registered(self):
        return set(self.cameras.keys())


class IncrementalSfM:
    def __init__(
        self,
        features: list[ImageFeatures],
        pair_matches: list[PairMatches],
        K: np.ndarray,
        colors_per_image: list[np.ndarray] | None = None,
        min_triangulation_angle_deg: float = 2.0,
        ba_every: int = 2,
        verbose: bool = True,
    ):
        self.feats = features
        self.K = np.asarray(K, dtype=np.float64)
        self.colors_imgs = colors_per_image
        self.min_angle = np.deg2rad(min_triangulation_angle_deg)
        self.ba_every = ba_every
        self.verbose = verbose

        self.tracks: list[Track] = build_tracks(pair_matches)
        self.pair_lookup = {(pm.i, pm.j): pm for pm in pair_matches}
        # Map (image, keypoint) -> track_id for fast 2D->3D lookups.
        self._node_to_track: dict = {}
        for tr in self.tracks:
            for img, kp in tr.obs.items():
                self._node_to_track[(img, kp)] = tr.track_id
        self.tracks_by_id = {tr.track_id: tr for tr in self.tracks}
        self.rec = Reconstruction()

    # ---- helpers ---------------------------------------------------------

    def _log(self, *a):
        if self.verbose:
            print(*a)

    def _pixel(self, img: int, kp: int) -> np.ndarray:
        return self.feats[img].xy[kp]

    def _color(self, img: int, kp: int):
        if self.colors_imgs is None:
            return np.array([200, 200, 200], dtype=np.uint8)
        x, y = self._pixel(img, kp)
        h, w = self.colors_imgs[img].shape[:2]
        xi = int(np.clip(round(x), 0, w - 1))
        yi = int(np.clip(round(y), 0, h - 1))
        b, g, r = self.colors_imgs[img][yi, xi]    # OpenCV is BGR
        return np.array([r, g, b], dtype=np.uint8)

    def _best_initial_pair(self):
        return max(self.pair_lookup.values(), key=len, default=None)

    # ---- core steps ------------------------------------------------------

    def _initialize(self) -> bool:
        pm = self._best_initial_pair()
        if pm is None:
            self._log("No matched pairs to initialise from.")
            return False
        i, j = pm.i, pm.j
        pts_i = self.feats[i].xy[pm.matches[:, 0]]
        pts_j = self.feats[j].xy[pm.matches[:, 1]]

        pose = geometry.estimate_pose(pts_i, pts_j, self.K)
        if pose is None:
            self._log("Essential-matrix pose recovery failed on the seed pair.")
            return False
        R, t, inliers = pose

        self.rec.cameras[i] = Camera.identity()        # first camera defines the frame
        self.rec.cameras[j] = Camera(R=R, t=t)         # second up-to-scale

        P1 = self.rec.cameras[i].P(self.K)
        P2 = self.rec.cameras[j].P(self.K)
        used = pm.matches[inliers]
        X = geometry.triangulate(P1, P2, self.feats[i].xy[used[:, 0]], self.feats[j].xy[used[:, 1]])

        front1 = geometry.in_front(X, self.rec.cameras[i].R, self.rec.cameras[i].t)
        front2 = geometry.in_front(X, self.rec.cameras[j].R, self.rec.cameras[j].t)
        ok = front1 & front2
        added = 0
        for (ki, kj), Xp, good in zip(used, X, ok):
            if not good:
                continue
            tid = self._node_to_track.get((i, int(ki)))
            if tid is None:
                continue
            self.rec.points3d[tid] = Xp
            self.rec.colors[tid] = self._color(i, int(ki))
            added += 1
        self._log(f"Initialised from pair ({i},{j}) with {added} points.")
        return added > 0

    def _correspondences_2d3d(self, img: int):
        """For an unregistered image, gather (2D pixel, 3D point) from tracks already
        triangulated. Returns pixels (M,2), points (M,3), track_ids list."""
        pix, X, tids = [], [], []
        for kp in range(len(self.feats[img].xy)):
            tid = self._node_to_track.get((img, kp))
            if tid is not None and tid in self.rec.points3d:
                pix.append(self._pixel(img, kp))
                X.append(self.rec.points3d[tid])
                tids.append(tid)
        if not pix:
            return None
        return np.array(pix), np.array(X), tids

    def _register_next(self) -> bool:
        candidates = [
            img for img in range(len(self.feats)) if img not in self.rec.cameras
        ]
        best = None
        for img in candidates:
            corr = self._correspondences_2d3d(img)
            if corr is None:
                continue
            if best is None or len(corr[2]) > len(best[1][2]):
                best = (img, corr)
        if best is None or len(best[1][2]) < 6:
            return False

        img, (pix, X, _tids) = best
        ok, rvec, tvec, inliers = cv2.solvePnPRansac(
            X.reshape(-1, 1, 3).astype(np.float64),
            pix.reshape(-1, 1, 2).astype(np.float64),
            self.K,
            None,
            reprojectionError=4.0,
            confidence=0.999,
            iterationsCount=200,
            flags=cv2.SOLVEPNP_EPNP,
        )
        if not ok or inliers is None or len(inliers) < 6:
            self._log(f"PnP failed for image {img}.")
            # Mark as attempted by giving it identity? No -- skip; avoid infinite loop.
            self.rec.cameras.setdefault(img, None)
            return True
        R, _ = cv2.Rodrigues(rvec)
        self.rec.cameras[img] = Camera(R=R, t=tvec.ravel())
        self._log(f"Registered image {img} via PnP ({len(inliers)} inliers).")

        self._triangulate_new(img)
        return True

    def _triangulate_new(self, img: int):
        """Triangulate tracks newly connectable now that `img` is registered."""
        cam = self.rec.cameras[img]
        if cam is None:
            return
        P_new = cam.P(self.K)
        added = 0
        for other in self.rec.registered():
            if other == img or self.rec.cameras[other] is None:
                continue
            key = (min(img, other), max(img, other))
            pm = self.pair_lookup.get(key)
            if pm is None:
                continue
            P_other = self.rec.cameras[other].P(self.K)
            for ki, kj in pm.matches:
                # orient (kp_in_img, kp_in_other)
                if pm.i == img:
                    kp_img, kp_other = int(ki), int(kj)
                else:
                    kp_img, kp_other = int(kj), int(ki)
                tid = self._node_to_track.get((img, kp_img))
                if tid is None or tid in self.rec.points3d:
                    continue
                x1 = self._pixel(img, kp_img).reshape(1, 2)
                x2 = self._pixel(other, kp_other).reshape(1, 2)
                X = geometry.triangulate(P_new, P_other, x1, x2)[0]
                if not (geometry.in_front(X[None], cam.R, cam.t)[0] and
                        geometry.in_front(X[None], self.rec.cameras[other].R, self.rec.cameras[other].t)[0]):
                    continue
                if self._triangulation_angle(X, cam, self.rec.cameras[other]) < self.min_angle:
                    continue                                   # weak parallax -> skip
                self.rec.points3d[tid] = X
                self.rec.colors[tid] = self._color(img, kp_img)
                added += 1
        if added:
            self._log(f"  + {added} new points from image {img}.")

    @staticmethod
    def _triangulation_angle(X, cam_a: Camera, cam_b: Camera) -> float:
        ray_a = X - cam_a.center
        ray_b = X - cam_b.center
        cos = np.dot(ray_a, ray_b) / (np.linalg.norm(ray_a) * np.linalg.norm(ray_b) + 1e-12)
        return float(np.arccos(np.clip(cos, -1.0, 1.0)))

    # ---- bundle adjustment ----------------------------------------------

    def _run_ba(self):
        cam_ids = [i for i, c in self.rec.cameras.items() if c is not None]
        if len(cam_ids) < 2 or len(self.rec.points3d) < 1:
            return
        cam_index = {img: k for k, img in enumerate(cam_ids)}
        pt_ids = list(self.rec.points3d.keys())
        pt_index = {tid: k for k, tid in enumerate(pt_ids)}

        camera_params = np.zeros((len(cam_ids), 6))
        for img in cam_ids:
            c = self.rec.cameras[img]
            rvec, _ = cv2.Rodrigues(c.R)
            camera_params[cam_index[img], :3] = rvec.ravel()
            camera_params[cam_index[img], 3:] = c.t
        points3d = np.array([self.rec.points3d[tid] for tid in pt_ids])

        cam_idx, pt_idx, pixels = [], [], []
        for tid in pt_ids:
            tr = self.tracks_by_id[tid]
            for img, kp in tr.obs.items():
                if img in cam_index:
                    cam_idx.append(cam_index[img])
                    pt_idx.append(pt_index[tid])
                    pixels.append(self._pixel(img, kp))
        cam_idx = np.array(cam_idx)
        pt_idx = np.array(pt_idx)
        pixels = np.array(pixels)

        result = bundle_adjust(camera_params, points3d, cam_idx, pt_idx, pixels, self.K)
        self._log(f"  BA cost {result.cost_before:.1f} -> {result.cost_after:.1f}")

        for img in cam_ids:
            p = result.camera_params[cam_index[img]]
            R, _ = cv2.Rodrigues(p[:3])
            self.rec.cameras[img] = Camera(R=R, t=p[3:6])
        for tid in pt_ids:
            self.rec.points3d[tid] = result.points3d[pt_index[tid]]

    # ---- driver ----------------------------------------------------------

    def run(self) -> Reconstruction:
        if not self._initialize():
            return self.rec
        self._run_ba()
        steps = 0
        while self._register_next():
            steps += 1
            if steps % self.ba_every == 0:
                self._run_ba()
        self._run_ba()                       # final global refine
        # drop placeholder (failed-PnP) cameras
        self.rec.cameras = {k: v for k, v in self.rec.cameras.items() if v is not None}
        self._log(
            f"Done: {len(self.rec.cameras)} cameras, {len(self.rec.points3d)} points."
        )
        return self.rec
