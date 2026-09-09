#!/usr/bin/env python3
"""Holt Volltexte (PMC OA / Europe PMC) fuer alle Kandidaten-PMIDs."""
import json,os,re,time,urllib.request,urllib.parse,xml.etree.ElementTree as ET
HERE=os.path.dirname(os.path.abspath(__file__)); OUT=os.path.join(HERE,"volltexte")
recs={}
for l in open(os.path.join(HERE,"..","02_suche","records_gesamt.jsonl")):
    r=json.loads(l); recs[r["pmid"]]=r
def get(url,data=None,timeout=45,tries=2):
    for a in range(tries):
        try:
            req=urllib.request.Request(url,data=data)
            with urllib.request.urlopen(req,timeout=timeout) as r: return r.read()
        except Exception:
            if a==tries-1: return None
            time.sleep(1)
def clean(x):
    x=re.sub(r"\s+"," ",x); return x.strip()
def pmc_xml_to_text(b):
    try: root=ET.fromstring(b)
    except Exception: return None
    parts=[]
    for sec in root.iter():
        if sec.tag in ("title","p","td","th","label","caption"):
            t=clean("".join(sec.itertext()))
            if t: parts.append(t)
    return "\n".join(parts) if parts else None
def fetch_pmc(pmcid):
    b=get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&retmode=xml&id="+pmcid.replace("PMC",""))
    return pmc_xml_to_text(b) if b else None
def fetch_epmc(pmid):
    b=get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/MED/{pmid}/fullTextXML",tries=1,timeout=25)
    return pmc_xml_to_text(b) if b else None
if __name__=="__main__":
    import sys
    pmids=[l.strip() for l in open(sys.argv[1]) if l.strip()]
    ok=0; miss=[]
    for i,pm in enumerate(pmids):
        f=os.path.join(OUT,f"{pm}.txt")
        if os.path.exists(f) and os.path.getsize(f)>2000: ok+=1; continue
        r=recs.get(pm,{}); txt=None
        if r.get("pmc"): txt=fetch_pmc(r["pmc"])
        if (not txt or len(txt)<2000) and r.get("pmc"): txt=fetch_epmc(pm)
        if txt and len(txt)>2000:
            open(f,"w").write(txt); ok+=1
        else: miss.append(pm)
        if i%25==0: print(f"  {i}/{len(pmids)} ok={ok}",flush=True)
        time.sleep(0.2)
    print("Volltexte:",ok,"| ohne Volltext:",len(miss))
    open(os.path.join(HERE,"ohne_volltext.txt"),"w").write("\n".join(miss))
