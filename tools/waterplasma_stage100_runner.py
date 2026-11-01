#!/usr/bin/env python3
"""
PAWNF001 Stage 100 official BOLSIG+ runner.
"""
from __future__ import annotations
import argparse, json, shutil, subprocess
from pathlib import Path

EN_MIN, EN_MAX, EN_N = 50.0, 250.0, 21
XN2_VALUES = (0.2, 0.5, 0.8)
TG_VALUES = (300.0, 500.0, 750.0, 1000.0)

_R44_CM2 = [
    (12,1e-18),(14,4e-18),(16,2e-17),(18,3.6e-17),(20,5.2e-17),
    (25,8.7e-17),(30,1.04e-16),(40,1.15e-16),(50,1.23e-16),
    (60,1.23e-16),(80,1.2e-16),(100,1.16e-16),(125,1.1e-16),
    (150,1.04e-16),(175,9.9e-17),(200,9.5e-17)
]

def r44_block() -> str:
    rows = ["EXCITATION",
            "N2 -> N + N(total-neutral)",
            "12.0",
            "COMMENT: PAWNF001 R44 BASIS; Song et al. 2023 Table 9; DOI 10.1063/5.0150618; channel-summed",
            "------------------------------------------------------------"]
    rows += [f"{e:.8e} {s*1e-4:.8e}" for e,s in _R44_CM2]
    rows += ["------------------------------------------------------------", ""]
    return "\n".join(rows)

def job_text(tg: float, xn2: float, tag: str) -> str:
    xo2 = 1.0 - xn2
    return f"""NOSCREEN

READCOLLISIONS
N2_STAGE100_WITH_R44.dat
N2
1

READCOLLISIONS
O2_COMPLETE_STAGE100.txt
O2
1

CONDITIONS
50.
0.
0.
{tg:.1f}
0.
0.
0.
3e22
1.
1.
0
1
1
0.
400
2
200.
1e-10
1e-6
1000
{xn2:.8f} {xo2:.8f}
1

RUNSERIES
1
{EN_MIN:.1f} {EN_MAX:.1f}
{EN_N}
1

SAVERESULTS
BOLSIG_STAGE100_FULL_{tag}.dat
1
1
1
1
0
0
1
0

END
"""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bolsig", required=True)
    ap.add_argument("--n2", required=True)
    ap.add_argument("--o2", required=True)
    ap.add_argument("--workdir", required=True)
    ap.add_argument("--generate-only", action="store_true")
    args = ap.parse_args()

    work = Path(args.workdir).resolve()
    work.mkdir(parents=True, exist_ok=True)
    bolsig = Path(args.bolsig).resolve()
    n2_src = Path(args.n2).resolve()
    o2_src = Path(args.o2).resolve()

    if not n2_src.is_file() or not o2_src.is_file():
        raise SystemExit("Frozen N2/O2 source file missing")
    if not args.generate_only and not bolsig.is_file():
        raise SystemExit("Official bolsigminus executable missing")

    n2_text = n2_src.read_text(encoding="utf-8", errors="replace").rstrip() + "\n\n" + r44_block()
    (work/"N2_STAGE100_WITH_R44.dat").write_text(n2_text, encoding="utf-8")
    shutil.copyfile(o2_src, work/"O2_COMPLETE_STAGE100.txt")

    manifest = {
      "stage": "100_MODERN_BOLSIG_RATE_TABLE_GENERATION",
      "authority": "official BOLSIG+ required for PASS100",
      "grid": {"EN_Td":[EN_MIN,EN_MAX,10.0], "xN2":list(XN2_VALUES), "Tg_K":list(TG_VALUES)},
      "jobs": []
    }

    for xn2 in XN2_VALUES:
        for tg in TG_VALUES:
            tag = f"xN2_{xn2:.1f}_Tg_{int(tg)}"
            script = work/f"BOLSIG_STAGE100_{tag}.in"
            script.write_text(job_text(tg, xn2, tag), encoding="utf-8")
            rec = {"tag":tag, "xn2":xn2, "xo2":1-xn2, "Tg_K":tg, "input":script.name}
            if not args.generate_only:
                cp = subprocess.run([str(bolsig), script.name], cwd=work, text=True,
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                rec["returncode"] = cp.returncode
                rec["stdout"] = cp.stdout[-4000:]
                log = work/"bolsiglog.txt"
                if log.exists():
                    dst = work/f"bolsiglog_{tag}.txt"
                    if dst.exists(): dst.unlink()
                    log.rename(dst)
                    rec["log"] = dst.name
                if cp.returncode != 0:
                    manifest["jobs"].append(rec)
                    (work/"PAWNF001_100_OFFICIAL_BOLSIG_RUN_MANIFEST.json").write_text(
                        json.dumps(manifest, indent=2), encoding="utf-8")
                    raise SystemExit(f"BOLSIG+ failed at {tag}")
            manifest["jobs"].append(rec)

    manifest["complete"] = True
    manifest["pass100"] = False
    (work/"PAWNF001_100_OFFICIAL_BOLSIG_RUN_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))

if __name__ == "__main__":
    main()
