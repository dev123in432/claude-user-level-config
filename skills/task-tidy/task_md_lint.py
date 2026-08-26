"""Deterministic hygiene linter for task-folder docs (task.md / readme.md).

Executable form of task-docs.md (sibling file). Portable: stdlib only, repo-agnostic. Run it
with a plain `python` from any repo root; targets are resolved relative to --root (default: cwd).

Modes:

  --check     report structure violations per file; exit non-zero if any file is BLOATED (default)
  --summary   one line per BLOATED file (for /hello); exit non-zero if any
  --fix       apply the SAFE mechanical fixes to task.md in place (collapse stacked PICKUP
              blocks to the newest, stamp undated [x] with (done today), sweep [x] older than
              5 days, strip Done / Completed Steps / Resolved-out-of-scope archive blocks)

Target selection:

  --file PATH   one file
  --all         every task.md, and every readme.md that has a sibling task.md, under --root/tasks
                (skips _-prefixed and zzz-archive folders)

Only --fix mutates, and only task.md. readme.md fixes need judgment; --check flags them so
they can be handled by the semantic pass (this skill) or by hand. Fixes are idempotent: a
second --fix is a no-op. Checklist items are treated as whole units, so a (done) stamp on a
wrapped continuation line counts.

Examples (from a repo root):
  python "%USERPROFILE%\\.claude\\skills\\task-tidy\\task_md_lint.py" --all --check
  python "%USERPROFILE%\\.claude\\skills\\task-tidy\\task_md_lint.py" --file tasks/erm-connector/task.md --fix

--today YYYY-MM-DD overrides the current date (for deterministic tests).
--root PATH overrides the repo root scanned by --all (default: current working directory).
"""

import argparse
import datetime as dt
import re
import sys
from pathlib import Path

# --- rule constants -------------------------------------------------------

SWEEP_DAYS = 5          # [x] items older than this (by their (done) stamp) are swept by --fix
LINE_WARN = 200         # weak secondary signal only

PICKUP_RE = re.compile(r"^PICKUP (\d{4}-\d{2}-\d{2}):")
HEADING_RE = re.compile(r"^(#{1,6}) ")
CHECK_ITEM_RE = re.compile(r"^\s*- \[[ xX]\]")
DONE_ITEM_RE = re.compile(r"^\s*- \[[xX]\]")
DONE_STAMP_RE = re.compile(r"\(done (\d{4}-\d{2}-\d{2})\)")
INBOX_HEADING_RE = re.compile(r"^#{2,6}\s+.*Inbox from", re.I)
AUTHOR_NOTE_RE = re.compile(r"^\s*>>")
ERROR_LOG_RE = re.compile(r"^\s*>+\s*Error:", re.I)
FENCE_RE = re.compile(r"^\s*```\s*(sql|powershell|python|json|results|bash|sh)\b", re.I)
STRIKE_DONE_RE = re.compile(r"~~.*~~.*\bDONE\b", re.I)
ARCHIVE_HEADING_RE = re.compile(
    r"^(#{2,4})\s*(Done\b|Completed Steps\b|Completed\b|Resolved or out of scope\b)", re.I
)
# readme.md-only smells
README_STATE_HEADING_RE = re.compile(  # clear state sections that belong in task.md
    r"^#{2,6}\s*(Now|Next|Pickup|Recently done|Open items?)\b", re.I
)
README_STATUS_DATED_RE = re.compile(r"^#{2,6}\s*Status\b.*\(\d{4}-\d{2}-\d{2}\)", re.I)  # dated snapshot
README_STATUS_BARE_RE = re.compile(r"^#{2,6}\s*Status\b", re.I)  # could be a pointer; warn only


class Finding:
    def __init__(self, severity, code, message):
        self.severity = severity  # "VIOLATION" | "WARNING"
        self.code = code
        self.message = message

    def __str__(self):
        return f"  [{self.severity}] {self.code}: {self.message}"


# --- block / item parsers -------------------------------------------------

def find_pickup_blocks(lines):
    """[(start, end_exclusive, date_str)] for each PICKUP block.

    A block runs from its `PICKUP YYYY-MM-DD:` line until the next PICKUP line, the next
    markdown heading, or EOF - whichever comes first.
    """
    blocks = []
    i, n = 0, len(lines)
    while i < n:
        m = PICKUP_RE.match(lines[i])
        if m:
            start, date = i, m.group(1)
            i += 1
            while i < n and not PICKUP_RE.match(lines[i]) and not HEADING_RE.match(lines[i]):
                i += 1
            blocks.append((start, i, date))
        else:
            i += 1
    return blocks


def iter_items(lines):
    """Yield (start, end_exclusive, is_done, stamp_date_or_None) for each checklist item.

    An item is its `- [ ]`/`- [x]` marker line plus following continuation lines (indented,
    non-blank, not a new marker), so a (done) stamp on a wrapped line still belongs to the item.
    """
    i, n = 0, len(lines)
    while i < n:
        if CHECK_ITEM_RE.match(lines[i]):
            start = i
            i += 1
            while (i < n and lines[i].strip() != "" and lines[i][:1] in (" ", "\t")
                   and not CHECK_ITEM_RE.match(lines[i])):
                i += 1
            text = "\n".join(lines[start:i])
            is_done = bool(DONE_ITEM_RE.match(lines[start]))
            m = DONE_STAMP_RE.search(text)
            yield (start, i, is_done, m.group(1) if m else None)
        else:
            i += 1


def max_table_run(lines):
    run = best = 0
    for ln in lines:
        if ln.lstrip().startswith("|"):
            run += 1
            best = max(best, run)
        else:
            run = 0
    return best


def _parse_date(s):
    try:
        return dt.date.fromisoformat(s)
    except (ValueError, TypeError):
        return None


# --- checkers -------------------------------------------------------------

def check_task_md(lines):
    findings = []

    blocks = find_pickup_blocks(lines)
    if len(blocks) == 0:
        findings.append(Finding("WARNING", "no-pickup", "no PICKUP block at top of file"))
    elif len(blocks) > 1:
        dates = ", ".join(b[2] for b in blocks)
        findings.append(Finding("VIOLATION", "multi-pickup",
                                f"{len(blocks)} PICKUP blocks stacked ({dates}) - keep only the newest"))

    items = list(iter_items(lines))
    done = [it for it in items if it[2]]
    bare = [it for it in done if it[3] is None]
    if bare:
        sev = "VIOLATION" if len(bare) > 5 else "WARNING"
        findings.append(Finding(sev, "undated-x",
                                f"{len(bare)} of {len(done)} [x] items lack a (done YYYY-MM-DD) stamp"))

    inbox = [ln for ln in lines if INBOX_HEADING_RE.match(ln)]
    if len(inbox) > 1:
        findings.append(Finding("VIOLATION", "inbox-sections",
                                f"{len(inbox)} '## Inbox from' sections - distill into actions and tombstone"))
    elif len(inbox) == 1:
        findings.append(Finding("WARNING", "inbox-sections",
                                "1 '## Inbox from' section - distill into actions and tombstone"))

    notes = sum(1 for ln in lines if AUTHOR_NOTE_RE.match(ln))
    if notes:
        findings.append(Finding("VIOLATION", "author-notes",
                                f"{notes} '>>' author-note line(s) - resolve and delete"))

    fences = sum(1 for ln in lines if FENCE_RE.match(ln))
    errs = sum(1 for ln in lines if ERROR_LOG_RE.match(ln))
    if fences or errs:
        bits = []
        if fences:
            bits.append(f"{fences} code fence(s)")
        if errs:
            bits.append(f"{errs} error-log line(s)")
        findings.append(Finding("VIOLATION", "result-dumps",
                                f"pasted output in a checklist ({', '.join(bits)}) - move to readme/design or drop"))

    wide = max_table_run(lines)
    if wide > 8:
        findings.append(Finding("WARNING", "wide-table",
                                f"a {wide}-row table - a mapping table belongs in readme/a design doc"))

    archive = [ln for ln in lines if ARCHIVE_HEADING_RE.match(ln)]
    strike = sum(1 for ln in lines if STRIKE_DONE_RE.search(ln))
    if archive:
        findings.append(Finding("VIOLATION", "archive-block",
                                f"{len(archive)} Done/Completed/Resolved archive heading(s) - git holds history"))
    if strike:
        findings.append(Finding("VIOLATION", "strike-done",
                                f"{strike} ~~strikethrough~~ DONE line(s) - tick + date or delete"))

    if len(lines) > LINE_WARN:
        findings.append(Finding("WARNING", "long-file",
                                f"{len(lines)} lines (weak signal; fine if disciplined)"))
    return findings


def check_readme_md(lines):
    findings = []
    boxes = sum(1 for ln in lines if CHECK_ITEM_RE.match(ln))
    if boxes:
        findings.append(Finding("VIOLATION", "readme-checkboxes",
                                f"{boxes} checkbox item(s) - task state belongs in task.md"))
    state = [ln.strip() for ln in lines
             if README_STATE_HEADING_RE.match(ln) or README_STATUS_DATED_RE.match(ln)]
    if state:
        findings.append(Finding("VIOLATION", "readme-state-heading",
                                f"{len(state)} live-state heading(s) (e.g. '{state[0]}') - move to task.md"))
    bare_status = [ln.strip() for ln in lines
                   if README_STATUS_BARE_RE.match(ln) and not README_STATUS_DATED_RE.match(ln)]
    if bare_status:
        findings.append(Finding("WARNING", "readme-status",
                                f"a bare '{bare_status[0]}' heading - keep only a pointer to task.md, not state"))
    if any(PICKUP_RE.match(ln) for ln in lines):
        findings.append(Finding("VIOLATION", "readme-pickup",
                                "a live PICKUP block - keep a pointer to task.md, not the block"))
    return findings


# --- fixer (task.md only) -------------------------------------------------

def fix_task_md(lines, today, sweep=True):
    """Return (new_lines, [action strings]). Idempotent.

    sweep=False keeps [x] items that are already older than 5 days (used for a one-off backfill,
    where a wholesale sweep would delete an entire dated trail at once; sweeping is meant to run
    incrementally each session).
    """
    actions = []
    drop = set()

    # 1. collapse stacked PICKUP blocks to the newest-dated one
    blocks = find_pickup_blocks(lines)
    if len(blocks) > 1:
        newest = max(range(len(blocks)), key=lambda i: blocks[i][2])
        for idx, (start, end, date) in enumerate(blocks):
            if idx != newest:
                drop.update(range(start, end))
        actions.append(f"collapsed {len(blocks)} PICKUP blocks to the newest ({blocks[newest][2]})")

    # 2. strip archive heading blocks (heading -> next same-or-higher heading / EOF)
    i, n = 0, len(lines)
    stripped = 0
    while i < n:
        m = ARCHIVE_HEADING_RE.match(lines[i])
        if m and i not in drop:
            level = len(m.group(1))
            start = i
            j = i + 1
            while j < n:
                hm = HEADING_RE.match(lines[j])
                if hm and len(hm.group(1)) <= level:
                    break
                j += 1
            drop.update(range(start, j))
            stripped += 1
            i = j
        else:
            i += 1
    if stripped:
        actions.append(f"stripped {stripped} archive heading block(s)")

    interim = [ln for idx, ln in enumerate(lines) if idx not in drop]

    # 3. stamp / sweep whole checklist items (stamp goes on the item's last line)
    today_d = _parse_date(today)
    stamp_at = {}      # last-line index -> stamped text
    sweep_idx = set()  # indices to drop
    stamped = swept = 0
    for start, end, is_done, stamp in iter_items(interim):
        if not is_done:
            continue
        if stamp is None:
            last = end - 1
            stamp_at[last] = f"{interim[last].rstrip()} (done {today})"
            stamped += 1
        elif sweep:
            d = _parse_date(stamp)
            if d and today_d and (today_d - d).days > SWEEP_DAYS:
                sweep_idx.update(range(start, end))
                swept += 1

    out = []
    for idx, ln in enumerate(interim):
        if idx in sweep_idx:
            continue
        out.append(stamp_at.get(idx, ln))
    if stamped:
        actions.append(f"stamped {stamped} undated [x] item(s) with (done {today})")
    if swept:
        actions.append(f"swept {swept} [x] item(s) older than {SWEEP_DAYS} days")

    return out, actions


# --- file / verdict plumbing ----------------------------------------------

def read_lines(path):
    return path.read_text(encoding="utf-8").split("\n")


def verdict(findings):
    if any(f.severity == "VIOLATION" for f in findings):
        return "BLOATED"
    if findings:
        return "WARN"
    return "CLEAN"


def analyse(path):
    lines = read_lines(path)
    if path.name.lower() == "readme.md":
        return check_readme_md(lines)
    return check_task_md(lines)


def collect_targets(root, one_file):
    if one_file:
        return [Path(one_file)]
    tasks_dir = root / "tasks"
    if not tasks_dir.exists():
        return []
    seen, targets = set(), []
    for p in sorted(tasks_dir.rglob("task.md")):
        if _skip(p) or p.resolve() in seen:
            continue
        seen.add(p.resolve())
        targets.append(p)
    for p in sorted(tasks_dir.rglob("readme.md")):
        # only a task-folder orientation file (has a sibling task.md), not a nested build README
        if _skip(p) or p.resolve() in seen or not (p.parent / "task.md").exists():
            continue
        seen.add(p.resolve())
        targets.append(p)
    return targets


def _skip(path):
    return any(part.startswith("_") or part.startswith("zzz") for part in path.parts)


def main():
    ap = argparse.ArgumentParser(description="task.md / readme.md hygiene linter")
    ap.add_argument("--file", help="lint a single file")
    ap.add_argument("--all", action="store_true", help="lint every task.md + sibling readme.md under --root")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="report per file (default)")
    mode.add_argument("--summary", action="store_true", help="one line per BLOATED file (for /hello)")
    mode.add_argument("--fix", action="store_true", help="apply safe mechanical fixes to task.md")
    ap.add_argument("--today", default=dt.date.today().isoformat(), help="override today (YYYY-MM-DD)")
    ap.add_argument("--root", default=str(Path.cwd()), help="repo root scanned by --all (default: cwd)")
    ap.add_argument("--quiet", action="store_true", help="with --check, only print files that are not CLEAN")
    ap.add_argument("--no-sweep", action="store_true",
                    help="with --fix, keep [x] older than 5 days (for a one-off backfill)")
    args = ap.parse_args()

    if not args.file and not args.all:
        ap.error("pass --file PATH or --all")

    root = Path(args.root).resolve()
    targets = collect_targets(root, args.file)

    if args.fix:
        return run_fix(targets, args.today, root, sweep=not args.no_sweep)
    if args.summary:
        return run_summary(targets, root)
    return run_check(targets, args.quiet, root)


def run_check(targets, quiet, root):
    bloated = []
    for path in targets:
        findings = analyse(path)
        v = verdict(findings)
        if v == "BLOATED":
            bloated.append(path)
        if quiet and v == "CLEAN":
            continue
        print(f"{v:8} {_rel(path, root)}")
        for f in findings:
            print(f)
    if bloated:
        print(f"\n{len(bloated)} file(s) need a tidy (run /task-tidy):")
        for p in bloated:
            print(f"  - {_rel(p, root)}")
        return 1
    if not quiet:
        print("\nAll files clean.")
    return 0


def run_summary(targets, root):
    bloated = []
    for path in targets:
        findings = analyse(path)
        if verdict(findings) == "BLOATED":
            codes = ",".join(sorted({f.code for f in findings if f.severity == "VIOLATION"}))
            bloated.append((path, codes))
    if not bloated:
        print("task docs: all clean")
        return 0
    print(f"task docs: {len(bloated)} file(s) need /task-tidy:")
    for p, codes in bloated:
        print(f"  - {_rel(p, root)} ({codes})")
    return 1


def run_fix(targets, today, root, sweep=True):
    changed = 0
    for path in targets:
        if path.name.lower() == "readme.md":
            continue  # --fix only mutates task.md; readme fixes need judgment
        lines = read_lines(path)
        new_lines, actions = fix_task_md(lines, today, sweep=sweep)
        if actions:
            path.write_text("\n".join(new_lines), encoding="utf-8")
            changed += 1
            print(f"FIXED {_rel(path, root)}")
            for a in actions:
                print(f"  - {a}")
        else:
            print(f"ok    {_rel(path, root)}")
    print(f"\n{changed} file(s) changed. Review with git diff; run /task-tidy for anything --check still flags.")
    return 0


def _rel(path, root):
    try:
        return str(path.resolve().relative_to(root))
    except ValueError:
        return str(path)


if __name__ == "__main__":
    sys.exit(main())
