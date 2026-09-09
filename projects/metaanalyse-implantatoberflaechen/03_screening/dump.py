import json,sys,re,os
recs={}
for l in open("02_suche/records_gesamt.jsonl"):
    r=json.loads(l); recs[r["pmid"]]=r
def dump(pmids, maxlen=1400, only_new=None, skip=set()):
    for pm in pmids:
        r=recs.get(pm)
        if not r or pm in skip: continue
        print(f"### {r['pmid']}|{r['year']}|{r['journal'][:38]}|PMC={r['pmc'] or '-'}|{'; '.join(r['authors'][:2])}")
        print(f"T: {r['title']}")
        print(f"A: {r['abstract'][:maxlen]}\n")
