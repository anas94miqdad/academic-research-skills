#!/usr/bin/env python3
"""Holt vollstaendige MEDLINE-Datensaetze fuer alle eindeutigen PMIDs und speichert sie als JSONL."""
import json, time, os, urllib.parse, urllib.request, xml.etree.ElementTree as ET

OUT = os.path.dirname(os.path.abspath(__file__))
BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

def fetch(pmids):
    data = urllib.parse.urlencode({"db": "pubmed", "id": ",".join(pmids), "retmode": "xml"}).encode()
    for a in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(BASE, data=data), timeout=120) as r:
                return r.read()
        except Exception:
            if a == 4: raise
            time.sleep(2 ** a)

def txt(el):
    return "".join(el.itertext()).strip() if el is not None else ""

def parse(xml_bytes):
    root = ET.fromstring(xml_bytes); recs = []
    for art in root.findall(".//PubmedArticle"):
        m = art.find(".//MedlineCitation")
        pmid = txt(m.find("PMID"))
        a = m.find(".//Article")
        title = txt(a.find("ArticleTitle"))
        abst = " ".join(txt(x) for x in a.findall(".//Abstract/AbstractText"))
        journal = txt(a.find(".//Journal/Title"))
        year = txt(a.find(".//Journal/JournalIssue/PubDate/Year")) or txt(a.find(".//Journal/JournalIssue/PubDate/MedlineDate"))[:4]
        pts = [txt(x) for x in a.findall(".//PublicationTypeList/PublicationType")]
        langs = [txt(x) for x in a.findall(".//Language")]
        mesh = [txt(x.find("DescriptorName")) for x in m.findall(".//MeshHeadingList/MeshHeading")]
        doi = ""
        for aid in art.findall(".//ArticleIdList/ArticleId"):
            if aid.get("IdType") == "doi": doi = txt(aid)
        pmc = ""
        for aid in art.findall(".//ArticleIdList/ArticleId"):
            if aid.get("IdType") == "pmc": pmc = txt(aid)
        authors = []
        for au in a.findall(".//AuthorList/Author")[:12]:
            ln, fn = txt(au.find("LastName")), txt(au.find("Initials"))
            if ln: authors.append(f"{ln} {fn}".strip())
        recs.append(dict(pmid=pmid, title=title, abstract=abst, journal=journal, year=year,
                         pubtypes=pts, languages=langs, mesh=mesh, doi=doi, pmc=pmc, authors=authors))
    return recs

if __name__ == "__main__":
    pmids = open(os.path.join(OUT, "pmids_alle_unique.txt")).read().split()
    print("PMIDs:", len(pmids))
    path = os.path.join(OUT, "records.jsonl")
    n = 0
    with open(path, "w") as f:
        for i in range(0, len(pmids), 200):
            batch = pmids[i:i+200]
            for r in parse(fetch(batch)):
                f.write(json.dumps(r, ensure_ascii=False) + "\n"); n += 1
            print(f"  {i+len(batch)}/{len(pmids)} -> {n} Datensaetze", flush=True)
            time.sleep(0.4)
    print("Gespeichert:", n)
