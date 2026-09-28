#!/usr/bin/env python3
"""Build the single-source Tampa Supplementary Information markdown."""
from __future__ import annotations

import argparse
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
METHODS=ROOT/"manuscript/TAMPA_ECOLOGY_SUPPLEMENT_V1.md"
CAPTIONS=ROOT/"manuscript/TAMPA_ECOLOGY_SUPPLEMENT_CAPTIONS_V1.md"


def body_after_title(text:str)->str:
    lines=text.splitlines()
    return "\n".join(lines[2:]).strip()


def build()->str:
    methods=METHODS.read_text().strip()
    caps=CAPTIONS.read_text().strip()
    if not methods.startswith("# Supplementary Information"):
        raise RuntimeError("supplement title marker missing")
    text=methods+"\n\n# Supplementary display captions\n\n"+body_after_title(caps)+"\n"
    required=[
        "Supplementary Methods S1",
        "Supplementary Methods S14",
        "Fig. S1",
        "Fig. S7",
        "Table S1",
        "Table S9",
        "not demographic extinction",
        "no additional response-free hidden-state simulation family",
    ]
    low=text.lower()
    for phrase in required:
        if phrase.lower() not in low:
            raise RuntimeError(f"required supplement boundary missing: {phrase}")
    forbidden=["CITATION NEEDED","TODO:","[REF"]
    for token in forbidden:
        if token.lower() in low:
            raise RuntimeError(f"unresolved supplement token: {token}")
    return text


def main(out:Path):
    text=build()
    out.write_text(text)
    print(f"built {out} ({len(text.split())} whitespace-delimited tokens)")


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=ROOT/"manuscript/TAMPA_ECOLOGY_SUPPLEMENT_ASSEMBLED_V1.md")
    a=p.parse_args()
    main(a.out)
