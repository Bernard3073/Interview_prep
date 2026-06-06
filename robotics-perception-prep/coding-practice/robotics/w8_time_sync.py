"""
Week 8 — Nearest-timestamp message synchronizer.

PROBLEM
-------
Two sensors (e.g. camera and LiDAR) publish at different rates with timestamps.
For each camera message, find the LiDAR message with the closest timestamp within
a tolerance — the core of message_filters ApproximateTime sync.

Implement an O((N+M)) two-pointer matcher over time-sorted streams.

Run:  python w8_time_sync.py
"""


def sync_nearest(stamps_a, stamps_b, max_dt):
    """
    stamps_a, stamps_b: ascending lists of timestamps (seconds).
    Returns list of (i, j, dt) pairing each a[i] to the nearest b[j] within max_dt.
    Two-pointer sweep: O(N + M).
    """
    pairs = []
    j = 0
    n, m = len(stamps_a), len(stamps_b)
    for i in range(n):
        # advance j while the next b is closer to a[i]
        while j + 1 < m and abs(stamps_b[j + 1] - stamps_a[i]) <= abs(stamps_b[j] - stamps_a[i]):
            j += 1
        dt = abs(stamps_b[j] - stamps_a[i])
        if dt <= max_dt:
            pairs.append((i, j, dt))
    return pairs


if __name__ == "__main__":
    # Camera at ~30 Hz, LiDAR at ~10 Hz (timestamps in seconds)
    cam = [0.00, 0.033, 0.066, 0.10, 0.133, 0.166, 0.20]
    lidar = [0.005, 0.105, 0.205]

    pairs = sync_nearest(cam, lidar, max_dt=0.02)
    for i, j, dt in pairs:
        print(f"cam[{i}] t={cam[i]:.3f}  ->  lidar[{j}] t={lidar[j]:.3f}  (dt={dt*1000:.1f} ms)")

    # cam[0]~0.0 -> lidar0 (5ms); cam[3]~0.10 -> lidar1 (5ms); cam[6]~0.20 -> lidar2
    matched_cam = {i for i, _, _ in pairs}
    assert {0, 3, 6}.issubset(matched_cam)
    assert all(dt <= 0.02 for _, _, dt in pairs)
    print("Time sync OK")
