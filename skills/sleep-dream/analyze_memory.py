#!/usr/bin/env python
"""Mechanical memory-health analysis for the sleep-dream skill.

Why: subagents repeatedly guessed at facts they should have verified -
whether a referenced file still exists on disk, whether a memory is really
orphaned, whether a "supersede" claim is circular (pointing at the MEMORY.md
index line that exists only to index that same file). This script computes
those facts deterministically so the agent applies judgement to ground truth,
not to a guess.

Usage:
    python analyze_memory.py <memory_dir> [--repo <repo_root>] [--today YYYY-MM-DD]

Prints a JSON report to stdout: per-file age, date markers, on-disk referent
status, inbound/outbound [[links]], MEMORY.md index presence, and flags.
"""
import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

FRONT_RE = re.compile(r"^---\s*$")
DATE_RE = re.compile(r"(20\d\d)-(\d\d)-(\d\d)")
LINK_RE = re.compile(r"\[\[([a-z0-9_\-]+)\]\]")
# Windows abs paths, or repo-relative task/doc/script paths.
WINPATH_RE = re.compile(r"[A-Za-z]:\\[\w \\.\-]+\.\w+")
RELPATH_RE = re.compile(r"\b((?:tasks|docs|scripts|reference-data|msm-mapping|fabric|activity-data|verification|power-apps)/[\w\-./]+\.\w+)")
RESOLVED_RE = re.compile(r"(RESOLVED|Complete|complete|fixed|resolved)\s+(20\d\d-\d\d-\d\d)")
POINT_IN_TIME_RE = re.compile(r"(week of|by|w/c|CHASE[\w ]*|due)\s+(20\d\d-\d\d-\d\d)", re.I)


def parse_front(text):
    """Return (frontmatter_dict, body). Tolerates files with no frontmatter."""
    lines = text.splitlines()
    if not lines or not FRONT_RE.match(lines[0]):
        return {}, text
    end = None
    for i in range(1, len(lines)):
        if FRONT_RE.match(lines[i]):
            end = i
            break
    if end is None:
        return {}, text
    fm = {}
    for ln in lines[1:end]:
        if ":" in ln:
            k, _, v = ln.partition(":")
            fm[k.strip()] = v.strip()
    return fm, "\n".join(lines[end + 1:])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("memory_dir")
    ap.add_argument("--repo", default=None, help="repo root for referent checks")
    ap.add_argument("--today", default=dt.date.today().isoformat())
    args = ap.parse_args()

    mem = Path(args.memory_dir)
    today = dt.date.fromisoformat(args.today)
    repo = Path(args.repo) if args.repo else None

    files = sorted(
        p for p in mem.glob("*.md")
        if p.name != "MEMORY.md" and not p.name.startswith(".")
    )
    index_text = (mem / "MEMORY.md").read_text(encoding="utf-8", errors="replace") if (mem / "MEMORY.md").exists() else ""

    # First pass: collect bodies, slugs, outbound links.
    records = {}
    all_outbound = {}  # slug -> set of linked slugs
    for p in files:
        text = p.read_text(encoding="utf-8", errors="replace")
        fm, body = parse_front(text)
        slug = p.stem
        mtime = dt.date.fromtimestamp(p.stat().st_mtime)
        outbound = set(LINK_RE.findall(body))
        all_outbound[slug] = outbound
        records[slug] = {
            "file": p.name,
            "type": fm.get("type", "?"),
            "description": fm.get("description", ""),
            "predicts": fm.get("predicts", ""),
            "mtime": mtime.isoformat(),
            "age_days": (today - mtime).days,
            "_body": body,
            "outbound_links": sorted(outbound),
        }

    # Inbound link graph.
    inbound = {s: set() for s in records}
    for src, outs in all_outbound.items():
        for dst in outs:
            inbound.setdefault(dst, set()).add(src)

    # Indexed in MEMORY.md? Match by filename (the link target) not by prose.
    for slug, rec in records.items():
        rec["indexed_in_memory_md"] = (rec["file"] in index_text) or (f"[[{slug}]]" in index_text)
        rec["inbound_links"] = sorted(inbound.get(slug, set()))

    # Per-file flags computed from ground truth.
    for slug, rec in records.items():
        body = rec.pop("_body")
        flags = []

        # Resolution markers aged.
        for m in RESOLVED_RE.finditer(body):
            d = dt.date.fromisoformat(m.group(2))
            age = (today - d).days
            if age > 30:
                flags.append(f"resolved-marker {m.group(2)} ({age}d old)")

        # Expired point-in-time claims.
        for m in POINT_IN_TIME_RE.finditer(body):
            d = dt.date.fromisoformat(m.group(2))
            age = (today - d).days
            if age > 14:
                flags.append(f"expired-point-in-time '{m.group(0).strip()}' ({age}d past)")

        # Referent file existence (only meaningful if repo provided).
        referents = set(WINPATH_RE.findall(body))
        for rel in RELPATH_RE.findall(body):
            referents.add(rel)
        missing = []
        present = []
        # Skip template/placeholder paths - they are illustrative, not referents.
        placeholder = re.compile(r"NN-|\{|<|XX|\.\.\.")
        if repo:
            for ref in referents:
                ref = ref.strip().rstrip(".,;:`)")
                if placeholder.search(ref):
                    continue
                cand = Path(ref) if Path(ref).is_absolute() else (repo / ref)
                (present if cand.exists() else missing).append(ref)
        rec["referents_present"] = sorted(set(present))
        rec["referents_missing"] = sorted(set(missing))
        if missing:
            flags.append(f"missing-referents: {sorted(set(missing))}")

        # Orphan: no inbound links AND not indexed in MEMORY.md.
        if not rec["inbound_links"] and not rec["indexed_in_memory_md"]:
            flags.append("orphan (no inbound links, not in MEMORY.md)")

        rec["flags"] = flags

    # Dangling MEMORY.md pointers: [[slug]] or (file.md) targets with no file.
    md_link_targets = set(re.findall(r"\(([\w\-]+\.md)\)", index_text))
    dangling = sorted(t for t in md_link_targets if not (mem / t).exists() and t not in ("MEMORY.md",))

    # Near-duplicate description detection (token Jaccard > 0.6).
    def toks(s):
        return set(re.findall(r"[a-z0-9]{3,}", s.lower()))
    dupes = []
    slugs = list(records)
    for i in range(len(slugs)):
        for j in range(i + 1, len(slugs)):
            a, b = records[slugs[i]], records[slugs[j]]
            ta, tb = toks(a["description"]), toks(b["description"])
            if ta and tb:
                jac = len(ta & tb) / len(ta | tb)
                if jac > 0.5:
                    dupes.append({"a": slugs[i], "b": slugs[j], "jaccard": round(jac, 2)})

    report = {
        "today": today.isoformat(),
        "total_files": len(records),
        "dangling_memory_md_pointers": dangling,
        "near_duplicate_descriptions": sorted(dupes, key=lambda d: -d["jaccard"]),
        "files": records,
    }
    json.dump(report, sys.stdout, indent=2, default=str)


if __name__ == "__main__":
    main()
