#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Abbildungen: Forest-Plot, Funnel-Plot, Leave-one-out, RoB-Ampel, PRISMA-Fluss."""
import os, math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 9,
    "axes.linewidth": 0.8, "savefig.dpi": 300, "figure.dpi": 110,
    "axes.spines.top": False, "axes.spines.right": False,
})
C_PT   = "#1f4e79"
C_DIA  = "#8b1a1a"
C_GREY = "#666666"

def forest(rows, pooled, xlabel, title, outfile, effect="MD", subgroups=None,
           favours=None, xlim=None, extra_lines=None):
    log = effect == "RR"
    n = len(rows)
    nsub = len(subgroups) if subgroups else 0
    h = 1.15 + 0.30 * n + 0.60 * nsub + 1.0
    fig, ax = plt.subplots(figsize=(9.8, h))
    ypos, labels = [], []
    y = 0.0
    order = []
    if subgroups:
        for g, res in subgroups.items():
            y -= 1.0
            order.append(("head", g, res, y))
            for r in [x for x in rows if x.get("sub") == g]:
                y -= 1.0; order.append(("row", r, None, y))
            y -= 0.8
            order.append(("subsum", g, res, y))
            y -= 0.4
    else:
        for r in rows:
            y -= 1.0; order.append(("row", r, None, y))
    y -= 1.2
    order.append(("total", None, pooled, y))
    ymin = y - 1.25

    def tx(v): return math.log(v) if log else v
    allv = [tx(r["ci_lo"]) for r in rows] + [tx(r["ci_hi"]) for r in rows] + \
           [tx(pooled["ci_lo"]), tx(pooled["ci_hi"])]
    if not math.isnan(pooled.get("pi_lo", float("nan"))):
        allv += [tx(pooled["pi_lo"]), tx(pooled["pi_hi"])]
    lo, hi = min(allv), max(allv)
    pad = 0.15 * (hi - lo + 1e-9)
    if xlim: lo, hi = tx(xlim[0]), tx(xlim[1])
    else: lo, hi = lo - pad, hi + pad

    maxw = max([r.get("w", 1) for r in rows]) or 1
    for kind, a, b, yy in order:
        if kind == "row":
            r = a
            lo_, hi_, e = tx(r["ci_lo"]), tx(r["ci_hi"]), tx(r["y"])
            ax.plot([max(lo_, lo), min(hi_, hi)], [yy, yy], color=C_GREY, lw=1.0, zorder=2)
            for xx in (lo_, hi_):
                if lo <= xx <= hi:
                    ax.plot([xx, xx], [yy - 0.15, yy + 0.15], color=C_GREY, lw=1.0, zorder=2)
            s = 14 + 130 * (r.get("w", 1) / maxw)
            ax.scatter([e], [yy], s=s, marker="s", color=C_PT, zorder=3)
            ypos.append(yy); labels.append(r["label"])
        elif kind == "head":
            ax.text(lo, yy, f"{a}", fontsize=9, fontweight="bold", va="center")
        elif kind in ("subsum", "total"):
            res = b
            e, l_, h_ = tx(res["est"]), tx(res["ci_lo"]), tx(res["ci_hi"])
            ax.add_patch(plt.Polygon([[l_, yy], [e, yy + 0.30], [h_, yy], [e, yy - 0.30]],
                                     closed=True, color=C_DIA, zorder=4))
            nm = ("Gesamteffekt (Random-Effects, REML/HKSJ)" if kind == "total"
                  else f"Subtotal: {a}  (k = {res['k']}, I² = {res['I2']:.0f} %)")
            ypos.append(yy); labels.append(nm)
            if kind == "total" and not math.isnan(res.get("pi_lo", float("nan"))):
                ax.plot([max(tx(res["pi_lo"]), lo), min(tx(res["pi_hi"]), hi)],
                        [yy - 0.55, yy - 0.55], color=C_DIA, lw=1.7, ls=(0, (4, 2)), zorder=3)
                ax.text(min(tx(res["pi_hi"]), hi), yy - 0.55, "  95 %-Vorhersageintervall",
                        fontsize=7.2, va="center", color=C_DIA)
    ax.axvline(0.0, color="black", lw=0.8, zorder=1)
    ax.set_ylim(ymin, 0.4)
    ax.set_yticks(ypos); ax.set_yticklabels(labels, fontsize=8)
    ax.set_xlim(lo, hi)
    if log:
        cand = [0.02,0.05,0.1,0.2,0.33,0.5,0.75,1,1.5,2,3,5,10,20,50]
        tk = [c for c in cand if lo <= math.log(c) <= hi]
        ax.set_xticks([math.log(c) for c in tk]); ax.set_xticklabels([str(c) for c in tk])
    ax.set_xlabel(xlabel, fontsize=9)
    ax.set_title(title, fontsize=10.5, fontweight="bold", loc="left", pad=15)
    ax.spines["left"].set_visible(False); ax.tick_params(axis="y", length=0)
    if favours:
        ax.annotate("◀ " + favours[0], xy=(0.02, -0.075), xycoords="axes fraction",
                    fontsize=7.8, color=C_GREY)
        ax.annotate(favours[1] + " ▶", xy=(0.98, -0.075), xycoords="axes fraction",
                    fontsize=7.8, color=C_GREY, ha="right")
    sub = (f"k = {pooled['k']}   |   tau² = {pooled['tau2']:.4f}   |   "
           f"I² = {pooled['I2']:.1f} %   |   Q({pooled['Q_df']}) = {pooled['Q']:.2f}, "
           f"p = {pooled['Q_p']:.3f}")
    ax.annotate(sub, xy=(0, 1.012), xycoords="axes fraction", fontsize=7.8, color=C_GREY)
    if extra_lines:
        ax.annotate(extra_lines, xy=(0, -0.13), xycoords="axes fraction", fontsize=7.3,
                    color=C_GREY, va="top")
    fig.tight_layout()
    fig.savefig(outfile, bbox_inches="tight"); plt.close(fig)
    return outfile

def funnel(y, v, pooled, xlabel, title, outfile, filled=None):
    y = np.asarray(y, float); se = np.sqrt(np.asarray(v, float))
    fig, ax = plt.subplots(figsize=(6.1, 5.2))
    est = pooled["est"]; semax = se.max() * 1.15
    for z, al in zip([1.96, 2.58], [0.15, 0.07]):
        ax.fill([est - z * semax, est, est + z * semax], [semax, 0, semax],
                color=C_PT, alpha=al, lw=0)
    ax.axvline(est, color=C_DIA, lw=1.1, ls="--", label="gepoolter Effekt")
    ax.scatter(y, se, s=28, facecolor="white", edgecolor=C_PT, lw=1.1, zorder=3,
               label="Studien")
    if filled is not None and len(filled[0]) > len(y):
        fy, fv = filled
        ax.scatter(fy[len(y):], np.sqrt(fv[len(y):]), s=28, marker="o",
                   facecolor=C_DIA, edgecolor=C_DIA, alpha=.55, zorder=3,
                   label="imputiert (Trim-and-Fill)")
    ax.invert_yaxis()
    ax.set_xlabel(xlabel); ax.set_ylabel("Standardfehler")
    ax.set_title(title, fontsize=10.5, fontweight="bold", loc="left")
    ax.legend(frameon=False, fontsize=7.8, loc="lower left")
    fig.tight_layout(); fig.savefig(outfile, bbox_inches="tight"); plt.close(fig)
    return outfile

def loo_plot(loo, gesamt, xlabel, title, outfile):
    fig, ax = plt.subplots(figsize=(7.8, 0.32 * len(loo) + 1.9))
    ys = np.arange(len(loo))[::-1]
    ax.axvspan(gesamt["ci_lo"], gesamt["ci_hi"], color=C_PT, alpha=.10)
    ax.axvline(gesamt["est"], color=C_DIA, lw=1.0, ls="--")
    for i, r in zip(ys, loo):
        ax.plot([r["ci_lo"], r["ci_hi"]], [i, i], color=C_GREY, lw=1.0)
        ax.scatter([r["est"]], [i], s=22, color=C_PT, zorder=3)
    ax.set_yticks(ys); ax.set_yticklabels([r["weggelassen"] for r in loo], fontsize=7.6)
    ax.set_xlabel(xlabel); ax.set_title(title, fontsize=10.5, fontweight="bold", loc="left")
    ax.spines["left"].set_visible(False); ax.tick_params(axis="y", length=0)
    fig.tight_layout(); fig.savefig(outfile, bbox_inches="tight"); plt.close(fig)
    return outfile

ROB_COL = {"niedrig": "#2e7d32", "unklar": "#f9a825", "hoch": "#c62828",
           "einige Bedenken": "#f9a825", "kritisch": "#7f0000", "n. z.": "#cfcfcf"}
def rob_traffic(studies, domains, matrix, title, outfile, legend_note=None):
    fig, ax = plt.subplots(figsize=(2.2 + 0.62 * len(domains), 1.7 + 0.30 * len(studies)))
    for i, st in enumerate(studies):
        for j, d in enumerate(domains):
            v = matrix[i][j]
            ax.add_patch(plt.Circle((j, len(studies) - 1 - i), 0.33,
                                    color=ROB_COL.get(v, "#cfcfcf"), zorder=2))
            sym = {"niedrig": "+", "hoch": "–", "kritisch": "x"}.get(v, "?")
            ax.text(j, len(studies) - 1 - i, sym, ha="center", va="center",
                    color="white", fontsize=8, fontweight="bold", zorder=3)
    ax.set_xlim(-0.6, len(domains) - 0.4); ax.set_ylim(-0.7, len(studies) - 0.3)
    ax.set_aspect("equal")
    ax.set_xticks(range(len(domains)))
    ax.set_xticklabels(domains, rotation=45, ha="left", fontsize=7.2)
    ax.xaxis.set_ticks_position("top")
    ax.set_yticks(range(len(studies)))
    ax.set_yticklabels(studies[::-1], fontsize=7.4)
    for s in ax.spines.values(): s.set_visible(False)
    ax.tick_params(length=0)
    ax.set_title(title, fontsize=10.5, fontweight="bold", loc="left", pad=70)
    if legend_note:
        ax.annotate(legend_note, xy=(0, -0.03), xycoords="axes fraction",
                    fontsize=7.2, va="top", color=C_GREY)
    fig.tight_layout(); fig.savefig(outfile, bbox_inches="tight"); plt.close(fig)
    return outfile

def prisma_flow(d, outfile):
    fig, ax = plt.subplots(figsize=(9.4, 10.6)); ax.axis("off")
    ax.set_xlim(0, 10); ax.set_ylim(0, 12)
    def box(x, y, w, h, txt, fc="#eef3f8", ec=C_PT, fs=8.2, bold=False):
        ax.add_patch(Rectangle((x, y), w, h, fc=fc, ec=ec, lw=1.0, zorder=2))
        ax.text(x + w / 2, y + h / 2, txt, ha="center", va="center", fontsize=fs,
                zorder=3, fontweight="bold" if bold else "normal", linespacing=1.5)
    def arrow(x1, y1, x2, y2):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                     mutation_scale=11, lw=1.0, color=C_PT, zorder=1))
    for y0, y1, lab in [(9.6, 11.85, "Identifikation"), (5.3, 9.45, "Screening"),
                        (0.5, 5.15, "Eingeschlossen")]:
        ax.add_patch(Rectangle((0.05, y0), 0.62, y1 - y0, fc="#1f4e79", ec="none", alpha=.86))
        ax.text(0.36, (y0 + y1) / 2, lab, rotation=90, ha="center", va="center",
                color="white", fontsize=9.4, fontweight="bold")
    box(1.0, 10.6, 4.2, 1.15,
        "Datensätze aus Datenbanksuche\nPubMed/MEDLINE (n = %d)" % d['db_main'], bold=True)
    box(5.7, 10.6, 3.9, 1.15,
        "Datensätze aus ergänzenden\nzielgerichteten Suchen (n = %d)" % d['db_supp'])
    arrow(7.65, 10.6, 7.65, 10.25); arrow(7.65, 10.25, 3.15, 10.25)
    arrow(3.1, 10.6, 3.1, 10.02)
    box(1.0, 9.05, 4.2, 0.95, "Datensätze nach Dublettenentfernung\n(n = %d)" % d['unique'], bold=True)
    box(5.7, 9.05, 3.9, 0.95, "entfernte Dubletten\n(n = %d)" % d['dupes'], fc="#f6f6f6", ec=C_GREY)
    arrow(5.2, 9.52, 5.68, 9.52)
    arrow(3.1, 9.05, 3.1, 8.4)
    box(1.0, 7.4, 4.2, 1.0, "Datensätze im regelbasierten\nVorscreening (Stufe 1) (n = %d)" % d['unique'])
    ex1 = "\n".join(["%s: %d" % (k, v) for k, v in d["ex_stage1"].items()])
    box(5.7, 6.35, 3.9, 2.05, "ausgeschlossen (n = %d)\n%s" % (d['ex1_total'], ex1),
        fc="#f6f6f6", ec=C_GREY, fs=6.9)
    arrow(5.2, 7.9, 5.68, 7.9)
    arrow(3.1, 7.4, 3.1, 6.75)
    box(1.0, 5.8, 4.2, 0.95, "Titel-/Abstract-Screening\n(Stufe 2) (n = %d)" % d["stage2"])
    box(5.7, 4.95, 3.9, 1.3, "ausgeschlossen (n = %d)\n%s" % (d['ex2_total'], d['ex2_txt']),
        fc="#f6f6f6", ec=C_GREY, fs=6.9)
    arrow(5.2, 6.27, 5.68, 6.27)
    arrow(3.1, 5.8, 3.1, 5.0)
    box(1.0, 4.05, 4.2, 0.95, "Berichte im Detail auf Eignung\ngeprüft (Stufe 3) (n = %d)" % d['stage3'])
    box(5.7, 3.1, 3.9, 1.45, "ausgeschlossen (n = %d)\n%s" % (d['ex3_total'], d['ex3_txt']),
        fc="#f6f6f6", ec=C_GREY, fs=6.9)
    arrow(5.2, 4.52, 5.68, 4.52)
    arrow(3.1, 4.05, 3.1, 3.35)
    box(1.0, 2.4, 4.2, 0.95,
        "in qualitative Synthese\neingeschlossene Studien (n = %d)" % d['incl_qual'], bold=True)
    arrow(3.1, 2.4, 3.1, 1.75)
    box(1.0, 0.6, 8.6, 1.15,
        "in quantitative Synthese (Metaanalysen) eingeschlossene Studien (n = %d)\n%s"
        % (d['incl_quant'], d["quant_txt"]), fc="#dce9f5", bold=True, fs=8.0)
    ax.set_title("Abbildung 1: PRISMA-2020-Flussdiagramm der Studienselektion",
                 fontsize=11, fontweight="bold", loc="left", y=0.99)
    fig.savefig(outfile, bbox_inches="tight"); plt.close(fig)
    return outfile
