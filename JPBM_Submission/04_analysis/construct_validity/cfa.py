"""Minimal ML confirmatory factor analysis for congeneric measurement models.

Estimates loadings, error variances and factor covariances by minimising the
normal-theory ML discrepancy function, and reports chi-square, df, CFI, TLI,
RMSEA and SRMR together with reliability and discriminant-validity indices.
Factor variances are fixed at 1 so every loading is free and standardised.
"""
import numpy as np
from scipy.optimize import minimize
from scipy.stats import chi2 as chi2dist


def _implied(params, blocks, nfac, p):
    """Model-implied covariance matrix Sigma."""
    lam = np.zeros((p, nfac))
    k = 0
    for j, idx in enumerate(blocks):
        for i in idx:
            lam[i, j] = params[k]
            k += 1
    theta = np.diag(params[k:k + p])
    k += p
    phi = np.eye(nfac)
    for a in range(nfac):
        for b in range(a + 1, nfac):
            phi[a, b] = phi[b, a] = params[k]
            k += 1
    return lam @ phi @ lam.T + theta, lam, phi, np.diag(theta)


def _fml(params, S, blocks, nfac, p):
    sigma, *_ = _implied(params, blocks, nfac, p)
    try:
        sign, logdet = np.linalg.slogdet(sigma)
        if sign <= 0:
            return 1e6
        return logdet + np.trace(S @ np.linalg.inv(sigma)) - np.linalg.slogdet(S)[1] - p
    except np.linalg.LinAlgError:
        return 1e6


def fit_cfa(data, blocks, labels=None):
    """Fit a CFA. `blocks` is a list of lists of column indices, one per factor."""
    X = np.asarray(data, float)
    n, p = X.shape
    S = np.cov(X, rowvar=False, ddof=1)
    nfac = len(blocks)
    nload = sum(len(b) for b in blocks)
    ncov = nfac * (nfac - 1) // 2
    sd = np.sqrt(np.diag(S))
    x0 = np.concatenate([np.repeat(sd[np.concatenate(blocks)] * 0.7, 1),
                         np.diag(S) * 0.5,
                         np.full(ncov, 0.3)])
    bnds = [(None, None)] * nload + [(1e-6, None)] * p + [(-0.999, 0.999)] * ncov
    res = minimize(_fml, x0, args=(S, blocks, nfac, p), method="L-BFGS-B",
                   bounds=bnds, options={"maxiter": 20000, "ftol": 1e-14, "gtol": 1e-12})
    fmin = res.fun
    npar = nload + p + ncov
    df = p * (p + 1) // 2 - npar
    chi = (n - 1) * fmin
    sigma, lam, phi, theta = _implied(res.x, blocks, nfac, p)

    # null (independence) model
    Sd = np.diag(np.diag(S))
    fnull = np.linalg.slogdet(Sd)[1] + np.trace(S @ np.linalg.inv(Sd)) - np.linalg.slogdet(S)[1] - p
    chin, dfn = (n - 1) * fnull, p * (p - 1) // 2

    d_t, d_n = max(chi - df, 0), max(chin - dfn, 0)
    cfi = 1 - d_t / d_n if d_n > 0 else np.nan
    tli = ((chin / dfn) - (chi / df)) / ((chin / dfn) - 1) if df > 0 and dfn > 0 else np.nan
    rmsea = np.sqrt(max(chi - df, 0) / (df * (n - 1))) if df > 0 else np.nan
    # SRMR on the correlation metric
    Rs = S / np.outer(sd, sd)
    sdm = np.sqrt(np.diag(sigma))
    Rm = sigma / np.outer(sdm, sdm)
    iu = np.tril_indices(p)
    srmr = np.sqrt(np.mean((Rs[iu] - Rm[iu]) ** 2))

    # standardised loadings, AVE, composite reliability
    std_lam = lam / sdm[:, None]
    ave, cr = [], []
    for j, idx in enumerate(blocks):
        l = std_lam[idx, j]
        e = 1 - l ** 2
        ave.append(np.mean(l ** 2))
        cr.append(l.sum() ** 2 / (l.sum() ** 2 + e.sum()))
    return dict(chi2=chi, df=df, p=1 - chi2dist.cdf(chi, df) if df > 0 else np.nan,
                cfi=cfi, tli=tli, rmsea=rmsea, srmr=srmr, fmin=fmin, n=n,
                loadings=std_lam, phi=phi, theta=theta, ave=np.array(ave),
                cr=np.array(cr), converged=res.success, labels=labels)


def alpha(X):
    X = np.asarray(X, float)
    k = X.shape[1]
    v = np.var(X, axis=0, ddof=1).sum()
    t = np.var(X.sum(axis=1), ddof=1)
    return k / (k - 1) * (1 - v / t)


def htmt(X, blocks):
    """Heterotrait-monotrait ratio of correlations for two blocks."""
    R = np.corrcoef(np.asarray(X, float), rowvar=False)
    a, b = blocks
    hetero = np.mean([R[i, j] for i in a for j in b])
    def mono(idx):
        return np.mean([R[i, j] for ii, i in enumerate(idx) for j in idx[ii + 1:]])
    return hetero / np.sqrt(mono(a) * mono(b))


def param_se(params, S, blocks, nfac, p, n):
    """Asymptotic SEs from the numerical Hessian of the ML discrepancy function.

    acov(theta) = 2/(n-1) * H^{-1}, with H the Hessian of F_ML at the optimum.
    """
    k = len(params)
    h = np.maximum(np.abs(params) * 1e-4, 1e-6)
    H = np.zeros((k, k))
    for i in range(k):
        for j in range(i, k):
            ei = np.zeros(k); ei[i] = h[i]
            ej = np.zeros(k); ej[j] = h[j]
            fpp = _fml(params + ei + ej, S, blocks, nfac, p)
            fpm = _fml(params + ei - ej, S, blocks, nfac, p)
            fmp = _fml(params - ei + ej, S, blocks, nfac, p)
            fmm = _fml(params - ei - ej, S, blocks, nfac, p)
            H[i, j] = H[j, i] = (fpp - fpm - fmp + fmm) / (4 * h[i] * h[j])
    try:
        acov = 2.0 / (n - 1) * np.linalg.inv(H)
        return np.sqrt(np.abs(np.diag(acov)))
    except np.linalg.LinAlgError:
        return np.full(k, np.nan)
