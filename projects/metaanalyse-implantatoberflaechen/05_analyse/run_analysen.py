#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fuehrt alle vorab spezifizierten Metaanalysen aus und erzeugt Ergebnisse + Abbildungen."""
import os, sys, json, math
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path[:0] = [HERE, os.path.join(ROOT, "06_abbildungen"), os.path.join(ROOT, "04_extraktion")]
from metaanalyse import (smd_hedges, md, log_rr, freeman_tukey, ft_back, rma, subgroup,
                         leave_one_out, egger, begg, trim_and_fill, metareg)
from plots import forest, funnel, loo_plot
import datensatz as D

ABB = os.path.join(ROOT, "06_abbildungen")
ERG = {}

def ci_row(y, v, label, w=None, sub=None, log=False):
    se = math.sqrt(v); lo, hi = y - 1.96 * se, y + 1.96 * se
    if log: y, lo, hi = math.exp(y), math.exp(lo), math.exp(hi)
    return dict(label=label, y=y, ci_lo=lo, ci_hi=hi, w=w if w is not None else 1 / v, sub=sub)

def bericht(name, res, extra=None):
    ERG[name] = {k: (float(x) if isinstance(x, (int, float, np.floating)) else x)
                 for k, x in res.items() if k != "weights"}
    if extra: ERG[name].update(extra)
    print(f"\n=== {name} ===")
    print(f"  k={res['k']}  Effekt={res['est']:.4f}  95%-KI [{res['ci_lo']:.4f}; {res['ci_hi']:.4f}]  p={res['pval']:.4f}")
    print(f"  tau2={res['tau2']:.4f}  I2={res['I2']:.1f}%  Q({res['Q_df']})={res['Q']:.2f} (p={res['Q_p']:.4f})")
    if not math.isnan(res.get('pi_lo', float('nan'))):
        print(f"  95%-Vorhersageintervall [{res['pi_lo']:.4f}; {res['pi_hi']:.4f}]")

# ---------------------------------------------------------------- A1
rows_d = D.A1_BIC_KERAMIK_VS_TITAN
y, v = md([r["mt"] for r in rows_d], [r["sdt"] for r in rows_d], [r["nt"] for r in rows_d],
          [r["mk"] for r in rows_d], [r["sdk"] for r in rows_d], [r["nk"] for r in rows_d])
res = rma(y, v)
rows = [ci_row(y[i], v[i], f"{r['studie']} ({r['spezies']}, {int(r['zeit_w'])} W)", res["weights"][i])
        for i, r in enumerate(rows_d)]
bericht("A1_BIC_Keramik_vs_Titan", res)
forest(rows, res, "Mittelwertdifferenz des Knochen-Implantat-Kontakts (%)",
       "Abbildung 2: Knochen-Implantat-Kontakt – keramische vs. metallische Implantate (praeklinisch, in vivo)",
       os.path.join(ABB, "abb02_forest_A1_BIC_keramik_titan.png"),
       favours=("zugunsten Titan", "zugunsten Keramik"),
       extra_lines="Positive Werte = hoeherer BIC bei keramischen Implantaten. Random-Effects-Modell (REML), "
                   "Konfidenzintervall nach Hartung-Knapp-Sidik-Jonkman.")
funnel(y, v, res, "Mittelwertdifferenz BIC (%)",
       "Abbildung 3: Funnel-Plot – Analyse A1", os.path.join(ABB, "abb03_funnel_A1.png"))
ERG["A1_BIC_Keramik_vs_Titan"]["egger"] = egger(y, v)
ERG["A1_BIC_Keramik_vs_Titan"]["begg"] = begg(y, v)
tf = trim_and_fill(y, v)
ERG["A1_BIC_Keramik_vs_Titan"]["trim_fill"] = dict(k0=tf["k0"], seite=tf["seite"],
    est_adj=tf["adjustiert"]["est"], ci=[tf["adjustiert"]["ci_lo"], tf["adjustiert"]["ci_hi"]])
loo = leave_one_out(y, v, [r["studie"] for r in rows_d])
ERG["A1_BIC_Keramik_vs_Titan"]["leave_one_out"] = loo
loo_plot(loo, res, "Mittelwertdifferenz BIC (%)",
         "Abbildung 4: Leave-one-out-Sensitivitaetsanalyse – Analyse A1",
         os.path.join(ABB, "abb04_loo_A1.png"))
# Subgruppen: Einheilzeit
grp = np.array(["≤ 8 Wochen" if r["zeit_w"] <= 8 else "> 8 Wochen" for r in rows_d])
sg = subgroup(y, v, grp)
ERG["A1_BIC_Keramik_vs_Titan"]["subgruppe_zeit"] = {
    g: dict(k=r["k"], est=r["est"], ci=[r["ci_lo"], r["ci_hi"]], I2=r["I2"]) for g, r in sg["groups"].items()}
ERG["A1_BIC_Keramik_vs_Titan"]["subgruppe_zeit"]["Q_between"] = sg["Q_between"]
ERG["A1_BIC_Keramik_vs_Titan"]["subgruppe_zeit"]["p_between"] = sg["p_between"]
ERG["A1_BIC_Keramik_vs_Titan"]["subgruppe_zeit"]["p_between_re"] = sg["p_between_re"]
# Sensitivitaet: ohne imputierte/angenommene Werte
keep = [i for i, r in enumerate(rows_d) if not r.get("imputiert") and "SEM" not in (r.get("anmerkung") or "")]
res_s = rma(y[keep], v[keep])
ERG["A1_BIC_Keramik_vs_Titan"]["sens_ohne_imputation"] = dict(k=res_s["k"], est=res_s["est"],
    ci=[res_s["ci_lo"], res_s["ci_hi"]], I2=res_s["I2"], p=res_s["pval"])
res_dl = rma(y, v, method="DL", knha=False)
ERG["A1_BIC_Keramik_vs_Titan"]["sens_DL"] = dict(est=res_dl["est"], ci=[res_dl["ci_lo"], res_dl["ci_hi"]])
mr = metareg(y, v, np.array([r["zeit_w"] for r in rows_d]), names=["Einheilzeit_Wochen"])
ERG["A1_BIC_Keramik_vs_Titan"]["metaregression_zeit"] = dict(
    beta=list(mr["koeff"]), se=list(mr["se"]), p=list(mr["p"]), tau2=mr["tau2"])

# ---------------------------------------------------------------- B1
rows_d = D.B1_BIC_OFM_VS_MASCHINIERT
y, v = md([r["mt"] for r in rows_d], [r["sdt"] for r in rows_d], [r["nt"] for r in rows_d],
          [r["mk"] for r in rows_d], [r["sdk"] for r in rows_d], [r["nk"] for r in rows_d])
res = rma(y, v)
grp = np.array([r["strang"] for r in rows_d])
sg = subgroup(y, v, grp)
order = ["Tier", "Mensch"]
rows = []
for i, r in enumerate(rows_d):
    rows.append(ci_row(y[i], v[i], f"{r['studie']} ({r['spezies']}, {r['gruppe_t'][:34]})",
                       res["weights"][i], sub=r["strang"]))
bericht("B1_BIC_OFM_vs_maschiniert", res)
print("  Subgruppen:", {g: (round(r['est'], 2), r['k']) for g, r in sg["groups"].items()},
      f"Q_between(RE)={sg['Q_between_re']:.2f}, p={sg['p_between_re']:.4f} | "
      f"Q_between(FE)={sg['Q_between']:.2f}, p={sg['p_between']:.4f}")
forest(rows, res, "Mittelwertdifferenz des Knochen-Implantat-Kontakts (%)",
       "Abbildung 5: Knochen-Implantat-Kontakt – oberflaechenmodifizierte vs. maschinierte Implantate",
       os.path.join(ABB, "abb05_forest_B1_BIC_ofm.png"),
       subgroups={g: sg["groups"][g] for g in order if g in sg["groups"]},
       favours=("zugunsten maschiniert", "zugunsten modifiziert"),
       extra_lines="Positive Werte = hoeherer BIC nach Oberflaechenmodifikation. "
                   f"Subgruppenunterschied (Random-Effects): Q = {sg['Q_between_re']:.2f}, p = {sg['p_between_re']:.3f}.")
funnel(y, v, res, "Mittelwertdifferenz BIC (%)",
       "Abbildung 6: Funnel-Plot – Analyse B1", os.path.join(ABB, "abb06_funnel_B1.png"),
       filled=(trim_and_fill(y, v)["y_gefuellt"], trim_and_fill(y, v)["v_gefuellt"]))
tf = trim_and_fill(y, v)
ERG["B1_BIC_OFM_vs_maschiniert"].update(
    egger=egger(y, v), begg=begg(y, v),
    trim_fill=dict(k0=tf["k0"], seite=tf["seite"], est_adj=tf["adjustiert"]["est"],
                   ci=[tf["adjustiert"]["ci_lo"], tf["adjustiert"]["ci_hi"]]),
    subgruppe_strang={g: dict(k=r["k"], est=r["est"], ci=[r["ci_lo"], r["ci_hi"]], I2=r["I2"])
                      for g, r in sg["groups"].items()},
    Q_between=sg["Q_between"], p_between=sg["p_between"],
    Q_between_re=sg["Q_between_re"], p_between_re=sg["p_between_re"])
loo = leave_one_out(y, v, [r["studie"] for r in rows_d])
ERG["B1_BIC_OFM_vs_maschiniert"]["leave_one_out"] = loo
loo_plot(loo, res, "Mittelwertdifferenz BIC (%)",
         "Abbildung 7: Leave-one-out-Sensitivitaetsanalyse – Analyse B1",
         os.path.join(ABB, "abb07_loo_B1.png"))
# Subgruppe nach Art der Modifikation
grp2 = np.array([r["ofm_klasse"].split(" ")[0] for r in rows_d])
sg2 = subgroup(y, v, grp2)
ERG["B1_BIC_OFM_vs_maschiniert"]["subgruppe_modifikationsart"] = {
    g: dict(k=r["k"], est=r["est"], ci=[r["ci_lo"], r["ci_hi"]], I2=r["I2"]) for g, r in sg2["groups"].items()}
ERG["B1_BIC_OFM_vs_maschiniert"]["subgruppe_modifikationsart"]["p_between"] = sg2["p_between"]
ERG["B1_BIC_OFM_vs_maschiniert"]["subgruppe_modifikationsart"]["p_between_re"] = sg2["p_between_re"]
mr = metareg(y, v, np.array([r["zeit_w"] for r in rows_d]), names=["Einheilzeit_Wochen"])
ERG["B1_BIC_OFM_vs_maschiniert"]["metaregression_zeit"] = dict(
    beta=list(mr["koeff"]), se=list(mr["se"]), p=list(mr["p"]), tau2=mr["tau2"])
res_dl = rma(y, v, method="DL", knha=False)
ERG["B1_BIC_OFM_vs_maschiniert"]["sens_DL"] = dict(est=res_dl["est"], ci=[res_dl["ci_lo"], res_dl["ci_hi"]])

# ---------------------------------------------------------------- B2
rows_d = D.B2_BIOMECHANIK_OFM_VS_MASCHINIERT
g_, vg = smd_hedges([r["mt"] for r in rows_d], [r["sdt"] for r in rows_d], [r["nt"] for r in rows_d],
                    [r["mk"] for r in rows_d], [r["sdk"] for r in rows_d], [r["nk"] for r in rows_d])
res = rma(g_, vg)
rows = [ci_row(g_[i], vg[i], f"{r['studie']} ({r['spezies']}, {int(r['zeit_w'])} W)", res["weights"][i])
        for i, r in enumerate(rows_d)]
bericht("B2_Biomechanik_OFM_vs_maschiniert", res)
forest(rows, res, "Standardisierte Mittelwertdifferenz (Hedges' g)",
       "Abbildung 8: Biomechanische Verankerung – oberflaechenmodifizierte vs. maschinierte Implantate",
       os.path.join(ABB, "abb08_forest_B2_biomechanik.png"),
       favours=("zugunsten maschiniert", "zugunsten modifiziert"),
       extra_lines="Zielgroesse: Ausdrehmoment bzw. Ausdrueckkraft. Positive Werte = staerkere Verankerung "
                   "nach Oberflaechenmodifikation.")
funnel(g_, vg, res, "Hedges' g", "Abbildung 9: Funnel-Plot – Analyse B2",
       os.path.join(ABB, "abb09_funnel_B2.png"))
tf = trim_and_fill(g_, vg)
ERG["B2_Biomechanik_OFM_vs_maschiniert"].update(
    egger=egger(g_, vg), begg=begg(g_, vg),
    trim_fill=dict(k0=tf["k0"], seite=tf["seite"], est_adj=tf["adjustiert"]["est"],
                   ci=[tf["adjustiert"]["ci_lo"], tf["adjustiert"]["ci_hi"]]))
loo = leave_one_out(g_, vg, [r["studie"] for r in rows_d])
ERG["B2_Biomechanik_OFM_vs_maschiniert"]["leave_one_out"] = loo

# ---------------------------------------------------------------- C1
rows_d = [r for r in D.C1_KLIN_VERLUST if not (r["et"] == 0 and r["ek"] == 0)]
lrr, vr = log_rr([r["et"] for r in rows_d], [r["nt"] for r in rows_d],
                 [r["ek"] for r in rows_d], [r["nk"] for r in rows_d])
res = rma(lrr, vr)
rows = [ci_row(lrr[i], vr[i], f"{r['studie']} ({r['design']}, {r['nachbeob_mo']} Mon.)",
               res["weights"][i], log=True) for i, r in enumerate(rows_d)]
bericht("C1_klinischer_Implantatverlust_ZrO2_vs_Ti", res,
        extra=dict(RR=math.exp(res["est"]), RR_ci=[math.exp(res["ci_lo"]), math.exp(res["ci_hi"])]))
print(f"  RR = {math.exp(res['est']):.2f} [{math.exp(res['ci_lo']):.2f}; {math.exp(res['ci_hi']):.2f}]")
forest(rows, dict(res, est=math.exp(res["est"]), ci_lo=math.exp(res["ci_lo"]), ci_hi=math.exp(res["ci_hi"]),
                  pi_lo=math.exp(res["pi_lo"]), pi_hi=math.exp(res["pi_hi"])),
       "Risk Ratio des Implantatverlusts (log-Skala)",
       "Abbildung 10: Implantatverlust – Zirkonoxid- vs. Titanimplantate (klinisch)",
       os.path.join(ABB, "abb10_forest_C1_verlust.png"), effect="RR",
       favours=("zugunsten Zirkonoxid", "zugunsten Titan"),
       extra_lines="RR > 1 = hoeheres Verlustrisiko bei Zirkonoxidimplantaten. Nullzellen mit "
                   "Kontinuitaetskorrektur 0,5; Doppelnullstudien ausgeschlossen.")
loo = leave_one_out(lrr, vr, [r["studie"] for r in rows_d])
ERG["C1_klinischer_Implantatverlust_ZrO2_vs_Ti"]["leave_one_out"] = [
    dict(x, est=math.exp(x["est"]), ci_lo=math.exp(x["ci_lo"]), ci_hi=math.exp(x["ci_hi"])) for x in loo]
keep = [i for i, r in enumerate(rows_d) if not r.get("unsicher")]
res_s = rma(lrr[keep], vr[keep])
ERG["C1_klinischer_Implantatverlust_ZrO2_vs_Ti"]["sens_ohne_rekonstruierte"] = dict(
    k=res_s["k"], RR=math.exp(res_s["est"]), ci=[math.exp(res_s["ci_lo"]), math.exp(res_s["ci_hi"])], I2=res_s["I2"])

# ---------------------------------------------------------------- C2
rows_d = D.C2_KLIN_MBL
y, v = md([r["mt"] for r in rows_d], [r["sdt"] for r in rows_d], [r["nt"] for r in rows_d],
          [r["mk"] for r in rows_d], [r["sdk"] for r in rows_d], [r["nk"] for r in rows_d])
res = rma(y, v)
rows = [ci_row(y[i], v[i], f"{r['studie']} ({r['design']}, {r['nachbeob_mo']} Mon.)", res["weights"][i])
        for i, r in enumerate(rows_d)]
bericht("C2_marginaler_Knochenverlust_ZrO2_vs_Ti", res)
forest(rows, res, "Mittelwertdifferenz des marginalen Knochenverlusts (mm)",
       "Abbildung 11: Marginaler Knochenverlust – Zirkonoxid- vs. Titanimplantate",
       os.path.join(ABB, "abb11_forest_C2_mbl.png"),
       favours=("zugunsten Zirkonoxid", "zugunsten Titan"),
       extra_lines="Positive Werte = groesserer marginaler Knochenverlust um Zirkonoxidimplantate.")
loo = leave_one_out(y, v, [r["studie"] for r in rows_d])
ERG["C2_marginaler_Knochenverlust_ZrO2_vs_Ti"]["leave_one_out"] = loo
keep = [i for i, r in enumerate(rows_d) if not r.get("imputiert")]
res_s = rma(y[keep], v[keep])
ERG["C2_marginaler_Knochenverlust_ZrO2_vs_Ti"]["sens_ohne_imputation"] = dict(
    k=res_s["k"], est=res_s["est"], ci=[res_s["ci_lo"], res_s["ci_hi"]], I2=res_s["I2"])

# ---------------------------------------------------------------- C3
rows_d = [r for r in D.C3_KERAMIK_UEBERLEBEN if r["studie"] != "Kohal 2025a"]
t, vt = freeman_tukey([r["ereignisse"] for r in rows_d], [r["n"] for r in rows_d])
res = rma(t, vt)
nh = len(rows_d) / sum(1.0 / r["n"] for r in rows_d)
p_pool = ft_back(res["est"], nh)
p_lo, p_hi = ft_back(res["ci_lo"], nh), ft_back(res["ci_hi"], nh)
bericht("C3_Ueberleben_Keramikimplantate", res,
        extra=dict(anteil=p_pool, anteil_ci=[p_lo, p_hi], n_harmonisch=nh,
                   gesamt_implantate=int(sum(r["n"] for r in rows_d))))
print(f"  Gepoolte Ueberlebensrate = {p_pool*100:.1f} % [{p_lo*100:.1f}; {p_hi*100:.1f}]  "
      f"(N = {sum(r['n'] for r in rows_d)} Implantate)")
rows = []
for i, r in enumerate(rows_d):
    pi = r["ereignisse"] / r["n"]
    se = math.sqrt(max(pi * (1 - pi) / r["n"], 1e-6))
    rows.append(dict(label=f"{r['studie']} ({r['nachbeob_mo']} Mon., n={r['n']})", y=pi * 100,
                     ci_lo=max(0, (pi - 1.96 * se)) * 100, ci_hi=min(1, (pi + 1.96 * se)) * 100,
                     w=res["weights"][i]))
pooled_disp = dict(res, est=p_pool * 100, ci_lo=p_lo * 100, ci_hi=p_hi * 100,
                   pi_lo=ft_back(res["pi_lo"], nh) * 100, pi_hi=ft_back(res["pi_hi"], nh) * 100)
forest(rows, pooled_disp, "Ueberlebensrate (%)",
       "Abbildung 12: Gepoolte Ueberlebensrate keramischer Dentalimplantate",
       os.path.join(ABB, "abb12_forest_C3_ueberleben.png"), xlim=(40, 102),
       extra_lines="Freeman-Tukey-Doppelarcussinus-Transformation, Ruecktransformation nach Miller "
                   "mit harmonischem Mittel der Stichprobenumfaenge. Einarmige Poolung heterogener "
                   "Nachbeobachtungszeiten - nur deskriptiv zu interpretieren.")
mr = metareg(t, vt, np.array([r["nachbeob_mo"] for r in rows_d]), names=["Nachbeobachtung_Monate"])
ERG["C3_Ueberleben_Keramikimplantate"]["metaregression_nachbeobachtung"] = dict(
    beta=list(mr["koeff"]), se=list(mr["se"]), p=list(mr["p"]), tau2=mr["tau2"])
ERG["C3_Ueberleben_Keramikimplantate"]["egger"] = egger(t, vt)

json.dump(ERG, open(os.path.join(HERE, "ergebnisse.json"), "w"), indent=1,
          ensure_ascii=False, default=float)
print("\nAbbildungen:", sorted(f for f in os.listdir(ABB) if f.endswith(".png")))
