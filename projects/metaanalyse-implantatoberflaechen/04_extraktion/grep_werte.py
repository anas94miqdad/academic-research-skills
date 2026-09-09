#!/usr/bin/env python3
"""Zeigt die zahlentragenden Saetze eines Volltextes zu vorgegebenen Zielgroessen."""
import re,sys,os
HERE=os.path.dirname(os.path.abspath(__file__))
PAT={"BIC":r"bone[- ](to[- ])?implant contact|\bBIC\b|\bBIC%|%BIC",
     "RT":r"removal torque|reverse torque|RTQ|push-?out|pull-?out|insertion torque",
     "MBL":r"marginal bone|crestal bone|bone level|MBL|bone loss",
     "SURV":r"surviv|fail|lost|success rate",
     "ISQ":r"\bISQ\b|implant stability quotient|resonance frequency"}
NUM=re.compile(r"\d")
def show(pmid, keys, maxs=40, ctx=260):
    f=os.path.join(HERE,"volltexte",f"{pmid}.txt")
    if not os.path.exists(f): print(f"[{pmid}] KEIN VOLLTEXT"); return
    txt=open(f).read()
    sents=re.split(r"(?<=[.;])\s+|\n", txt)
    seen=set(); n=0
    for s in sents:
        s=s.strip()
        if len(s)<15 or not NUM.search(s): continue
        for k in keys:
            if re.search(PAT[k],s,re.I):
                key=s[:80]
                if key in seen: break
                seen.add(key); n+=1
                print(f"  [{k}] {s[:ctx]}")
                break
        if n>=maxs: break
if __name__=="__main__":
    pm=sys.argv[1]; keys=sys.argv[2].split(",") if len(sys.argv)>2 else list(PAT)
    print(f"=== {pm} ==="); show(pm,keys, int(sys.argv[3]) if len(sys.argv)>3 else 40)
