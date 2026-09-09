#!/usr/bin/env python3
"""Korrigiert DOI/PMCID: nur PubmedData/ArticleIdList auswerten (nicht Referenzlisten)."""
import json,time,os,urllib.parse,urllib.request,xml.etree.ElementTree as ET
BASE="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
def fetch(pmids):
    data=urllib.parse.urlencode({"db":"pubmed","id":",".join(pmids),"retmode":"xml"}).encode()
    for a in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(BASE,data=data),timeout=120) as r: return r.read()
        except Exception:
            if a==4: raise
            time.sleep(2**a)
def ids(xmlb):
    root=ET.fromstring(xmlb); out={}
    for art in root.findall(".//PubmedArticle"):
        pmid=(art.find("MedlineCitation/PMID").text or "").strip()
        doi=pmc=""
        lst=art.find("PubmedData/ArticleIdList")
        if lst is not None:
            for aid in lst.findall("ArticleId"):
                t=aid.get("IdType"); v=(aid.text or "").strip()
                if t=="doi": doi=v
                elif t=="pmc": pmc=v
        # Fallback: ELocationID im Article-Element
        if not doi:
            for el in art.findall("MedlineCitation/Article/ELocationID"):
                if el.get("EIdType")=="doi": doi=(el.text or "").strip()
        out[pmid]=(doi,pmc)
    return out
if __name__=="__main__":
    recs=[json.loads(l) for l in open("records_gesamt.jsonl")]
    pm=[r["pmid"] for r in recs]; mapping={}
    for i in range(0,len(pm),200):
        mapping.update(ids(fetch(pm[i:i+200])))
        if i% 1000==0: print(f"  {i}/{len(pm)}",flush=True)
        time.sleep(0.35)
    n=0
    with open("records_korrigiert.jsonl","w") as f:
        for r in recs:
            d,p=mapping.get(r["pmid"],("",""))
            if r["doi"]!=d or r["pmc"]!=p: n+=1
            r["doi"],r["pmc"]=d,p
            f.write(json.dumps(r,ensure_ascii=False)+"\n")
    print("korrigierte Datensaetze:",n,"von",len(recs))
    print("mit PMC:",sum(1 for r in recs if r["pmc"]),"| mit DOI:",sum(1 for r in recs if r["doi"]))
