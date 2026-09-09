#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Metaanalyse-Kernbibliothek (reine Python/NumPy/SciPy-Implementierung).
Formeln validiert gegen metafor (Viechtbauer 2010, J Stat Softw 36:3) und
Cochrane Handbook v6.5, Kap. 6 und 10.

Enthaelt:
  - Effektmasse: MD, SMD (Hedges' g), RR, RD, logit-/Freeman-Tukey-Proportionen
  - Random-Effects-Modelle: DerSimonian-Laird und REML (Profile-Likelihood-Iteration)
  - Konfidenzintervalle: Wald und Hartung-Knapp-Sidik-Jonkman (HKSJ)
  - Heterogenitaet: Q, I^2, tau^2, H^2, Vorhersageintervall
  - Publikationsbias: Egger-Regressionstest, Begg-Rangkorrelation, Trim-and-Fill
  - Subgruppenanalyse (Q_between), Meta-Regression (gewichtete KQ, Knapp-Hartung)
  - Sensitivitaet: Leave-one-out
"""
import math
import numpy as np
from scipy import stats

# ---------------------------------------------------------------- Effektmasse
def smd_hedges(m1, sd1, n1, m2, sd2, n2):
    """Standardisierte Mittelwertdifferenz nach Hedges (g) inkl. Varianz.
    Gruppe 1 = Intervention/Test, Gruppe 2 = Kontrolle."""
    m1, sd1, n1, m2, sd2, n2 = map(np.asarray, (m1, sd1, n1, m2, sd2, n2))
    df = n1 + n2 - 2
    sp = np.sqrt(((n1 - 1) * sd1**2 + (n2 - 1) * sd2**2) / df)
    d = (m1 - m2) / sp
    J = 1 - 3.0 / (4 * df - 1)              # Korrektur fuer kleine Stichproben
    g = J * d
    vg = J**2 * (1.0 / n1 + 1.0 / n2 + d**2 / (2 * (n1 + n2)))
    return g, vg

def md(m1, sd1, n1, m2, sd2, n2):
    """Rohe Mittelwertdifferenz inkl. Varianz."""
    m1, sd1, n1, m2, sd2, n2 = map(np.asarray, (m1, sd1, n1, m2, sd2, n2))
    return m1 - m2, sd1**2 / n1 + sd2**2 / n2

def log_rr(e1, n1, e2, n2, cc=0.5):
    """log(Risk Ratio) inkl. Varianz; Kontinuitaetskorrektur cc bei Nullzellen."""
    e1, n1, e2, n2 = map(lambda x: np.asarray(x, dtype=float), (e1, n1, e2, n2))
    zero = (e1 == 0) | (e2 == 0)
    a, b, c, d = e1.copy(), n1.copy(), e2.copy(), n2.copy()
    a[zero] += cc; c[zero] += cc; b[zero] += 2 * cc; d[zero] += 2 * cc
    lrr = np.log((a / b) / (c / d))
    v = 1 / a - 1 / b + 1 / c - 1 / d
    return lrr, v

def freeman_tukey(x, n):
    """Freeman-Tukey-doppelte-Arcussinus-Transformation fuer Proportionen."""
    x, n = np.asarray(x, dtype=float), np.asarray(n, dtype=float)
    t = np.arcsin(np.sqrt(x / (n + 1))) + np.arcsin(np.sqrt((x + 1) / (n + 1)))
    v = 1.0 / (n + 0.5)
    return t, v

def ft_back(t, n_harm):
    """Ruecktransformation Freeman-Tukey (Miller 1978) mit harmonischem Mittel n."""
    if 1.0 / n_harm > math.sin(t / 2)**2 or math.sin(t / 2)**2 > 1 - 1.0 / n_harm:
        # Randbereich -> begrenzte Ruecktransformation
        return max(0.0, min(1.0, math.sin(t / 2)**2))
    return 0.5 * (1 - np.sign(np.cos(t)) * np.sqrt(
        1 - (np.sin(t) + (np.sin(t) - 1 / np.sin(t)) / n_harm)**2))

# ------------------------------------------------------- Random-Effects-Modell
def _tau2_dl(y, v):
    w = 1.0 / v
    mu = np.sum(w * y) / np.sum(w)
    Q = np.sum(w * (y - mu)**2)
    k = len(y)
    C = np.sum(w) - np.sum(w**2) / np.sum(w)
    return max(0.0, (Q - (k - 1)) / C) if C > 0 else 0.0, Q

def _tau2_reml(y, v, tol=1e-10, maxit=200):
    t2, _ = _tau2_dl(y, v)
    for _ in range(maxit):
        w = 1.0 / (v + t2)
        sw = np.sum(w)
        mu = np.sum(w * y) / sw
        num = np.sum(w**2 * ((y - mu)**2 - v)) + np.sum(w**2) / sw
        den = np.sum(w**2)
        new = max(0.0, num / den) if den > 0 else 0.0
        if abs(new - t2) < tol:
            t2 = new
            break
        t2 = new
    return t2

def rma(y, v, method="REML", knha=True, level=0.95):
    """Random-Effects-Metaanalyse (Inverse-Varianz). Gibt Dictionary zurueck."""
    y = np.asarray(y, dtype=float); v = np.asarray(v, dtype=float)
    k = len(y)
    if k == 0:
        raise ValueError("keine Studien")
    t2_dl, Q = _tau2_dl(y, v)
    tau2 = _tau2_reml(y, v) if method.upper() == "REML" else t2_dl
    w = 1.0 / (v + tau2)
    mu = np.sum(w * y) / np.sum(w)
    se = math.sqrt(1.0 / np.sum(w))
    df = k - 1
    if knha and k > 1:
        # Hartung-Knapp-Sidik-Jonkman-Varianzanpassung
        s2 = np.sum(w * (y - mu)**2) / df
        se = math.sqrt(max(s2, 1e-12) / np.sum(w))
        crit = stats.t.ppf(1 - (1 - level) / 2, df)
        pval = 2 * (1 - stats.t.cdf(abs(mu / se), df))
    else:
        crit = stats.norm.ppf(1 - (1 - level) / 2)
        pval = 2 * (1 - stats.norm.cdf(abs(mu / se)))
    ci_lo, ci_hi = mu - crit * se, mu + crit * se
    # Heterogenitaet
    wf = 1.0 / v
    C = np.sum(wf) - np.sum(wf**2) / np.sum(wf)
    Q_p = 1 - stats.chi2.cdf(Q, df) if df > 0 else float("nan")
    I2 = max(0.0, (Q - df) / Q * 100) if Q > 0 and df > 0 else 0.0
    H2 = Q / df if df > 0 else float("nan")
    # Vorhersageintervall (Higgins/Thompson/Spiegelhalter)
    if k >= 3:
        tcrit = stats.t.ppf(1 - (1 - level) / 2, k - 2)
        pi_lo = mu - tcrit * math.sqrt(tau2 + se**2)
        pi_hi = mu + tcrit * math.sqrt(tau2 + se**2)
    else:
        pi_lo = pi_hi = float("nan")
    return dict(k=k, est=mu, se=se, ci_lo=ci_lo, ci_hi=ci_hi, pval=pval,
                tau2=tau2, tau=math.sqrt(tau2), Q=Q, Q_df=df, Q_p=Q_p, I2=I2, H2=H2,
                pi_lo=pi_lo, pi_hi=pi_hi, weights=w / np.sum(w) * 100,
                method=method, knha=knha)

# ------------------------------------------------------------- Subgruppen etc.
def subgroup(y, v, groups, method="REML", knha=True):
    y = np.asarray(y, float); v = np.asarray(v, float); groups = np.asarray(groups)
    out = {}
    Qw = 0.0; dfw = 0
    ests, ses = [], []
    for g in sorted(set(groups)):
        idx = groups == g
        if idx.sum() == 0: continue
        r = rma(y[idx], v[idx], method, knha and idx.sum() > 1)
        out[g] = r
        wf = 1.0 / v[idx]; mug = np.sum(wf * y[idx]) / np.sum(wf)
        Qw += np.sum(wf * (y[idx] - mug)**2); dfw += idx.sum() - 1
        ests.append(r["est"]); ses.append(r["se"])
    tot = rma(y, v, method, knha)
    Qb = max(0.0, tot["Q"] - Qw); dfb = len(out) - 1
    p_b = 1 - stats.chi2.cdf(Qb, dfb) if dfb > 0 else float("nan")
    # Random-Effects-Subgruppentest (Mixed-Effects-Modell, Cochrane Handbook 10.11.3.1):
    # Wald-Test ueber die Random-Effects-Subgruppenschaetzer
    e = np.array(ests); s_ = np.array(ses)
    wg = 1.0 / s_**2
    mu_g = np.sum(wg * e) / np.sum(wg)
    Qb_re = float(np.sum(wg * (e - mu_g)**2))
    p_b_re = 1 - stats.chi2.cdf(Qb_re, dfb) if dfb > 0 else float("nan")
    return dict(groups=out, gesamt=tot, Q_between=Qb, df_between=dfb, p_between=p_b,
                Q_between_re=Qb_re, p_between_re=p_b_re)

def leave_one_out(y, v, labels, method="REML", knha=True):
    y = np.asarray(y, float); v = np.asarray(v, float)
    res = []
    for i in range(len(y)):
        m = np.ones(len(y), bool); m[i] = False
        if m.sum() < 2: continue
        r = rma(y[m], v[m], method, knha)
        res.append(dict(weggelassen=labels[i], est=r["est"], ci_lo=r["ci_lo"],
                        ci_hi=r["ci_hi"], I2=r["I2"], tau2=r["tau2"]))
    return res

# --------------------------------------------------------- Publikationsbias
def egger(y, v):
    """Egger-Regressionstest (Praezision vs. standardisierter Effekt)."""
    y = np.asarray(y, float); v = np.asarray(v, float)
    se = np.sqrt(v); snd = y / se; prec = 1.0 / se
    X = np.column_stack([np.ones(len(y)), prec])
    beta, *_ = np.linalg.lstsq(X, snd, rcond=None)
    resid = snd - X @ beta
    dof = len(y) - 2
    s2 = np.sum(resid**2) / dof
    cov = s2 * np.linalg.inv(X.T @ X)
    t = beta[0] / math.sqrt(cov[0, 0])
    p = 2 * (1 - stats.t.cdf(abs(t), dof))
    return dict(intercept=beta[0], se=math.sqrt(cov[0, 0]), t=t, df=dof, p=p, slope=beta[1])

def begg(y, v):
    """Begg-Mazumdar-Rangkorrelation (Kendall's tau) zwischen Effekt und Varianz."""
    y = np.asarray(y, float); v = np.asarray(v, float)
    fixed_mu = np.sum(y / v) / np.sum(1 / v)
    vs = v - 1.0 / np.sum(1 / v)
    ys = (y - fixed_mu) / np.sqrt(np.maximum(vs, 1e-12))
    tau, p = stats.kendalltau(ys, v)
    return dict(tau=tau, p=p)

def trim_and_fill(y, v, side=None, method="REML"):
    """Duval-Tweedie Trim-and-Fill (L0-Schaetzer)."""
    y = np.asarray(y, float); v = np.asarray(v, float)
    base = rma(y, v, method, knha=False)
    if side is None:
        eg = egger(y, v); side = "left" if eg["slope"] < base["est"] else "right"
    sgn = 1.0 if side == "left" else -1.0
    yy, vv = y.copy(), v.copy()
    k0_prev, k0 = -1, 0
    for _ in range(50):
        r = rma(yy, vv, method, knha=False)
        c = sgn * (yy - r["est"])
        order = np.argsort(np.abs(c))
        ranks = np.empty(len(c)); ranks[order] = np.arange(1, len(c) + 1)
        Tn = np.sum(ranks[c > 0])
        n = len(c)
        k0_new = max(0, int(round((4 * Tn - n * (n + 1)) / (2 * n - 1))))
        if k0_new == k0_prev: break
        k0_prev = k0; k0 = k0_new
        idx = np.argsort(sgn * (y - r["est"]))[::-1][:k0]
        yy = np.concatenate([y, 2 * r["est"] - y[idx]])
        vv = np.concatenate([v, v[idx]])
    filled = rma(yy, vv, method, knha=False)
    return dict(k0=k0, seite=side, original=base, adjustiert=filled,
                y_gefuellt=yy, v_gefuellt=vv, n_original=len(y))

# ------------------------------------------------------------- Meta-Regression
def metareg(y, v, X, method="REML", knha=True, names=None):
    y = np.asarray(y, float); v = np.asarray(v, float)
    X = np.asarray(X, float)
    if X.ndim == 1: X = X[:, None]
    X = np.column_stack([np.ones(len(y)), X])
    t2 = _tau2_reml(y, v) if method.upper() == "REML" else _tau2_dl(y, v)[0]
    # iterativ tau^2 im Regressionsmodell
    for _ in range(100):
        W = np.diag(1.0 / (v + t2))
        XtWX = X.T @ W @ X
        beta = np.linalg.solve(XtWX, X.T @ W @ y)
        resid = y - X @ beta
        P = W - W @ X @ np.linalg.solve(XtWX, X.T @ W)
        num = resid @ W @ W @ resid - np.trace(P @ np.diag(v))
        den = np.trace(P @ P) if method.upper() == "REML" else np.trace(W @ W)
        new = max(0.0, t2 + num / den) if den != 0 else t2
        if abs(new - t2) < 1e-10: t2 = new; break
        t2 = new
    W = np.diag(1.0 / (v + t2))
    XtWX = X.T @ W @ X
    beta = np.linalg.solve(XtWX, X.T @ W @ y)
    cov = np.linalg.inv(XtWX)
    dfr = len(y) - X.shape[1]
    if knha and dfr > 0:
        resid = y - X @ beta
        s2 = (resid @ W @ resid) / dfr
        cov = cov * s2
    se = np.sqrt(np.diag(cov))
    tv = beta / se
    p = 2 * (1 - stats.t.cdf(np.abs(tv), max(dfr, 1)))
    nm = names or ([f"b{i}" for i in range(X.shape[1] - 1)])
    return dict(koeff=beta, se=se, t=tv, p=p, tau2=t2, df=dfr,
                namen=["Intercept"] + list(nm))
