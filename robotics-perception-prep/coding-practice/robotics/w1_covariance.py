"""
Week 1 — Covariance & Mahalanobis distance from scratch.

PROBLEM
-------
1. Compute the sample mean and covariance of an Nx D dataset WITHOUT np.cov.
2. Implement Mahalanobis distance d(x) = sqrt((x-mu)^T Σ^-1 (x-mu)).
3. Use it for simple outlier gating (a common trick in data association).

Run:  python w1_covariance.py
"""
import numpy as np


def mean_cov(X):
    """X: (N, D). Returns (mu (D,), Sigma (D, D)) using the unbiased estimator."""
    X = np.asarray(X, float)
    N = X.shape[0]
    mu = X.mean(axis=0)
    Xc = X - mu
    Sigma = (Xc.T @ Xc) / (N - 1)
    return mu, Sigma


def mahalanobis(x, mu, Sigma):
    d = np.asarray(x, float) - mu
    return float(np.sqrt(d @ np.linalg.inv(Sigma) @ d))


def gate(points, mu, Sigma, chi2_thresh=9.21):
    """Return boolean inlier mask. 9.21 ≈ chi-square 0.99 quantile for 2 DoF."""
    return np.array([mahalanobis(p, mu, Sigma) ** 2 < chi2_thresh for p in points])


if __name__ == "__main__":
    rng = np.random.default_rng(1)
    # Correlated 2D gaussian
    A = np.array([[1.0, 0.8], [0.0, 0.6]])
    data = rng.normal(size=(500, 2)) @ A.T + np.array([3.0, -1.0])

    mu, Sigma = mean_cov(data)
    print("mean:", np.round(mu, 3))
    print("cov:\n", np.round(Sigma, 3))
    print("np.cov check:\n", np.round(np.cov(data.T), 3))

    # A point along the correlation direction is "closer" than one across it,
    # even at equal Euclidean distance — that's the point of Mahalanobis.
    p_along = mu + np.array([0.8, 0.6])
    p_across = mu + np.array([0.6, -0.8])
    print("Mahalanobis along :", round(mahalanobis(p_along, mu, Sigma), 3))
    print("Mahalanobis across:", round(mahalanobis(p_across, mu, Sigma), 3))

    mask = gate(data, mu, Sigma)
    print(f"inliers: {mask.sum()}/{len(mask)}")
    assert np.allclose(Sigma, np.cov(data.T))
    print("OK")
