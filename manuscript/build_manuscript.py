#!/usr/bin/env python3
"""Build the single-file Tampa ecology manuscript from canonical section drafts."""
from __future__ import annotations
import argparse
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

SOURCES={
    "intro": ROOT/"manuscript/TAMPA_ECOLOGY_ABSTRACT_INTRO_V1.md",
    "methods": ROOT/"manuscript/TAMPA_ECOLOGY_METHODS_V1.md",
    "results": ROOT/"manuscript/TAMPA_ECOLOGY_RESULTS_DISCUSSION_V1.md",
    "captions": ROOT/"manuscript/TAMPA_ECOLOGY_FIGURE_CAPTIONS_V1.md",
    "references": ROOT/"manuscript/TAMPA_ECOLOGY_REFERENCES_V1.md",
}

def read(name:str)->str:
    return SOURCES[name].read_text()

def build()->str:
    intro=read("intro")
    methods=read("methods")
    results=read("results")
    captions=read("captions")
    references=read("references")

    m=re.search(r"## Working title\s+\*\*([^*]+)\*\*",intro,re.S)
    if not m:
        raise RuntimeError("working title not found")
    title=m.group(1).strip()

    if "## Abstract" not in intro or "# Results" not in results:
        raise RuntimeError("required manuscript section marker missing")

    intro_section=intro[intro.index("## Abstract"):].strip()
    methods_body="\n".join(methods.splitlines()[2:]).strip()
    results_section=results[results.index("# Results"):].strip()
    captions_body="\n".join(captions.splitlines()[2:]).strip()
    references_body="\n".join(references.splitlines()[2:]).strip()

    text=(
        f"# {title}\n\n"
        f"{intro_section}\n\n"
        "# Methods\n\n"
        f"{methods_body}\n\n"
        f"{results_section}\n\n"
        "# Figure captions\n\n"
        f"{captions_body}\n\n"
        "# References\n\n"
        f"{references_body}\n"
    )

    forbidden=["[REF", "CITATION NEEDED", "TODO:"]
    for token in forbidden:
        if token in text:
            raise RuntimeError(f"unresolved manuscript token: {token}")

    required=[
        "post-hoc external ecological",
        "recorded loss",
        "not demographic extinction",
        "mechanism",
        "state decoupling",
    ]
    lower=text.lower()
    for phrase in required:
        if phrase.lower() not in lower:
            raise RuntimeError(f"required claim-boundary phrase missing: {phrase}")

    return text

def main(out:Path):
    text=build()
    out.write_text(text)
    words=len(re.findall(r"\b\w+[\w’'-]*\b",text))
    print(f"built {out} ({words} approximate words)")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=ROOT/"manuscript/TAMPA_ECOLOGY_MANUSCRIPT_V1.md")
    a=p.parse_args()
    main(a.out)
