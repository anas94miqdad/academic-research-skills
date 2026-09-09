#!/usr/bin/env python3
"""Stufe 1 der Studienselektion: regelbasiertes, vorab spezifiziertes Vorscreening.
Jeder Datensatz erhaelt Signal-Flags und einen Ausschlussgrund-Code (falls zutreffend).
Vollstaendig deterministisch und reproduzierbar; Ergebnis = Screening-Sheet fuer Stufe 2.
"""
import json, re, os, csv, collections

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "02_suche", "records_gesamt.jsonl")

def rx(*words): return re.compile("|".join(words), re.I)

# --- Materialsignale ---
KERAMIK = rx(r"\bzirconi", r"\bzro2\b", r"zirconium (di)?oxide", r"\bceramic", r"\balumina\b",
             r"aluminium oxide", r"aluminum oxide", r"\bal2o3\b", r"silicon nitride", r"\bsi3n4\b",
             r"yttri[au][- ]stabili", r"\by-?tzp\b", r"\batz\b")
METALL  = rx(r"\btitanium\b", r"\bti-?6al-?4v\b", r"\btial6v4\b", r"\bcp-?ti\b", r"\btizr\b",
             r"titanium[- ]zirconium", r"roxolid", r"\btantalum\b", r"titanium alloy", r"\bti\b(?!me)")
# --- Oberflaechenmodifikation ---
OFM = rx(r"surface modif", r"surface treat", r"surface roughness", r"surface topograph",
         r"sand-?blast", r"grit-?blast", r"air-?abras", r"acid-?etch", r"\bsla\b", r"slactive",
         r"anodi[sz]", r"anodic oxidation", r"micro-?arc oxidation", r"\bmao\b", r"plasma spray",
         r"hydroxyapatite coat", r"\bha[- ]coat", r"calcium phosphate coat", r"bioactive coat",
         r"biofunctionali", r"laser[- ](treat|modif|ablat|structur|textur)", r"photofunctionali",
         r"\buv[- ](treat|irradiat|photo)", r"machined surface", r"turned surface", r"polished surface",
         r"nanostructur", r"nanotopograph", r"nanotub", r"coating", r"etched", r"blasted",
         r"surface characteri", r"modified surface", r"surface energ", r"wettabilit", r"hydrophil")
# --- Outcomes ---
OUT_PRAEKLIN = rx(r"bone[- ](to[- ])?implant contact", r"\bbic\b", r"removal torque", r"reverse torque",
                  r"pull-?out", r"push-?out", r"bone area", r"bone volume", r"\bbv/tv\b", r"osseointegrat")
OUT_KLINISCH = rx(r"marginal bone (loss|level)", r"crestal bone (loss|level)", r"peri-?implant bone (loss|level)",
                  r"\bmbl\b", r"survival rate", r"success rate", r"implant failure", r"cumulative survival",
                  r"\bisq\b", r"resonance frequency", r"implant stability quotient")
OUT_INVITRO  = rx(r"osteoblast", r"cell adhesion", r"cell proliferation", r"cell viability", r"\bmc3t3",
                  r"\bsaos", r"\bmg-?63\b", r"alkaline phosphatase", r"\balp\b", r"protein adsorption",
                  r"biofilm", r"bacterial adhesion", r"mineraliz", r"gene expression", r"osteogenic differentiation")
# --- Studiendesign ---
D_KLINISCH = rx(r"\bpatient", r"randomi[sz]ed", r"\brct\b", r"clinical trial", r"cohort", r"follow-?up",
                r"\bin (a group of )?humans?\b", r"prospective", r"retrospective", r"\bsplit-?mouth\b",
                r"case[- ]control", r"loaded implants? in")
D_TIER = rx(r"\bdog", r"\bcanine\b", r"\bbeagle", r"\brabbit", r"\bminipig", r"\bmini-?pig", r"\bpig\b",
            r"\bswine\b", r"\bsheep\b", r"\bgoat\b", r"\brat\b", r"\brats\b", r"\bmouse\b", r"\bmice\b",
            r"\bmonkey", r"\bbaboon", r"animal model", r"\bin vivo\b", r"tibia", r"femur", r"calvari")
D_INVITRO = rx(r"\bin vitro\b", r"cell culture", r"cultured", r"\bdiscs?\b", r"\bdisks?\b", r"specimens",
               r"\bsem\b", r"\bafm\b", r"\bxps\b", r"contact angle")
# --- harte Ausschluesse ---
EX_PUBTYPE = {"Review","Systematic Review","Meta-Analysis","Editorial","Letter","Comment","News",
              "Case Reports","Practice Guideline","Guideline","Published Erratum","Retraction of Publication",
              "Historical Article","Biography","Interview","Bibliography","Congress","Address","Lecture"}
EX_NICHTDENTAL = rx(r"cochlear implant", r"breast implant", r"intraocular", r"\bstent\b", r"cardiovascular",
                    r"hip (arthroplast|prosthes|replacement)", r"knee (arthroplast|prosthes|replacement)",
                    r"spinal (fusion|cage|implant)", r"\bpenile\b", r"\bcranioplast", r"vascular graft",
                    r"drug[- ]eluting", r"contraceptive implant", r"pacemaker", r"neural (electrode|implant)")
DENTAL = rx(r"dental implant", r"oral implant", r"endosseous", r"endosteal", r"\bjaw\b", r"mandib", r"maxill",
            r"alveolar", r"peri-?implant", r"edentulous", r"tooth", r"teeth", r"\bdent(al|istry)\b",
            r"abutment", r"implantolog", r"\bosseointegrat")

def screen(r):
    t = (r["title"] or "") + " " + (r["abstract"] or "")
    mesh = " ".join(r.get("mesh") or [])
    full = t + " " + mesh
    flags = {
        "keramik": bool(KERAMIK.search(full)),
        "metall": bool(METALL.search(full)),
        "ofm": bool(OFM.search(full)),
        "out_praeklin": bool(OUT_PRAEKLIN.search(t)),
        "out_klinisch": bool(OUT_KLINISCH.search(t)),
        "out_invitro": bool(OUT_INVITRO.search(t)),
        "d_klinisch": bool(D_KLINISCH.search(t)),
        "d_tier": bool(D_TIER.search(t)),
        "d_invitro": bool(D_INVITRO.search(t)),
        "dental": bool(DENTAL.search(full)),
        "hat_abstract": bool((r["abstract"] or "").strip()),
    }
    pts = set(r.get("pubtypes") or [])
    reasons = []
    if pts & EX_PUBTYPE and not (pts & {"Randomized Controlled Trial","Clinical Trial","Comparative Study"}):
        reasons.append("A1_Publikationstyp")
    if not flags["hat_abstract"]:
        reasons.append("A2_kein_Abstract")
    if EX_NICHTDENTAL.search(t) and not DENTAL.search(t):
        reasons.append("A3_nicht_dental")
    if not flags["dental"]:
        reasons.append("A3_nicht_dental")
    if not (flags["keramik"] or flags["metall"]):
        reasons.append("A4_kein_relevanter_Werkstoff")
    if not flags["ofm"]:
        reasons.append("A5_keine_Oberflaechenmodifikation")
    if not (flags["out_praeklin"] or flags["out_klinisch"] or flags["out_invitro"]):
        reasons.append("A6_keine_relevante_Zielgroesse")
    if not (flags["d_klinisch"] or flags["d_tier"] or flags["d_invitro"]):
        reasons.append("A7_Studiendesign_unklar")
    # Analysestrang
    if flags["d_klinisch"] and flags["out_klinisch"]: strang = "klinisch"
    elif flags["d_tier"] and (flags["out_praeklin"] or flags["out_klinisch"]): strang = "praeklinisch_in_vivo"
    elif flags["d_invitro"] or flags["out_invitro"]: strang = "in_vitro"
    else: strang = "unklar"
    return flags, sorted(set(reasons)), strang

if __name__ == "__main__":
    rows, kept = [], 0
    reason_count = collections.Counter(); strang_count = collections.Counter()
    with open(SRC) as f:
        for line in f:
            r = json.loads(line)
            flags, reasons, strang = screen(r)
            status = "AUSGESCHLOSSEN_S1" if reasons else "WEITER_S2"
            if not reasons: kept += 1; strang_count[strang] += 1
            for x in reasons: reason_count[x] += 1
            rows.append(dict(pmid=r["pmid"], jahr=r["year"], autoren="; ".join(r["authors"][:3]),
                             titel=r["title"], journal=r["journal"], doi=r["doi"], pmc=r["pmc"],
                             pubtypes="; ".join(r["pubtypes"]), status_stufe1=status,
                             ausschlussgrund_s1="; ".join(reasons), analysestrang=strang,
                             **{f"sig_{k}": int(v) for k, v in flags.items()}))
    out_csv = os.path.join(HERE, "screening_sheet_stufe1.csv")
    with open(out_csv, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), delimiter=";")
        w.writeheader(); w.writerows(rows)
    with open(os.path.join(HERE, "stufe1_pmids_weiter.txt"), "w") as f:
        f.write("\n".join(r["pmid"] for r in rows if r["status_stufe1"] == "WEITER_S2"))
    summary = {"n_gesamt": len(rows), "n_weiter_stufe2": kept,
               "n_ausgeschlossen_stufe1": len(rows) - kept,
               "ausschlussgruende": dict(reason_count.most_common()),
               "analysestraenge_weiter": dict(strang_count.most_common())}
    json.dump(summary, open(os.path.join(HERE, "stufe1_summary.json"), "w"), indent=2, ensure_ascii=False)
    print(json.dumps(summary, indent=2, ensure_ascii=False))
