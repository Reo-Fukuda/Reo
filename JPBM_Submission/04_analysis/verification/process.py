"""Minimal re-implementation of PROCESS Models 4, 6 and 7 (Hayes, 2022)."""
import numpy as np

def ols(y, cols):
    X = np.column_stack([np.ones(len(y))] + [np.asarray(c, float) for c in cols])
    y = np.asarray(y, float)
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    res = y - X @ b
    n, k = X.shape
    s2 = res @ res / (n - k)
    se = np.sqrt(np.diag(s2 * np.linalg.inv(X.T @ X)))
    ss_t = ((y - y.mean()) ** 2).sum()
    return dict(b=b, se=se, df=n - k, r2=1 - res @ res / ss_t, resid=res, k=k, n=n)

def model4(X, M, Y, B=5000, seed=20260828):
    """X -> M -> Y simple mediation."""
    a = ols(M, [X]); b_ = ols(Y, [X, M]); c = ols(Y, [X])
    rng = np.random.default_rng(seed); n = len(X); ind = []
    Xa, Ma, Ya = map(lambda v: np.asarray(v, float), (X, M, Y))
    for _ in range(B):
        i = rng.integers(0, n, n)
        ind.append(ols(Ma[i], [Xa[i]])['b'][1] * ols(Ya[i], [Xa[i], Ma[i]])['b'][2])
    ind = np.array(ind)
    return dict(a=a, b=b_, c=c, indirect=a['b'][1] * b_['b'][2],
                boot_se=ind.std(ddof=1), ci=np.percentile(ind, [2.5, 97.5]))

def model7(X, W, M, Y, wvals, B=5000, seed=20260828):
    """W moderates the X->M path; M -> Y."""
    Xa, Wa = np.asarray(X, float), np.asarray(W, float)
    Ma, Ya = np.asarray(M, float), np.asarray(Y, float)
    am = ols(Ma, [Xa, Wa, Xa * Wa]); bm = ols(Ya, [Xa, Ma])
    a1, a3, bpath = am['b'][1], am['b'][3], bm['b'][2]
    red = ols(Ma, [Xa, Wa])
    dR2 = am['r2'] - red['r2']
    F = dR2 / (1 - am['r2']) * am['df']
    rng = np.random.default_rng(seed); n = len(Xa)
    cond = {w: [] for w in wvals}; idx = []
    for _ in range(B):
        i = rng.integers(0, n, n)
        A = ols(Ma[i], [Xa[i], Wa[i], Xa[i] * Wa[i]])['b']
        bb = ols(Ya[i], [Xa[i], Ma[i]])['b'][2]
        for w in wvals: cond[w].append((A[1] + A[3] * w) * bb)
        idx.append(A[3] * bb)
    idx = np.array(idx)
    out = dict(am=am, bm=bm, dR2=dR2, F=F, dfF=(1, am['df']),
               index=a3 * bpath, index_se=idx.std(ddof=1),
               index_ci=np.percentile(idx, [2.5, 97.5]), cond={})
    for w in wvals:
        c = np.array(cond[w])
        # simple slope of X on M at W=w, with SE from the covariance matrix
        V = am['se'] ** 2
        out['cond'][w] = dict(slope=a1 + a3 * w, effect=(a1 + a3 * w) * bpath,
                              se=c.std(ddof=1), ci=np.percentile(c, [2.5, 97.5]))
    return out

def simple_slope(X, W, M, w):
    """Slope of X on M at W = w, with correct SE from the parameter covariance."""
    Xa, Wa, Ma = (np.asarray(v, float) for v in (X, W, M))
    D = np.column_stack([np.ones(len(Xa)), Xa, Wa, Xa * Wa])
    b, *_ = np.linalg.lstsq(D, Ma, rcond=None)
    res = Ma - D @ b; n, k = D.shape
    V = (res @ res / (n - k)) * np.linalg.inv(D.T @ D)
    est = b[1] + b[3] * w
    se = np.sqrt(V[1, 1] + w ** 2 * V[3, 3] + 2 * w * V[1, 3])
    return est, se, n - k
