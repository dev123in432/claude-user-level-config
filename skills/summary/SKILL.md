---
name: summary
description: Quick recap of the current Claude Code window. Only use when explicitly invoked via /summary -- do not trigger automatically on phrases like "recap", "remind me", or "what were we working on".
allowed-tools: 
---

Give a fast, scannable recap of the current conversation so the user can remember which window they're in. No tool calls -- everything you need is already in context.

## How to answer

Scan the conversation and produce a condensed bullet list of the main things worked on, followed by a single `**Currently:**` line showing where things stand right now.

Keep it high-level. One bullet per topic/workstream. If a bullet has closely related sub-moves (small tweaks, follow-ups), tack them onto the end after a dash: `- this, that`.

End with `**Currently:** ...` -- one short line describing the most recent state. What was the last thing happening? Is it waiting on the user, mid-implementation, just finished?

## Format

```
- <topic> - <optional sub-moves>
- <topic>
- <topic> - <optional sub-moves>

**Currently:** <one-line state>
```

## Style

- No preamble. No "Here's a summary of our conversation" opener.
- Scannable at a glance -- this is a memory-jogger, not a report.
- Include file paths, task names, or tool names when they're the clearest handle for a topic.
- If the conversation is very short (one or two exchanges), just say so in one line rather than forcing bullets.

## Example

```
- Drafted `scripts/batch_download.py` - pagination, retry logic
- Debugged ADO auth in `ado.py` - turned out to be stale token cache
- Added `/summary` skill

**Currently:** waiting on your call about whether to bundle the ADO fix into the same PR.
```
