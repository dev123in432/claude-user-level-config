---
description: Install and connect the GO Mini MCP on this machine (guided) — accelerate-go skill
argument-hint: "[optional: live | ci]"
---

Invoke the `accelerate-go` skill in **install** mode.

Target environment: $ARGUMENTS (default **live**; use **ci** only for testing).

Follow [`references/install.md`](../references/install.md): detect OS/arch and client, fetch the correct
`.mcpb`, register or install the server, precheck the Entra `http://localhost` redirect, complete the
first-connect sign-in, and verify with a test `timeslot_dayview`.
