# ⓪ Guided install & first-connect

The skill is the guided installer for the GO Mini MCP. This runs when GO isn't connected yet, or on
"set up / install / connect GO". **Steps proven on Live 2026-08-11.**

> **Boundary:** the skill cannot place *itself* onto a fresh Claude Desktop — that first hop is the plugin
> install / MDM push. Once the skill is present, everything below is guided.

## The artifact

Single self-contained server, distributed as a `.mcpb` (a zip) from Azure Blob:
`https://stgominimcp.blob.core.windows.net/releases/latest/GoMiniMcp-acceleratetech-{env}-{os}-{arch}.mcpb`

- `env` = `live` (default) or `ci` (testing).
- `os-arch` = `win-x64` | `osx-x64` (macOS Intel) | `osx-arm64` (macOS Apple Silicon).
- **No Windows-ARM or Linux build** — if detected, stop and tell the user.
- The `.mcpb` contains `GoMiniMcp-{os}.exe`, `icon.png`, `manifest.json`. The manifest's
  `server.mcp_config` is the launch line: `command` = the exe, `args` = `["--config", "acceleratetech-{env}"]`.
  **Environment is just that `--config` flag on one shared binary** (CI and Live exes are byte-identical).

## Preflight for every install

1. **Detect** OS + architecture + client (Claude Code vs Claude Desktop).
2. **Environment**: default `live`; `ci` only if the user asks.
3. **Entra redirect precheck (critical).** The env's Entra app reg must have `http://localhost` (no port)
   registered as a Mobile-and-desktop (public client) redirect, or first-connect fails
   **`AADSTS50011`**. App regs: Live `996f126a-e9da-49a5-8863-2931c07c52ca`, CI
   `a1a7cfed-dfb5-4ef9-96a3-50dd7a8c8813` (tenant `b885cb47-66da-4872-9300-c1d67cd8cd9d`). If the user
   isn't an Entra admin and it isn't set, hand them the fix or the ask-to-admin text (see below) and stop.

## Path A — Claude Desktop

**Do NOT tell users to "double-click" the `.mcpb`.** On Windows the `.mcpb` extension is usually not
associated with Claude Desktop, so double-clicking pops a "how do you want to open this file?" dialog and
goes nowhere. Hand the user these explicit steps instead:

1. Give the user the exact `.mcpb` link for their OS/env; they download it (note where it saves, e.g.
   Downloads).
2. **Install it from inside Claude Desktop:**
   - Open **Claude Desktop → Settings → Extensions** (may sit under "Advanced settings" in some builds).
   - **Drag the downloaded `.mcpb` onto the Extensions window**, OR click **Install extension / Install
     from file** and select the `.mcpb`.
   - Approve the install → Claude Desktop configures it (environment baked in) and auto-updates thereafter.
3. Restart Claude Desktop.
4. First GO call → Entra sign-in + MFA in the browser (complete it).
5. Verify (see below).

Vendor how-to: https://support.claude.com/en/articles/10949351-getting-started-with-local-mcp-servers-on-claude-desktop
Confirmed on Windows: the double-click auto-route does not fire; use the Extensions pane.

## Path B — Claude Code (proven)

```bash
# 1. Download + extract the exe to a durable path (Windows example)
#    base: https://stgominimcp.blob.core.windows.net/releases/latest
curl -sL -o GoMiniMcp.mcpb "$BASE/GoMiniMcp-acceleratetech-live-win-x64.mcpb"
mkdir -p "$LOCALAPPDATA/GoMiniMcp/live"
unzip -o GoMiniMcp.mcpb GoMiniMcp-win-x64.exe icon.png -d "$LOCALAPPDATA/GoMiniMcp/live"

# 2. Register as a user-scope STDIO server
claude mcp add go-mini-mcp --scope user -- \
  "C:\Users\<user>\AppData\Local\GoMiniMcp\live\GoMiniMcp-win-x64.exe" --config acceleratetech-live
```

3. **Restart Claude Code** — MCP servers load at startup only; the 19 tools appear after restart.
4. First GO call → Entra sign-in + MFA (complete within the 90s window).

TODO: macOS paths + the download/extract for `osx-x64` / `osx-arm64`; wrap this as a scripted routine the
skill runs rather than pasting commands.

## Verify (both paths)

- `timeslot_description_standards()` — returns without auth (sanity check the server is up).
- `timeslot_dayview(date: <today ISO>)` — triggers auth; a clean day view confirms end-to-end success.

## AADSTS50011 — the redirect fix (ask-an-admin text)

> Add `http://localhost` (no port) to the GO {env} app reg (`{appId}`) under
> **Authentication → Add a platform → Mobile and desktop applications**, and confirm
> **Allow public client flows = Yes**. Bare `http://localhost` matches any runtime port; the client binds
> a random one each connect.
