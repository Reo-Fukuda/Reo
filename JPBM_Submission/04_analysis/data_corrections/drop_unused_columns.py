#!/usr/bin/env python3
"""Drop columns that no reported analysis uses and that form no scale.

Kept deliberately: every exclusion criterion (attention checks), every item
and composite that enters a reported analysis, and any unused column that
turns out to belong to a multi-item scale -- those are listed in HOLD below
and stay until the authors decide whether to report them.

Note that neither `I1`/`I2` nor `F1`-`F4` denote the same thing across files.
`I1` is an instructed-response item in Studies 2, 3a and 3b but a background
variable in 3c and 4; `F1`-`F4` are a cost/value scale in Study 2 and the
flagship scale in 3b/3c. Every column below was classified from its own
content, never from its name.

Usage:  python3 drop_unused_columns.py <src_dir> <dst_dir>
"""
import csv, io, sys, pathlib

# What each dropped column actually was, established from the data itself
# (identifications recorded here because the column no longer appears in the codebook):
WHY = {
    ("study1_public.csv", "O1"): "unused single item; forms no scale",
    ("study1_public.csv", "M1"): "unused single item; forms no scale",
    ("study1_public.csv", "D1"): "unused single item; forms no scale",
    ("study1_public.csv", "M2"): "unused single item; forms no scale",
    ("study2_public.csv", "C1"): "condition-recall check (A01/A02, 277/6)",
    ("study2_public.csv", "NP"): "PRODUCT-FORM recall check: NP=A01 matches physical=1 for 147/149 and "
                                 "NP=A02 matches physical=0 for 127/134 (9 mismatches). Redundant with the "
                                 "reported Inferred Cost manipulation check, so dropped under the authors' "
                                 "decision not to report condition-recall checks",
    ("study2_public.csv", "I2"): "4-category background variable, not a check",
    ("study3a_public.csv", "C1"): "condition-recall check",
    ("study3a_public.csv", "S1"): "condition-recall duplicate of `condition` (r = .99)",
    ("study3a_public.csv", "I2"): "binary background variable, not a check",
    ("study3b_public.csv", "C1"): "condition-recall check",
    ("study3b_public.csv", "S1"): "condition-recall duplicate of `condition`",
    ("study3b_public.csv", "I2"): "3-category background variable, not a check",
    ("study3c_public.csv", "S1"): "condition-recall duplicate of `condition`",
    ("study3c_public.csv", "I1"): "3-category background variable, NOT an instructed-response item "
                                  "(the letter I is reused across files for different things)",
    ("study4_public.csv", "C1"): "condition-recall check",
    ("study4_public.csv", "I1"): "3-category background variable, not a check",
}

DROP = {
    "study1_public.csv": ["O1", "M1", "D1", "M2"],
    "study2_public.csv": ["C1", "NP", "I2"],
    "study3a_public.csv": ["C1", "S1", "I2"],
    "study3b_public.csv": ["C1", "S1", "I2"],
    "study3c_public.csv": ["S1", "I1"],
    "study4_public.csv":  ["C1", "I1"],
}
HOLD = {  # unused but scale-forming; awaiting the reporting decision
    "study1_public.csv":  ("A1, SI1, AT1, FA1", "alpha = .812"),
    "study2_public.csv":  ("F1 (reversed), F2, F3, F4", "alpha = .760"),
    "study3a_public.csv": ("F1", "second monetization item, alpha = .793 with monetization_intent"),
    "study3b_public.csv": ("F1, F2, F3, F4", "flagship scale with flagship_item, alpha = .930"),
    "study3c_public.csv": ("F1, F2, F3, F4", "flagship scale with flagship_item, alpha = .887"),
    "study4_public.csv":  ("M1, M2, M3", "alpha = .792"),
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
        held = HOLD[fname]
        print(f"{fname}: dropped {len(drop)} ({', '.join(drop)}); "
              f"held {held[0]} ({held[1]})")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".",
         sys.argv[2] if len(sys.argv) > 2 else "trimmed")
