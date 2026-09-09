#!/usr/bin/env python3
"""Dokumentierte, reproduzierbare Suchstrategie (PubMed/MEDLINE via NCBI E-utilities).
Erzeugt: blocks_counts.json, pmids_<set>.txt, search_log.md
"""
import json, time, urllib.parse, urllib.request, os, datetime, sys

BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
OUT = os.path.dirname(os.path.abspath(__file__))

def eutil(tool, **params):
    params.setdefault("db", "pubmed")
    url = BASE + tool + ".fcgi?" + urllib.parse.urlencode(params)
    for attempt in range(5):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:
            if attempt == 4: raise
            time.sleep(2 ** attempt)

def esearch(term, retmax=10000):
    txt = eutil("esearch", term=term, retmode="json", retmax=retmax)
    d = json.loads(txt)["esearchresult"]
    return int(d["count"]), d.get("idlist", [])

# ---------------- Suchblöcke ----------------
B = {}
B["P_dental"] = ('("Dental Implants"[MeSH] OR "Dental Implantation, Endosseous"[MeSH] OR '
    '"dental implant*"[tiab] OR "endosseous implant*"[tiab] OR "endosteal implant*"[tiab] OR '
    '"oral implant*"[tiab])')

B["M_keramik"] = ('("zirconia"[tiab] OR "zirconium oxide"[tiab] OR "ZrO2"[tiab] OR "zirconium dioxide"[tiab] OR '
    '"yttria-stabilized"[tiab] OR "yttria stabilized"[tiab] OR "ceramic implant*"[tiab] OR '
    '"alumina"[tiab] OR "aluminium oxide"[tiab] OR "Al2O3"[tiab] OR "silicon nitride"[tiab] OR '
    '"Ceramics"[MeSH] OR "Zirconium"[MeSH] OR "Aluminum Oxide"[MeSH])')

B["M_metall"] = ('("titanium"[tiab] OR "Titanium"[MeSH] OR "Ti-6Al-4V"[tiab] OR "TiAl6V4"[tiab] OR '
    '"titanium-zirconium"[tiab] OR "TiZr"[tiab] OR "Roxolid"[tiab] OR "commercially pure titanium"[tiab] OR '
    '"cpTi"[tiab] OR "titanium alloy*"[tiab] OR "Alloys"[MeSH] OR "tantalum"[tiab])')

B["I_oberflaeche"] = ('("Surface Properties"[MeSH] OR "surface modif*"[tiab] OR "surface treat*"[tiab] OR '
    '"surface roughness"[tiab] OR "surface topograph*"[tiab] OR "surface characteristic*"[tiab] OR '
    '"sandblast*"[tiab] OR "sand-blast*"[tiab] OR "grit-blast*"[tiab] OR "grit blast*"[tiab] OR '
    '"acid-etch*"[tiab] OR "acid etch*"[tiab] OR "SLA"[tiab] OR "SLActive"[tiab] OR "sandblasted large-grit acid-etched"[tiab] OR '
    '"anodiz*"[tiab] OR "anodis*"[tiab] OR "anodic oxidation"[tiab] OR "micro-arc oxidation"[tiab] OR '
    '"plasma spray*"[tiab] OR "hydroxyapatite coat*"[tiab] OR "calcium phosphate coat*"[tiab] OR '
    '"bioactive coating*"[tiab] OR "biofunctionaliz*"[tiab] OR "laser treat*"[tiab] OR "laser-modif*"[tiab] OR '
    '"laser ablation"[tiab] OR "photofunctionaliz*"[tiab] OR "UV treatment"[tiab] OR "ultraviolet treatment"[tiab] OR '
    '"machined surface*"[tiab] OR "turned surface*"[tiab] OR "polished surface*"[tiab] OR '
    '"nanostructur*"[tiab] OR "nanotopograph*"[tiab] OR "microstructur* surface*"[tiab] OR '
    '"Coated Materials, Biocompatible"[MeSH] OR "Dental Etching"[MeSH] OR "Etching"[tiab])')

B["O_outcome"] = ('("Osseointegration"[MeSH] OR "osseointegrat*"[tiab] OR "osteointegrat*"[tiab] OR '
    '"bone-to-implant contact"[tiab] OR "bone to implant contact"[tiab] OR "bone-implant contact"[tiab] OR '
    '"BIC"[tiab] OR "removal torque"[tiab] OR "reverse torque"[tiab] OR "pull-out"[tiab] OR '
    '"push-out"[tiab] OR "marginal bone loss"[tiab] OR "crestal bone"[tiab] OR "peri-implant bone"[tiab] OR '
    '"bone level*"[tiab] OR "implant stability"[tiab] OR "ISQ"[tiab] OR "resonance frequency"[tiab] OR '
    '"survival rate*"[tiab] OR "success rate*"[tiab] OR "implant failure*"[tiab] OR '
    '"Dental Restoration Failure"[MeSH] OR "Dental Implant-Abutment Design"[MeSH] OR '
    '"osteoblast*"[tiab] OR "cell adhesion"[tiab] OR "cell proliferation"[tiab] OR "biocompatib*"[tiab] OR '
    '"Peri-Implantitis"[MeSH] OR "peri-implantitis"[tiab])')

B["F_filter"] = '(english[lang] OR german[lang])'

SETS = {}
# Gesamtsuche: Dentalimplantat UND (Keramik ODER Metall) UND Oberflächenmodifikation UND Outcome
SETS["S1_gesamt"] = f'{B["P_dental"]} AND ({B["M_keramik"]} OR {B["M_metall"]}) AND {B["I_oberflaeche"]} AND {B["O_outcome"]} AND {B["F_filter"]}'
# Direkter Werkstoffvergleich Keramik vs. Metall
SETS["S2_direktvergleich"] = f'{B["P_dental"]} AND {B["M_keramik"]} AND {B["M_metall"]} AND {B["O_outcome"]} AND {B["F_filter"]}'
# Keramik + Oberflächenmodifikation
SETS["S3_keramik_ofm"] = f'{B["P_dental"]} AND {B["M_keramik"]} AND {B["I_oberflaeche"]} AND {B["O_outcome"]} AND {B["F_filter"]}'
# Metall + Oberflächenmodifikation
SETS["S4_metall_ofm"] = f'{B["P_dental"]} AND {B["M_metall"]} AND {B["I_oberflaeche"]} AND {B["O_outcome"]} AND {B["F_filter"]}'
# Bereits existierende Evidenzsynthesen (für Handsuche / Referenzlistenscreening)
SETS["S5_reviews"] = (f'{B["P_dental"]} AND ({B["M_keramik"]} OR {B["M_metall"]}) AND {B["I_oberflaeche"]} '
    f'AND (systematic review[pt] OR meta-analysis[pt] OR "systematic review"[tiab] OR "meta-analysis"[tiab]) AND {B["F_filter"]}')

if __name__ == "__main__":
    stamp = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    results = {"suchdatum_utc": stamp, "datenbank": "PubMed/MEDLINE (NCBI E-utilities)", "bloecke": {}, "sets": {}}
    for name, term in B.items():
        c, _ = esearch(term, retmax=0); results["bloecke"][name] = {"term": term, "treffer": c}
        print(f"BLOCK {name}: {c}", flush=True); time.sleep(0.4)
    allids = set()
    for name, term in SETS.items():
        c, ids = esearch(term)
        results["sets"][name] = {"term": term, "treffer": c, "abgerufen": len(ids)}
        with open(os.path.join(OUT, f"pmids_{name}.txt"), "w") as f: f.write("\n".join(ids))
        allids |= set(ids)
        print(f"SET {name}: {c} (abgerufen {len(ids)})", flush=True); time.sleep(0.4)
    with open(os.path.join(OUT, "pmids_alle_unique.txt"), "w") as f: f.write("\n".join(sorted(allids, key=int)))
    results["unique_gesamt"] = len(allids)
    with open(os.path.join(OUT, "blocks_counts.json"), "w") as f: json.dump(results, f, indent=2, ensure_ascii=False)
    print("UNIQUE GESAMT:", len(allids))
