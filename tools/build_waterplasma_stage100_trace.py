#!/usr/bin/env python3
from pathlib import Path
import argparse, re

KEYS={"ELASTIC","EFFECTIVE","MOMENTUM","EXCITATION","IONIZATION","ATTACHMENT"}
SEP=re.compile(r"^-{5,}")

def parse_bolsig(path):
    lines=Path(path).read_text(errors="replace").splitlines()
    out=[]; i=0
    while i < len(lines):
        kind=lines[i].strip().upper()
        if kind not in KEYS:
            i+=1; continue
        i+=1
        while i<len(lines) and not lines[i].strip(): i+=1
        target=lines[i].strip(); i+=1
        arg=None
        if kind!="ATTACHMENT":
            while i<len(lines) and not lines[i].strip(): i+=1
            arg=lines[i].strip(); i+=1
        while i<len(lines) and not SEP.match(lines[i].strip()): i+=1
        if i>=len(lines): raise RuntimeError(f"no data start for {kind} {target}")
        i+=1; data=[]
        while i<len(lines) and not SEP.match(lines[i].strip()):
            s=lines[i].strip()
            if s:
                p=s.split()
                try: data.append((float(p[0]),float(p[1])))
                except: pass
            i+=1
        lhs,rhs=target,None
        if "->" in target:
            lhs,rhs=[x.strip() for x in target.split("->",1)]
        threshold=0.0
        if kind!="ATTACHMENT":
            threshold=float(arg.split()[0])
        out.append(dict(kind=kind,target=lhs,product=rhs,threshold=threshold,data=data))
        i+=1
    return out

def one(ps,target,product,kind):
    h=[p for p in ps if p["target"]==target and p["product"]==product and p["kind"]==kind]
    if len(h)!=1: raise RuntimeError((target,product,kind,len(h)))
    return h[0]

def reverse(p):
    de=p["threshold"]; d=[]
    for e,s in p["data"]:
        ed=e-de
        if ed>1e-9: d.append((ed,((ed+de)/ed)*s))
    if d and d[0][0]>1e-6: d.insert(0,(max(0,d[0][0]-1e-6),0.0))
    return dict(kind="ATTACHMENT",threshold=0.0,data=d,diagnostic_semantics="superelastic_sigma_rate_only")

def ev(kind,threshold,rows):
    d=[(e,s*1e-4) for e,s in rows]
    if threshold is not None and d[0][0]>threshold: d.insert(0,(threshold,0.0))
    return dict(kind=kind,threshold=threshold or 0.0,data=d)

R25=[(12.5,4.8e-18),(15,2.1e-17),(17.5,4.8e-17),(20,5.9e-17),(22.5,7.5e-17),(25,9.8e-17),(30,1.2e-16),(35,1.37e-16),(40,1.51e-16),(45,1.67e-16),(50,1.74e-16),(55,1.84e-16),(60,1.89e-16),(70,1.92e-16),(80,1.96e-16),(90,1.97e-16),(100,1.97e-16),(125,1.92e-16),(150,1.84e-16),(200,1.69e-16),(250,1.55e-16),(300,1.4e-16),(400,1.24e-16),(500,1.11e-16),(600,9.8e-17),(800,8.1e-17),(1000,7e-17)]
R26=[(14,6.7e-18),(16,2.69e-17),(18,4.11e-17),(20,5.27e-17),(22.5,6.84e-17),(25,8.27e-17),(27.5,9.22e-17),(30,1.02e-16),(35,1.17e-16),(40,1.29e-16),(50,1.41e-16),(60,1.48e-16),(70,1.54e-16),(80,1.57e-16),(90,1.56e-16),(100,1.56e-16),(120,1.53e-16),(140,1.51e-16),(160,1.46e-16),(200,1.39e-16),(250,1.3e-16),(300,1.22e-16),(400,1.06e-16),(500,9.5e-17),(600,8.44e-17),(800,7.31e-17),(1000,6.66e-17)]
R29=[(6.7,8.8e-21),(6.8,1.76e-20),(6.9,4.4e-20),(7,7.92e-20),(7.1,1.5e-19),(7.2,3.34e-19),(7.3,5.37e-19),(7.4,7.13e-19),(7.5,8.62e-19),(7.6,9.59e-19),(7.7,1.04e-18),(7.8,1.076e-18),(7.9,1.103e-18),(8,1.115e-18),(8.1,1.117e-18),(8.2,1.116e-18),(8.3,1.109e-18),(8.4,1.1e-18),(8.5,1.103e-18),(8.6,1.106e-18),(8.7,1.1e-18),(8.8,1.088e-18),(8.9,1.069e-18),(9,1.04e-18),(9.1,1e-18),(9.2,9.5e-19),(9.3,8.88e-19),(9.4,8.27e-19),(9.5,7.48e-19),(9.6,6.51e-19),(9.7,5.81e-19),(9.8,5.1e-19),(9.9,4.4e-19),(10,3.78e-19),(10.1,3.17e-19),(10.2,2.64e-19),(10.3,2.2e-19),(10.4,1.76e-19),(10.5,1.41e-19),(10.6,1.14e-19),(10.7,9.24e-20),(10.8,7.92e-20),(10.9,7.04e-20),(11,6.16e-20),(11.5,4.4e-20),(12,4.4e-20),(12.5,3.52e-20),(13,3.52e-20)]
R31=[(0.4,4.6e-19),(0.5,1.33e-18),(0.6,1.73e-18),(0.7,1.92e-18),(0.8,2.04e-18),(0.9,2.08e-18),(1,2.15e-18),(1.1,2.23e-18),(1.2,2.33e-18),(1.3,2.48e-18),(1.4,2.78e-18),(1.5,3.28e-18),(1.6,3.92e-18),(1.7,4.93e-18),(1.8,5.94e-18),(1.9,6.62e-18),(2,7.57e-18),(2.1,8.26e-18),(2.2,8.59e-18),(2.3,8.55e-18),(2.4,8.02e-18),(2.5,7.09e-18),(2.6,5.97e-18),(2.7,4.83e-18),(2.8,3.56e-18),(2.9,2.6e-18),(3,1.91e-18),(3.1,1.39e-18),(3.2,9.7e-19),(3.3,6.3e-19),(3.4,4.7e-19),(3.5,3.5e-19),(3.6,2.8e-19),(3.7,2.3e-19),(3.8,1.9e-19),(3.9,1.7e-19),(4,1.3e-19)]

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--n2"); ap.add_argument("--o2"); ap.add_argument("--air"); ap.add_argument("--out"); a=ap.parse_args()
    n2,o2,air=map(parse_bolsig,[a.n2,a.o2,a.air])
    P={}
    for i in range(1,9): P[f"R{i}"]=one(n2,"N2",f"N2(v{i})","EXCITATION")
    for i in range(1,9): P[f"R{8+i}"]=reverse(P[f"R{i}"])
    for i in range(1,5): P[f"R{16+i}"]=one(o2,"O2",f"O2(v{i})","EXCITATION")
    for i in range(1,5): P[f"R{20+i}"]=reverse(P[f"R{16+i}"])
    P["R25"]=ev("IONIZATION",9.26,R25); P["R26"]=ev("IONIZATION",12.89,R26)
    P["R28"]=one(air,"O3","O2^-","ATTACHMENT"); P["R29"]=ev("ATTACHMENT",6.7,R29)
    P["R30"]=one(air,"O3","O^-","ATTACHMENT"); P["R31"]=ev("ATTACHMENT",0.4,R31)
    P["R49"]=one(air,"O","O(1D)","EXCITATION"); P["R50"]=one(air,"O","O(1S)","EXCITATION")
    P["R53"]=one(air,"N","N^+","IONIZATION"); P["R54"]=one(air,"O","O^+","IONIZATION")
    missing=["R9","R10","R11","R12","R13","R14","R15","R16","R21","R22","R23","R24","R25","R26","R28","R29","R30","R31","R49","R50","R53","R54"]
    L=[]
    for rid in missing:
        p=P[rid]; tgt="TR_"+rid; kind=p["kind"]
        L.append(kind); L.append(f"{tgt} -> {tgt}_P")
        if kind!="ATTACHMENT": L.append(f'{p["threshold"]:.12g}')
        L += [f"COMMENT: PAWNF001 Stage100 diagnostic target for {rid}; mole fraction exactly zero",
              "------------------------------------------------------------"]
        L += [f"{e:.12e} {s:.12e}" for e,s in p["data"]]
        L += ["------------------------------------------------------------",""]
    Path(a.out).write_text("\n".join(L))
    print("generated",len(missing),"channels",Path(a.out).stat().st_size,"bytes")
if __name__=="__main__": main()
