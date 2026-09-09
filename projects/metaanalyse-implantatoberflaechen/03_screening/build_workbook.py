#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Erzeugt die Excel-Arbeitsmappe mit Screening-Sheet, Extraktion, RoB und Ergebnissen."""
import csv, json, os, sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "04_extraktion"))
import datensatz as D

KOPF = PatternFill("solid", fgColor="1F4E79")
KOPFF = Font(color="FFFFFF", bold=True, size=10)
GRUEN = PatternFill("solid", fgColor="C6E0B4")
GELB = PatternFill("solid", fgColor="FFE699")
ROT = PatternFill("solid", fgColor="F8CBAD")
GRAU = PatternFill("solid", fgColor="EDEDED")
BOX = Border(*[Side("thin", color="BFBFBF")] * 4)

def blatt(wb, name, kopf, zeilen, breiten=None, freeze="A2", tabelle=True):
    ws = wb.create_sheet(name[:31])
    ws.append(kopf)
    for c in ws[1]:
        c.fill = KOPF; c.font = KOPFF; c.alignment = Alignment(vertical="center", wrap_text=True)
    ws.row_dimensions[1].height = 30
    for z in zeilen: ws.append(z)
    for i, b in enumerate(breiten or [18] * len(kopf), start=1):
        ws.column_dimensions[get_column_letter(i)].width = b
    ws.freeze_panes = freeze
    if tabelle and len(zeilen) > 0:
        ref = f"A1:{get_column_letter(len(kopf))}{len(zeilen)+1}"
        t = Table(displayName=name.replace(" ", "_").replace("-", "_")[:30] + "_T", ref=ref)
        t.tableStyleInfo = TableStyleInfo(name="TableStyleLight1", showRowStripes=True)
        try: ws.add_table(t)
        except Exception: pass
    return ws

wb = Workbook(); wb.remove(wb.active)

# --- Deckblatt ---
ws = wb.create_sheet("Übersicht")
inhalt = [
 ("Metaanalyse experimenteller und klinischer Ergebnisse bei keramischen und metallischen Implantaten nach Oberflächenmodifikationen", 14, True),
 ("Arbeitsmappe zur systematischen Übersichtsarbeit — Stand 09.09.2026", 11, False), ("", 11, False),
 ("Blatt", 11, True),
 ("1  Screening-Sheet — alle 5 168 Datensätze mit Entscheidung je Selektionsstufe", 10, False),
 ("2  Eingeschlossene Studien — 103 Studien mit Zuordnung zu den Analysen", 10, False),
 ("3  Extraktion A1 — Knochen-Implantat-Kontakt: Keramik vs. Titan (präklinisch)", 10, False),
 ("4  Extraktion B1 — Knochen-Implantat-Kontakt: Oberflächenmodifikation vs. maschiniert", 10, False),
 ("5  Extraktion B2 — biomechanische Verankerung", 10, False),
 ("6  Extraktion C1 — klinischer Implantatverlust", 10, False),
 ("7  Extraktion C2 — marginaler Knochenverlust", 10, False),
 ("8  Extraktion C3 — Überleben keramischer Implantate", 10, False),
 ("9  Qualitative Synthese — eingeschlossen, aber nicht poolbar", 10, False),
 ("10 RoB SYRCLE — Verzerrungsrisiko tierexperimenteller Studien", 10, False),
 ("11 RoB 2 — Verzerrungsrisiko randomisierter klinischer Studien", 10, False),
 ("12 ROBINS-I — Verzerrungsrisiko nichtrandomisierter Studien", 10, False),
 ("13 Ergebnisse — alle Metaanalysen im Überblick", 10, False), ("", 10, False),
 ("Hinweis: Screening und Extraktion erfolgten KI-gestützt durch einen einzelnen Extraktor,", 10, False),
 ("nicht durch zwei unabhängige menschliche Reviewer. Vor jeder Verwendung ist die vollständige", 10, False),
 ("Verifikation gegen die Primärquellen erforderlich (PMID und DOI sind je Studie angegeben).", 10, False),
]
for i, (t, sz, bold) in enumerate(inhalt, start=1):
    ws.cell(i, 1, t).font = Font(size=sz, bold=bold, color="1F4E79" if bold and i == 1 else "000000")
ws.column_dimensions["A"].width = 120

# --- 1 Screening-Sheet ---
with open(os.path.join(HERE, "Screening-Sheet_vollstaendig.csv"), encoding="utf-8-sig") as f:
    rd = list(csv.reader(f, delimiter=";"))
kopf, zeilen = rd[0], rd[1:]
ws = blatt(wb, "1 Screening-Sheet", kopf, zeilen,
           breiten=[10, 7, 20, 60, 28, 24, 12, 22, 16, 12, 16, 12, 80], tabelle=False)
idx = kopf.index("stufe3")
for r in range(2, ws.max_row + 1):
    v = ws.cell(r, idx + 1).value
    fill = GRUEN if v == "EINGESCHLOSSEN" else (GELB if v == "ausgeschlossen" else GRAU)
    for c in range(1, 13): ws.cell(r, c).fill = fill
ws.auto_filter.ref = f"A1:{get_column_letter(len(kopf))}{ws.max_row}"

# --- 2 Eingeschlossene Studien ---
recs = {json.loads(l)["pmid"]: json.loads(l) for l in open(os.path.join(ROOT, "02_suche", "records_gesamt.jsonl"))}
kurz = json.load(open(os.path.join(ROOT, "07_dissertation", "kurzbelege.json")))
incl = {}
for k, v in D.ALLE.items():
    for r in v: incl.setdefault(r["pmid"], set()).add(k)
z = []
for pm, an in sorted(incl.items(), key=lambda x: kurz.get(x[0], "zz")):
    r = recs.get(pm, {})
    z.append([kurz.get(pm, ""), pm, r.get("year"), "; ".join((r.get("authors") or [])[:4]),
              r.get("title"), r.get("journal"), r.get("doi"), r.get("pmc"), ", ".join(sorted(an))])
blatt(wb, "2 Eingeschlossene Studien",
      ["Kurzbeleg", "PMID", "Jahr", "Autoren", "Titel", "Zeitschrift", "DOI", "PMCID", "Analysen"],
      z, breiten=[26, 11, 7, 40, 70, 34, 30, 14, 14])

# --- 3-9 Extraktionsblätter ---
NAMEN = {"A1": "3 Extraktion A1", "B1": "4 Extraktion B1", "B2": "5 Extraktion B2",
         "C1": "6 Extraktion C1", "C2": "7 Extraktion C2", "C3": "8 Extraktion C3",
         "Q": "9 Qualitative Synthese"}
for k, name in NAMEN.items():
    rows = D.ALLE[k]
    felder = []
    for r in rows:
        for f in r:
            if f not in felder: felder.append(f)
    z = []
    for r in rows:
        z.append([kurz.get(r["pmid"], "")] + [r.get(f, "") for f in felder])
    blatt(wb, name, ["Kurzbeleg"] + felder, z,
          breiten=[24] + [11 if f in ("mt","sdt","nt","mk","sdk","nk","jahr","zeit_w","et","ek","n","ereignisse","nachbeob_mo") else 26 for f in felder])

# --- 10-12 RoB ---
sys.path.insert(0, os.path.join(ROOT, "04_extraktion"))
import risk_of_bias as R
for name, dom, tab, beg in [("10 RoB SYRCLE", R.SYRCLE_DOMAENEN, R.SYRCLE, R.SYRCLE_BEGRUENDUNG),
                            ("11 RoB 2", R.ROB2_DOMAENEN, R.ROB2, R.ROB2_BEGRUENDUNG),
                            ("12 ROBINS-I", R.ROBINS_DOMAENEN, R.ROBINS, R.ROBINS_BEGRUENDUNG)]:
    z = [[s] + v + [beg.get(s, "")] for s, v in tab.items()]
    ws = blatt(wb, name, ["Studie"] + dom + ["Begründung"], z,
               breiten=[24] + [15] * len(dom) + [55], tabelle=False)
    for r in range(2, ws.max_row + 1):
        for c in range(2, len(dom) + 2):
            val = ws.cell(r, c).value
            ws.cell(r, c).fill = {"niedrig": GRUEN, "unklar": GELB, "einige Bedenken": GELB,
                                  "hoch": ROT, "kritisch": ROT}.get(val, GRAU)
            ws.cell(r, c).alignment = Alignment(horizontal="center")
    ws.auto_filter.ref = f"A1:{get_column_letter(len(dom)+2)}{ws.max_row}"

# --- 13 Ergebnisse ---
E = json.load(open(os.path.join(ROOT, "05_analyse", "ergebnisse.json")))
LAB = {"A1_BIC_Keramik_vs_Titan": ("A1  BIC Keramik vs. Titan (präklinisch)", "Mittelwertdifferenz (Prozentpunkte)"),
       "B1_BIC_OFM_vs_maschiniert": ("B1  BIC Oberflächenmodifikation vs. maschiniert", "Mittelwertdifferenz (Prozentpunkte)"),
       "B2_Biomechanik_OFM_vs_maschiniert": ("B2  biomechanische Verankerung", "Hedges' g"),
       "C1_klinischer_Implantatverlust_ZrO2_vs_Ti": ("C1  klinischer Implantatverlust", "Risk Ratio"),
       "C2_marginaler_Knochenverlust_ZrO2_vs_Ti": ("C2  marginaler Knochenverlust", "Mittelwertdifferenz (mm)"),
       "C3_Ueberleben_Keramikimplantate": ("C3  Überleben keramischer Implantate", "Anteil (%)")}
z = []
for k, (lab, em) in LAB.items():
    v = E[k]
    if k.startswith("C1"): est, lo, hi = v["RR"], v["RR_ci"][0], v["RR_ci"][1]
    elif k.startswith("C3"): est, lo, hi = v["anteil"]*100, v["anteil_ci"][0]*100, v["anteil_ci"][1]*100
    else: est, lo, hi = v["est"], v["ci_lo"], v["ci_hi"]
    z.append([lab, em, int(v["k"]), round(est, 4), round(lo, 4), round(hi, 4),
              round(v["pval"], 4), round(v["tau2"], 4), round(v["I2"], 1),
              f"Q({int(v['Q_df'])}) = {v['Q']:.2f}", round(v["Q_p"], 4),
              (f"{v['pi_lo']:.3f} bis {v['pi_hi']:.3f}" if k not in ("C1_klinischer_Implantatverlust_ZrO2_vs_Ti",) else
               f"{2.718281828**v['pi_lo']:.3f} bis {2.718281828**v['pi_hi']:.3f}")])
ws = blatt(wb, "13 Ergebnisse",
      ["Analyse", "Effektmaß", "k", "Punktschätzer", "95 %-KI unten", "95 %-KI oben",
       "p", "tau²", "I² (%)", "Q", "p (Q)", "95 %-Vorhersageintervall"], z,
      breiten=[42, 32, 6, 14, 14, 14, 10, 10, 9, 14, 10, 26])
ws.append([])
ws.append(["Random-Effects-Modell, τ² nach REML, Konfidenzintervall nach Hartung-Knapp-Sidik-Jonkman."])
ws.append(["Erstellt am 09.09.2026 mit Python 3.11 (NumPy/SciPy); Code unter 05_analyse/."])

out = os.path.join(ROOT, "Arbeitsmappe_Metaanalyse.xlsx")
wb.save(out)
print("gespeichert:", out, os.path.getsize(out)//1024, "KB |", len(wb.sheetnames), "Blätter")
