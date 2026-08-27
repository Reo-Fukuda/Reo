#!/usr/bin/env python3
"""Rename misleading column headers in the public data files.

Each old name read as the opposite of, or as unrelated to, what the column
actually codes. Only the header line is rewritten; every data row is copied
through byte for byte.

Usage:  python3 rename_columns.py /path/to/aspredicted [/path/to/output]
"""
import csv, io, sys, pathlib

RENAMES = {
    "study2_public.csv":  {"paid": "free_dummy"},
    "study3b_public.csv": {"low_flagship": "central_logo",
                           "Flagshipness_MC": "flagship_item"},
    "study3c_public.csv": {"low_flagship": "source_official",
                           "Flagshipness_MC": "flagship_item"},
}

def main(src, dst):
    src, dst = pathlib.Path(src), pathlib.Path(dst)
    dst.mkdir(parents=True, exist_ok=True)
    for fname, mapping in RENAMES.items():
        raw = (src / fname).read_bytes().decode("utf-8")
        nl = "\r\n" if "\r\n" in raw else "\n"
        head, sep, body = raw.partition(nl)
        cols = next(csv.reader(io.StringIO(head)))
        missing = [k for k in mapping if k not in cols]
        if missing:
            sys.exit(f"{fname}: expected column(s) not found: {missing}")
        new = [mapping.get(c, c) for c in cols]
        buf = io.StringIO()
        csv.writer(buf, lineterminator="").writerow(new)
        (dst / fname).write_text(buf.getvalue() + sep + body, encoding="utf-8", newline="")
        print(f"{fname}: " + ", ".join(f"{k} -> {v}" for k, v in mapping.items()))

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".",
         sys.argv[2] if len(sys.argv) > 2 else "corrected")
