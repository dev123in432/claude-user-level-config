---
description: Work with GO — log time, book leave, run reports, manage favourites (accelerate-go skill)
argument-hint: "[e.g. log today | copy last week | leave balance | export August | setup]"
---

Invoke the `accelerate-go` skill.

Request: $ARGUMENTS

If no argument was given, default to the daily timesheet flow for **today** (local day). Otherwise
interpret the argument as intent and route per the skill's workflow:
- "setup" / "install" / "connect" → guided install (`references/install.md`).
- timesheet phrases (log / catch up / copy last week / EOD) → timesheet drafting flow.
- "leave …" → leave module. "export …" / "finance …" / "time and charges" → finance module.
- "team …" / "on behalf of …" → impersonation module. "favourites …" → favourites module.

If the go-mini-mcp tools are not connected, run the guided install first regardless of the request.
