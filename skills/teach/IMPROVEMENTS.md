# teach skill - improvements & fixes

Working roadmap for refining this `teach` skill. The plan: fork the upstream repo
(mattpocock/skills), build on it, and push the genuinely good improvements back. This file is
the diff source - what we've changed locally and why, plus what we want to build next.

Status legend: ✅ shipped locally (pending upstream) · 🔨 doing · 💡 proposed · 🧊 candidate idea

Keep this lean. Per "embed over build": prefer reviving/generalising what already works to piling
on new features, and subtract as you add. A feature earns a place here only if it made a real
session better.

---

## ✅ Shipped locally (candidates to push upstream)

- **Links open in a new tab.** Interactive lessons lose progress when a link navigates the tab
  away and the user hits Back. Fix: `<base target="_blank">` in the lesson/reference `<head>`.
  Now in SKILL.md (Lessons > "Links must open in a new tab").
- **Robust browser-opening + browser detection.** "Open via a CLI command" was too thin. Now
  SKILL.md (Lessons > "Opening the lesson") says to check which browser the user actually uses
  and remember it, and to invoke the browser exe directly when a wrapper (e.g. Windows
  `powershell.exe Start-Process`) is blocked by a permission rule. Cross-platform fallbacks included.

---

## 💡 Proposed features (next to build)

### 1. Learner-profile interview at the start
A short, friendly interview when a workspace is first set up (or on request) about *how this person
learns*, not just *what* they want to learn. Captures: preferred modalities (do/read/watch),
attention & energy patterns, session length that actually sticks, motivation drivers, what has
derailed past learning - and any learning peculiarities / neurodivergence (ADHD, dyslexia, etc.)
the user chooses to share.

- **Why:** today the agent *infers* learning style from scattered cues. Making it explicit up front
  hugely improves lesson fit, especially for neurodivergent learners. It directly grounds both
  delivery format and the zone of proximal development.
- **Output:** writes a structured "Learner profile" into `NOTES.md` (consider a
  `LEARNER-PROFILE-FORMAT.md`), which every lesson then honours.
- **Tone:** light and opt-in, about teaching fit not diagnosis. Never required; skippable.
- **Portability:** generic. Belongs in SKILL.md alongside the Mission interview (the *why*), as a
  parallel "how you learn" step.

### 2. MyNotes living page + capture parking lot
A low-friction capture inbox plus a beautiful rendered notes page the agent regenerates on demand.

- **Capture:** a `QUESTIONS.md` parking lot - dump questions and raw notes one line at a time, no
  commitment. The agent reads it at the *start* of every session (warm-start / re-entry hook) and
  answers or folds items into lessons.
- **Render:** `mynotes.html` - the agent renders the raw Notes section into a sectioned, printable,
  link-safe page (videos with timestamps, fact callouts, lesson takeaways, reference tables).
- **Why:** raw notes are a wall to re-read (a real ADHD friction); a rendered, sectioned page is
  findable and motivating. Proven game-changer in the DP-600 workspace.
- **Portability:** generic. Add `QUESTIONS.md` and `mynotes.html` as first-class workspace artifacts
  in SKILL.md, and document the capture -> render loop + "refresh my notes page" trigger.

---

## 🧊 Candidate ideas (unsorted - promote when one proves itself)

- Re-entry / "where we were" recap generator for time-blind, weekly-cadence learners (cheap warm start).
- Progress map across lessons vs the mission's success criteria (visual "you are here").
- Spaced-repetition nudges on glossary terms / past lesson wins.
- Optional session length picker (10 / 20 / 40 min) that scales lesson scope to energy on the day.

---

## Fork / upstream workflow

1. Fork mattpocock/skills; add it as a remote.
2. Diff our local `teach` against upstream; the ✅ items above are the clean, generic ones to PR.
3. Keep this file as the running ledger so the fork review is a tidy diff, not archaeology.
