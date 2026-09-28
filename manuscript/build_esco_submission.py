#!/usr/bin/env python3
"""Build the Estuaries and Coasts submission-body manuscript from canonical sources."""
from __future__ import annotations
import argparse
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

SRC={
    "intro": ROOT/"manuscript/TAMPA_ECOLOGY_ABSTRACT_INTRO_V1.md",
    "methods": ROOT/"manuscript/TAMPA_ECOLOGY_METHODS_V1.md",
    "results": ROOT/"manuscript/TAMPA_ECOLOGY_RESULTS_DISCUSSION_V1.md",
    "captions": ROOT/"manuscript/TAMPA_ECOLOGY_FIGURE_CAPTIONS_ESCO_V1.md",
    "references": ROOT/"manuscript/TAMPA_ECOLOGY_REFERENCES_V1.md",
}

def read(k):
    return SRC[k].read_text()

def body_after_first_heading(text: str) -> str:
    return "\n".join(text.splitlines()[2:]).strip()

def build() -> str:
    intro=read("intro")
    methods=read("methods")
    results=read("results")
    captions=read("captions")
    refs=read("references")

    m=re.search(r"## Working title\s+\*\*([^*]+)\*\*", intro, re.S)
    if not m:
        raise RuntimeError("working title missing")
    title=m.group(1).strip()

    abstract=intro[intro.index("## Abstract")+len("## Abstract"):intro.index("## Keywords")].strip()
    keywords=intro[intro.index("## Keywords")+len("## Keywords"):intro.index("---",intro.index("## Keywords"))].strip()

    aw=len(re.findall(r"\b\w+[\w’'-]*\b",re.sub(r"[*_]"," ",abstract)))
    if not 150 <= aw <= 250:
        raise RuntimeError(f"ESCO abstract must be 150-250 words, got {aw}")
    kw=[x.strip() for x in keywords.split(";") if x.strip()]
    if not 4 <= len(kw) <= 6:
        raise RuntimeError(f"ESCO keywords must be 4-6, got {len(kw)}")

    intro_body=intro[intro.index("# Introduction"):].strip()
    methods_body=body_after_first_heading(methods)
    results_body=results[results.index("# Results"):].strip()
    captions_body=body_after_first_heading(captions)
    refs_body=body_after_first_heading(refs)

    text=(
        f"# {title}\n\n"
        "## Abstract\n\n"
        f"{abstract}\n\n"
        "## Keywords\n\n"
        f"{keywords}\n\n"
        f"{intro_body}\n\n"
        "# Methods\n\n"
        f"{methods_body}\n\n"
        f"{results_body}\n\n"
        "# Figure captions\n\n"
        f"{captions_body}\n\n"
        "# References\n\n"
        f"{refs_body}\n"
    )

    lower=text.lower()
    forbidden=[
        "statistically significant",
        "p < 0.05",
        "p<0.05",
        "[ref",
        "citation needed",
    ]
    for token in forbidden:
        if token in lower:
            raise RuntimeError(f"ESCO-forbidden/unresolved manuscript token: {token}")

    for phrase in [
        "post-hoc external ecological",
        "not interpreted as demographic extinction",
        "mechanism",
        "unresolved",
    ]:
        if phrase.lower() not in lower:
            raise RuntimeError(f"required claim-boundary phrase missing: {phrase}")

    bad=re.findall(r"\([A-Z][^()]{0,80}\bet al\. (?:19|20)\d{2}\)",text)
    if bad:
        raise RuntimeError(f"non-APA parenthetical citation punctuation: {bad[:3]}")

    return text

def main(out: Path):
    text=build()
    out.write_text(text)
    words=len(re.findall(r"\b\w+[\w’'-]*\b",text))
    print(f"built {out} ({words} approximate words)")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=ROOT/"manuscript/TAMPA_ECOLOGY_ESCO_SUBMISSION_V1.md")
    a=p.parse_args()
    main(a.out)
