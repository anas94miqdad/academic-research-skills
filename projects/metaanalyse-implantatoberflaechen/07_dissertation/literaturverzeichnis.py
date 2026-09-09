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
    # eingeschlossene Studien
    incl = {}
    for k, v in D.ALLE.items():
        for r in v:
            incl.setdefault(r["pmid"], set()).add(k)
    lit = []
    for pm in incl:
        r = recs.get(pm)
        if r: lit.append((r["authors"][0].split()[0] if r["authors"] else "ZZZ", int(r["year"] or 0), pm, r, sorted(incl[pm])))
    lit.sort(key=lambda x: (x[0].lower(), x[1]))
    zusatz = []
    for k, r in meth.items():
        if r and r.get("pmid") not in incl:
            zusatz.append(((r.get("autoren") or ["ZZZ"])[0].split()[0], int(r.get("jahr") or 0), r))
    zusatz.sort(key=lambda x: (x[0].lower(), x[1]))
    lines = []
    nr = 0
    key2nr = {}
    alle = [(a, y, r, sorted(an)) for a, y, pm, r, an in lit] + [(a, y, r, []) for a, y, r in zusatz]
    alle.sort(key=lambda x: (x[0].lower(), x[1]))
    lines.append("## A  Eingeschlossene Studien (n = %d)\n" % len(lit))
    for _, _, pm, r, an in lit:
        nr += 1; key2nr[pm] = nr
        lines.append(f"{nr}. {eintrag(r)}  *[Analyse: {', '.join(an)}]*")
    lines.append("\n## B  Methodische und weiterführende Literatur (n = %d)\n" % len(zusatz))
    for _, _, r in zusatz:
        nr += 1; key2nr[r["pmid"]] = nr
        lines.append(f"{nr}. {eintrag(r)}")
    lines.append("\n## C  Nicht in PubMed indexierte Quellen\n")
    n0 = nr
    weitere = [
     "Viechtbauer W. Conducting meta-analyses in R with the metafor package. J Stat Softw. 2010;36(3):1–48. doi:10.18637/jss.v036.i03.",
     "Higgins JPT, Thomas J, Chandler J, Cumpston M, Li T, Page MJ, Welch VA (Hrsg.). Cochrane Handbook for Systematic Reviews of Interventions. Version 6.5. Cochrane; 2024. www.training.cochrane.org/handbook.",
     "Freeman MF, Tukey JW. Transformations related to the angular and the square root. Ann Math Stat. 1950;21(4):607–611. doi:10.1214/aoms/1177729756.",
     "Miller JJ. The inverse of the Freeman–Tukey double arcsine transformation. Am Stat. 1978;32(4):138. doi:10.1080/00031305.1978.10479283.",
     "Hedges LV, Olkin I. Statistical Methods for Meta-Analysis. Orlando: Academic Press; 1985.",
     "Deutsche Gesellschaft für Implantologie (DGI), Deutsche Gesellschaft für Zahn-, Mund- und Kieferheilkunde (DGZMK). S3-Leitlinie: Implantatprothetische Versorgung. AWMF-Registernummer 083-010. (Fassung zum Recherchezeitpunkt.)",
    ]
    for w in weitere:
        nr += 1; lines.append(f"{nr}. {w}")
    txt = "\n".join(lines)
    open(os.path.join(HERE, "Literaturverzeichnis.md"), "w").write(
        "# Literaturverzeichnis\n\n"
        "Alle Angaben in Abschnitt A und B wurden unmittelbar aus dem MEDLINE-Datensatz der\n"
        "jeweiligen Publikation übernommen (Abruf 09.09.2026); PMID und DOI sind mit angegeben,\n"
        "damit jede Angabe unabhängig überprüfbar ist.\n\n" + txt + "\n")
    json.dump(key2nr, open(os.path.join(HERE, "zitatnummern.json"), "w"), indent=1)
    print("Literaturverzeichnis:", nr, "Einträge (A:", len(lit), "B:", len(zusatz), "C:", nr-n0, ")")
