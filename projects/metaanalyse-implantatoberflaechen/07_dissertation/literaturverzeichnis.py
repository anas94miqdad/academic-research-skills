#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Erzeugt das Literaturverzeichnis (Vancouver-Stil) aus den verifizierten PubMed-Datensaetzen.
Jede Angabe stammt unmittelbar aus dem MEDLINE-Datensatz; es werden keine Angaben ergaenzt,
die nicht in der Quelle stehen."""
import json, os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "04_extraktion"))
import datensatz as D

recs = {json.loads(l)["pmid"]: json.loads(l) for l in open(os.path.join(ROOT, "02_suche", "records_gesamt.jsonl"))}
meth = json.load(open(os.path.join(HERE, "methodenreferenzen.json")))

ABK = {  # Zeitschriftentitel -> gebraeuchliche Abkuerzung
 "Clinical oral implants research": "Clin Oral Implants Res",
 "Clinical oral investigations": "Clin Oral Investig",
 "Clinical implant dentistry and related research": "Clin Implant Dent Relat Res",
 "The International journal of oral & maxillofacial implants": "Int J Oral Maxillofac Implants",
 "International journal of oral and maxillofacial surgery": "Int J Oral Maxillofac Surg",
 "Journal of clinical periodontology": "J Clin Periodontol",
 "Journal of periodontology": "J Periodontol",
 "Journal of periodontal research": "J Periodontal Res",
 "Journal of dental research": "J Dent Res",
 "Journal of dentistry": "J Dent",
 "Dental materials : official publication of the Academy of Dental Materials": "Dent Mater",
 "Dental materials journal": "Dent Mater J",
 "Materials (Basel, Switzerland)": "Materials (Basel)",
 "Journal of prosthodontics : official journal of the American College of Prosthodontists": "J Prosthodont",
 "The Journal of oral implantology": "J Oral Implantol",
 "The journal of advanced prosthodontics": "J Adv Prosthodont",
 "International journal of implant dentistry": "Int J Implant Dent",
 "BMC oral health": "BMC Oral Health",
 "BMJ (Clinical research ed.)": "BMJ",
 "BMC medical research methodology": "BMC Med Res Methodol",
 "Journal of biomedical materials research. Part B, Applied biomaterials": "J Biomed Mater Res B Appl Biomater",
 "Journal of biomedical materials research": "J Biomed Mater Res",
 "Journal of biomedical materials research. Part A": "J Biomed Mater Res A",
 "Acta biomaterialia": "Acta Biomater",
 "Biomaterials": "Biomaterials",
 "Periodontology 2000": "Periodontol 2000",
 "Journal of prosthodontic research": "J Prosthodont Res",
 "Materials science & engineering. C, Materials for biological applications": "Mater Sci Eng C",
 "BioMed research international": "Biomed Res Int",
 "Journal of stomatology, oral and maxillofacial surgery": "J Stomatol Oral Maxillofac Surg",
 "Journal of cranio-maxillo-facial surgery : official publication of the European Association for Cranio-Maxillo-Facial Surgery": "J Craniomaxillofac Surg",
 "Brazilian dental journal": "Braz Dent J",
 "The Saudi dental journal": "Saudi Dent J",
 "Journal of functional biomaterials": "J Funct Biomater",
 "International journal of nanomedicine": "Int J Nanomedicine",
 "Nanomaterials (Basel, Switzerland)": "Nanomaterials (Basel)",
 "Korean journal of orthodontics": "Korean J Orthod",
 "Scandinavian journal of plastic and reconstructive surgery. Supplementum": "Scand J Plast Reconstr Surg Suppl",
 "Acta orthopaedica Scandinavica": "Acta Orthop Scand",
 "Controlled clinical trials": "Control Clin Trials",
 "Biometrics": "Biometrics",
 "BMJ open": "BMJ Open",
 "Progress in orthodontics": "Prog Orthod",
 "Medicina (Kaunas, Lithuania)": "Medicina (Kaunas)",
 "Life (Basel, Switzerland)": "Life (Basel)",
 "Bioengineering (Basel, Switzerland)": "Bioengineering (Basel)",
 "Journal of clinical medicine": "J Clin Med",
 "Biology": "Biology (Basel)",
 "SLAS technology": "SLAS Technol",
 "Cureus": "Cureus",
 "Odontology": "Odontology",
 "Head & face medicine": "Head Face Med",
 "Journal of pharmacy & bioallied sciences": "J Pharm Bioallied Sci",
 "International dental journal": "Int Dent J",
 "Journal of esthetic and restorative dentistry": "J Esthet Restor Dent",
 "Journal of the mechanical behavior of biomedical materials": "J Mech Behav Biomed Mater",
 "International journal of oral implantology (Berlin, Germany)": "Int J Oral Implantol (Berl)",
 "European journal of oral implantology": "Eur J Oral Implantol",
 "Implant dentistry": "Implant Dent",
 "Advances in clinical and experimental medicine": "Adv Clin Exp Med",
 "The International journal of periodontics & restorative dentistry": "Int J Periodontics Restorative Dent",
 "Yeungnam University journal of medicine": "Yeungnam Univ J Med",
 "Journal of dental sciences": "J Dent Sci",
 "Regenerative biomaterials": "Regen Biomater",
 "Clinical and experimental dental research": "Clin Exp Dent Res",
 "Journal of nanoscience and nanotechnology": "J Nanosci Nanotechnol",
 "Osteoporosis international : a journal established as result of cooperation between the European Foundation for Osteoporosis and the National Osteoporosis Foundation of the USA": "Osteoporos Int",
 "Journal of oral and maxillofacial surgery : official journal of the American Association of Oral and Maxillofacial Surgeons": "J Oral Maxillofac Surg",
 "Wiadomosci lekarskie (Warsaw, Poland : 1960)": "Wiad Lek",
 "Clinical, cosmetic and investigational dentistry": "Clin Cosmet Investig Dent",
 "Heliyon": "Heliyon",
 "Dentistry journal": "Dent J (Basel)",
 "Journal of oral biology and craniofacial research": "J Oral Biol Craniofac Res",
 "Journal of periodontal & implant science": "J Periodontal Implant Sci",
 "Oral and maxillofacial surgery": "Oral Maxillofac Surg",
 "Annals of biomedical engineering": "Ann Biomed Eng",
 "Biomaterials research": "Biomater Res",
 "Microbial pathogenesis": "Microb Pathog",
 "Minerva dental and oral science": "Minerva Dent Oral Sci",
 "Evidence-based dentistry": "Evid Based Dent",
 "Tissue engineering and regenerative medicine": "Tissue Eng Regen Med",
 "The European journal of prosthodontics and restorative dentistry": "Eur J Prosthodont Restor Dent",
 "Journal of orthopaedic research : official publication of the Orthopaedic Research Society": "J Orthop Res",
 "Journal of materials science. Materials in medicine": "J Mater Sci Mater Med",
 "Annals of anatomy = Anatomischer Anzeiger : official organ of the Anatomische Gesellschaft": "Ann Anat",
 "Journal of esthetic dentistry": "J Esthet Dent",
 "Vojnosanitetski pregled": "Vojnosanit Pregl",
 "Journal of biological regulators and homeostatic agents": "J Biol Regul Homeost Agents",
 "PloS one": "PLoS One",
 "Frontiers in bioengineering and biotechnology": "Front Bioeng Biotechnol",
 "Journal of long-term effects of medical implants": "J Long Term Eff Med Implants",
 "Dental research journal": "Dent Res J (Isfahan)",
 "Annals of the Royal Australasian College of Dental Surgeons": "Ann R Australas Coll Dent Surg",
 "Scientific reports": "Sci Rep",
 "Implant dentistry": "Implant Dent",
 "The American journal of otology": "Am J Otol",
 "Journal of clinical periodontology": "J Clin Periodontol",
}
def abk(j):
    return ABK.get(j, j)

def autoren(a, maxn=6):
    if not a: return "[o. A.]"
    if len(a) <= maxn: return ", ".join(a)
    return ", ".join(a[:maxn]) + " et al"

def eintrag(r):
    t = (r.get("titel") or r.get("title") or "").rstrip(".")
    au = autoren(r.get("autoren") or r.get("authors") or [])
    j = abk(r.get("journal") or "")
    y = r.get("jahr") or r.get("year") or ""
    doi = r.get("doi") or ""
    pm = r.get("pmid") or ""
    s = f"{au}. {t}. {j}. {y}."
    if doi: s += f" doi:{doi}."
    if pm: s += f" PMID:{pm}."
    return s

if __name__ == "__main__":
    from collections import Counter
    PART = {"de","da","van","von","der","den","del","dos","du","le","la","el","al"}
    def surname(a):
        t = a.split()
        return " ".join(t[:2]) if len(t) >= 3 and t[0].lower() in PART else t[0]
    def kurz(au, y):
        if not au: return f"o. A. {y}"
        n = surname(au[0])
        if len(au) == 1: return f"{n} {y}"
        if len(au) == 2: return f"{n} & {surname(au[1])} {y}"
        return f"{n} et al. {y}"
    incl = {}
    for k, v in D.ALLE.items():
        for r in v: incl.setdefault(r["pmid"], set()).add(k)
    items = []
    for pm, an in incl.items():
        r = recs.get(pm)
        if r: items.append(dict(pmid=pm, autoren=r["authors"], titel=r["title"],
                                journal=r["journal"], jahr=r["year"], doi=r["doi"], analysen=sorted(an)))
    for k, r in meth.items():
        if r and r["pmid"] not in incl:
            items.append(dict(pmid=r["pmid"], autoren=r["autoren"], titel=r["titel"],
                              journal=r["journal"], jahr=r["jahr"], doi=r["doi"], analysen=[]))
    for i in items: i["kurz"] = kurz(i["autoren"], i["jahr"])
    items.sort(key=lambda x: (surname((x["autoren"] or ["ZZ"])[0]).lower(), int(x["jahr"] or 0)))
    c = Counter(i["kurz"] for i in items); seen = Counter()
    for i in items:
        if c[i["kurz"]] > 1:
            seen[i["kurz"]] += 1; i["kurz"] = i["kurz"] + chr(96 + seen[i["kurz"]])
    NORM = {"39506212": "de Beus et al. 2025", "38940623": "Ruiz Henao et al. 2024"}
    for i in items: i["kurz"] = NORM.get(i["pmid"], i["kurz"])
    weitere = [
     ("Viechtbauer 2010", "Viechtbauer W. Conducting meta-analyses in R with the metafor package. J Stat Softw. 2010;36(3):1-48. doi:10.18637/jss.v036.i03."),
     ("Higgins et al. 2024", "Higgins JPT, Thomas J, Chandler J, Cumpston M, Li T, Page MJ, Welch VA (Hrsg.). Cochrane Handbook for Systematic Reviews of Interventions. Version 6.5. Cochrane; 2024."),
     ("Freeman & Tukey 1950", "Freeman MF, Tukey JW. Transformations related to the angular and the square root. Ann Math Stat. 1950;21(4):607-611. doi:10.1214/aoms/1177729756."),
     ("Miller 1978", "Miller JJ. The inverse of the Freeman-Tukey double arcsine transformation. Am Stat. 1978;32(4):138. doi:10.1080/00031305.1978.10479283."),
     ("Hedges & Olkin 1985", "Hedges LV, Olkin I. Statistical Methods for Meta-Analysis. Orlando: Academic Press; 1985."),
    ]
    out = ["# Literaturverzeichnis", "",
      "Alle bibliographischen Angaben wurden unmittelbar aus dem MEDLINE-Datensatz der jeweiligen",
      "Publikation uebernommen (Abruf 09.09.2026). PMID und DOI sind mitgefuehrt, damit jede Angabe",
      "unabhaengig ueberpruefbar ist. Der Kurzbeleg der linken Spalte entspricht der Zitierweise im Text.", "",
      "Kennzeichnung: **[A1]** Knochen-Implantat-Kontakt Keramik vs. Titan - **[B1]** Knochen-Implantat-",
      "Kontakt Oberflaechenmodifikation - **[B2]** biomechanische Verankerung - **[C1]** klinischer",
      "Implantatverlust - **[C2]** marginaler Knochenverlust - **[C3]** UEberleben keramischer Implantate -",
      "**[Q]** qualitative Synthese (keine poolbaren Kennwerte).", "",
      f"Eintraege insgesamt: {len(items)+len(weitere)} - davon {len(incl)} eingeschlossene Primaerstudien.", "",
      "| Kurzbeleg | Vollbeleg |", "|---|---|"]
    for i in items:
        a = autoren(i["autoren"]); t = (i["titel"] or "").rstrip(".")
        voll = f"{a}. {t}. {abk(i['journal'] or '')}. {i['jahr']}."
        if i["doi"]: voll += f" doi:{i['doi']}."
        voll += f" PMID:{i['pmid']}."
        if i["analysen"]: voll += " **[" + ", ".join(i["analysen"]) + "]**"
        out.append(f"| {i['kurz']} | {voll} |")
    out += ["", "## Nicht in PubMed indexierte Quellen", "", "| Kurzbeleg | Vollbeleg |", "|---|---|"]
    for k, v in weitere: out.append(f"| {k} | {v} |")
    open(os.path.join(HERE, "Literaturverzeichnis.md"), "w").write("\n".join(out) + "\n")
    json.dump({i["pmid"]: i["kurz"] for i in items},
              open(os.path.join(HERE, "kurzbelege.json"), "w"), indent=1, ensure_ascii=False)
    print("Literaturverzeichnis:", len(items) + len(weitere), "Eintraege |", len(incl), "Primaerstudien")
