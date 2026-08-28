#!/usr/bin/env python3
"""Restrict the public data files to the variables the paper reports.

Kept: every exclusion criterion (the instructed-response items) and every
item and composite that enters a reported analysis. Everything else is
dropped, and the codebooks list exactly the retained columns.

Column names are not consistent across the six files -- the same name can
denote different things in different studies -- so every column was
classified from its own content, never from its name.

Usage:  python3 drop_unused_columns.py <src_dir> <dst_dir>
"""
import csv, io, sys, pathlib

# Why each column was dropped, in one of two categories only:
#   "check"  -- a condition-recall or manipulation-recall item the paper does not report
#   "unused" -- a variable no reported analysis uses
WHY = {
    "study1_public.csv":  {"O1": "unused", "M1": "unused", "D1": "unused", "M2": "unused",
                           "A1": "unused", "SI1": "unused", "AT1": "unused", "FA1": "unused",
                           "SBC123567_d": "unused"},
    "study2_public.csv":  {"C1": "check", "NP": "check", "I2": "unused",
                           "F1": "unused", "F2": "unused", "F3": "unused", "F4": "unused"},
    "study3a_public.csv": {"C1": "check", "S1": "check", "I2": "unused", "F1": "unused"},
    "study3b_public.csv": {"C1": "check", "S1": "check", "I2": "unused",
                           "F1": "unused", "F2": "unused", "F3": "unused", "F4": "unused"},
    "study3c_public.csv": {"S1": "check", "I1": "unused",
                           "F1": "unused", "F2": "unused", "F3": "unused", "F4": "unused"},
    "study4_public.csv":  {"C1": "check", "I1": "unused",
                           "M1": "unused", "M2": "unused", "M3": "unused"},
}

DROP = {
    "study1_public.csv": ["O1", "M1", "D1", "M2", "A1", "SI1", "AT1", "FA1",
                          "SBC123567_d"],
    "study2_public.csv": ["C1", "NP", "I2", "F1", "F2", "F3", "F4"],
    "study3a_public.csv": ["C1", "S1", "I2", "F1"],
    "study3b_public.csv": ["C1", "S1", "I2", "F1", "F2", "F3", "F4"],
    "study3c_public.csv": ["S1", "I1", "F1", "F2", "F3", "F4"],
    "study4_public.csv":  ["C1", "I1", "M1", "M2", "M3"],
}


def main(src, dst):
    src, dst = pathlib.Path(src), pathlib.Path(dst)
    dst.mkdir(parents=True, exist_ok=True)
    for fname, drop in DROP.items():
        raw = (src / fname).read_bytes().decode("utf-8")
        nl = "\r\n" if "\r\n" in raw else "\n"
        lines = raw.split(nl)
        cols = next(csv.reader(io.StringIO(lines[0])))
        missing = [c for c in drop if c not in cols]
        if missing:
            sys.exit(f"{fname}: column(s) not found: {missing}")
        keep = [i for i, c in enumerate(cols) if c not in drop]
        out = []
        for ln in lines:
            if not ln.strip():
                out.append(ln); continue
            row = next(csv.reader(io.StringIO(ln)))
            buf = io.StringIO()
            csv.writer(buf, lineterminator="").writerow([row[i] for i in keep])
            out.append(buf.getvalue())
        (dst / fname).write_text(nl.join(out), encoding="utf-8", newline="")
        print(f"{fname}: dropped {len(drop)} ({', '.join(drop)}); "
              f"{len(keep)} columns retained")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".",
         sys.argv[2] if len(sys.argv) > 2 else "trimmed")
