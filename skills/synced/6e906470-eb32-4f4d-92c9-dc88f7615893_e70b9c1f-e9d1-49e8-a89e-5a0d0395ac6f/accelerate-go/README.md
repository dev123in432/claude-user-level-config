# accelerate-go

The company-wide skill for **GO** (Olympic Go — Accelerate Tech's timesheeting, leave, day-rate and
project-tracking system). It installs the GO Mini MCP for you and then drives it from Claude, on both
**Claude Code** and **Claude Desktop**.

> **Where this works:** **Claude Desktop** and **Claude Code** — the GO server runs locally on your
> machine, so it needs a real desktop client. It is **not** available on **claude.ai in the browser**,
> which can't run the local GO server. Use Desktop or Code for anything GO.

## What it can do

| Area | What you can ask for |
|---|---|
| **Setup** | "Set up GO", "install the GO MCP" — guided install + first-connect sign-in |
| **Timesheets** | "Log my time", "catch up my timesheet", "copy last week onto this week" |
| **Leave** | "Check my leave", "book annual leave next Monday", "cancel a leave request" |
| **Finance / reporting** | "My time and charges for July", "export my hours to Excel", project actuals + estimate status |
| **Team views** | (managers) view or act on a team member's timesheet, team compliance |
| **Favourites** | Tidy up your saved timeslot templates |

## ⚠️ What you can actually do depends on your GO role

**Not every feature above is available to everyone.** The skill can *reach* all of GO's tools, but what
**you** are allowed to do is gated by **your GO user role — exactly the same as the GO website/app.** The
MCP runs as *you*: if you can't do something in GO, you can't do it here either.

- **Everyone (standard / self-scoped role)** — your **own** timesheets, leave, favourites, and your own
  time-and-charges and exports. This covers the day-to-day for most people.
- **Elevated roles (approver / admin)** additionally get — viewing or acting on **other people's**
  timesheets, team compliance, impersonation, and all-resource finance exports.

If a feature returns **"Forbidden"** or only shows your own data, **that's your GO permission level, not a
fault in the skill** — the skill will tell you so and fall back to what you can access. To change what you
can do, your **GO access needs updating** (raise it with whoever manages GO/Olympic access). Getting the
right people onto the right GO roles is a rollout step, separate from installing this skill.

## Clients & setup

Runs on Claude Code and Claude Desktop. To set up, invoke the skill and say "set up GO" (or `/go-setup`) —
it detects your OS, installs the right build, and walks you through the one-time Microsoft sign-in. Full
design and evidence: `Helper Files & Templates/GO_MCP.md` and the design doc under `GO_MCP_design/`.

> Status: **beta** — proven on both Claude Code and Claude Desktop: install, timesheet, leave, favourites,
> finance, and M365 evidence (auto-draft) all work on Live. Team/impersonation needs an elevated-GO-role
> tester before it's confirmed. See `SKILL.md` for the live state.
