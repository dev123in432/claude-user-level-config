# Preferences folder

The skill stores persistent knowledge in a folder the user chooses; it rediscovers it fresh each run.
(Adapted from O33.)

> **TODO (naming):** O33 uses `o33-go-user-preferences/`. Decide whether AT keeps that or renames to an AT
> convention (e.g. `go-user-preferences/`). Renaming means updating every reference here. Until decided,
> keep `o33-go-user-preferences/` so an existing O33 folder is reused.

## Finding it (start of every run)

1. Scan the session's accessible directories (working + additional) for the folder at depth 1–2. Skip
   `node_modules`, `.git`, `_cache`.
2. **Exactly one match** → use it.
3. **No match** → offer, via `AskUserQuestion`: "New setup — create it" (ask which accessible directory;
   scaffold the files from [`knowledge-caches.md`](knowledge-caches.md) with empty headers) or "It's
   already somewhere — I'll tell you" (accept a path; verify the folder + one expected file).
4. **Multiple matches** → ask which is current; offer to archive the others.

## Notes

- Big tool-result artefacts too large for context → `<folder>/_cache/<YYYY-MM-DD>/`, disposable.
- Never store the chosen path outside the folder itself (chicken-and-egg), never hard-code a user's
  layout — every run rediscovers.
- Filesystem access: works on Claude Desktop + local Claude Code; **not** claude.ai web (isolated VM).
