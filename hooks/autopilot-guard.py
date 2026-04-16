"""
autopilot-guard.py -- PreToolUse hook for autopilot mode.

Enforces directory scoping and blocks dangerous patterns when running
claude --dangerously-skip-permissions.

Hook contract:
  - Receives JSON on stdin: {"tool_name": "...", "tool_input": {...}}
  - Exit 0 = allow
  - Exit 2 = block (stderr message shown to Claude)

Safety defaults:
  - Compound commands (&&, ||, ;) are split and each segment checked independently
  - Git uses default-deny: only known read subcommands are allowed
  - Unparseable input fails closed (exit 2)

Reads AUTOPILOT_ROOT env var (absolute path) set by autopilot.ps1.
"""

import json
import os
import re
import sys


# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------

AUTOPILOT_ROOT = os.environ.get("AUTOPILOT_ROOT", "")

# sensitive paths -- always blocked regardless of AUTOPILOT_ROOT
SENSITIVE_PATTERNS = [
    re.compile(r"[\\/]\.ssh[\\/]", re.IGNORECASE),
    re.compile(r"[\\/]\.aws[\\/]", re.IGNORECASE),
    re.compile(r"[\\/]\.azure[\\/]", re.IGNORECASE),
    re.compile(r"[\\/]\.gnupg[\\/]", re.IGNORECASE),
    re.compile(r"(^|[\\/])\.env(\.|$)", re.IGNORECASE),
    re.compile(r"(^|[\\/])config\.local\.py$", re.IGNORECASE),
]

# git subcommands that are read-only and always allowed
GIT_READ_COMMANDS = re.compile(
    r"^git\s+(status|diff|log|show|blame|branch\s+--list|branch\s+-[av]"
    r"|remote\s+-v|rev-parse|ls-files|shortlog|describe|cat-file"
    r"|name-rev|reflog\s+show|stash\s+list|stash\s+show)",
)

# git subcommands that modify state -- kept for documentation, no longer used
# in the check logic (default-deny covers these and any future additions)
GIT_WRITE_COMMANDS = re.compile(
    r"git\s+(push|commit|reset\s+--hard|clean|rebase|merge|cherry-pick"
    r"|tag|stash\s+drop|stash\s+clear|stash\s+pop|stash\s+apply"
    r"|branch\s+-[dD]|checkout\s+--|restore|rm|mv|am|format-patch"
    r"|filter-branch|replace|notes)",
)

# dangerous shell patterns
DANGEROUS_BASH = [
    (re.compile(r"\brm\s+(-[a-zA-Z]*r|-[a-zA-Z]*f)"), "rm with -r or -f flag"),
    (re.compile(r"\bsudo\s"), "sudo"),
    (re.compile(r"curl.*\|.*bash"), "piped curl to bash"),
    (re.compile(r"curl.*\|.*sh"), "piped curl to sh"),
    (re.compile(r"wget.*\|.*bash"), "piped wget to bash"),
    (re.compile(r"wget.*\|.*sh"), "piped wget to sh"),
    (re.compile(r"\bchmod\s+777"), "chmod 777"),
    (re.compile(r"\bmkfs\b"), "mkfs"),
    (re.compile(r"\bdd\s+if="), "dd"),
    (re.compile(r"\bpowershell\b.*Invoke-Expression", re.IGNORECASE), "PowerShell Invoke-Expression"),
    (re.compile(r"\bpowershell\b.*-enc\b", re.IGNORECASE), "PowerShell encoded command"),
    (re.compile(r"\b(env|printenv)\s*$"), "environment variable dump"),
    (re.compile(r"\bexport\s+-p\b"), "export -p (env dump)"),
]


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def block(reason: str):
    """Exit with code 2 to block the tool call."""
    print(f"AUTOPILOT BLOCKED: {reason}", file=sys.stderr)
    sys.exit(2)


def normalize_path(path: str) -> str:
    """Resolve a path to an absolute, normalized form for comparison."""
    # handle git bash paths like /c/Users/...
    if re.match(r"^/[a-zA-Z]/", path):
        path = path[1].upper() + ":" + path[2:]
    # handle forward slashes
    path = path.replace("/", os.sep)
    path = os.path.abspath(path)
    return os.path.normcase(path)


def is_under_root(path: str) -> bool:
    """Check if a normalized path is within AUTOPILOT_ROOT."""
    if not AUTOPILOT_ROOT:
        return True  # no root set, allow everything (shouldn't happen)
    norm_root = normalize_path(AUTOPILOT_ROOT)
    norm_path = normalize_path(path)
    # exact match or child directory
    return norm_path == norm_root or norm_path.startswith(norm_root + os.sep)


def is_claude_memory_path(path: str) -> bool:
    """Check if a path is inside the Claude project memory directory.

    Claude Code stores per-project memory at ~/.claude/projects/{slug}/memory/.
    This is outside the repo but is a normal part of Claude's operation and
    safe to allow in autopilot mode.
    """
    norm = normalize_path(path)
    claude_dir = normalize_path(os.path.join(os.path.expanduser("~"), ".claude", "projects"))
    if not norm.startswith(claude_dir + os.sep):
        return False
    # only allow paths under a memory/ subdirectory
    rel = norm[len(claude_dir) + 1:]  # strip prefix + separator
    parts = rel.replace(os.sep, "/").split("/")
    # expected: {project-slug}/memory/... or {project-slug}/memory
    return len(parts) >= 2 and parts[1] == "memory"


def is_sensitive(path: str) -> bool:
    """Check if a path touches sensitive locations."""
    for pattern in SENSITIVE_PATTERNS:
        if pattern.search(path):
            return True
    return False


def split_compound(command: str) -> list[str]:
    """Split a compound shell command into individual segments for checking.

    Splits on && || and ; but NOT on | (piping is common for safe read ops).
    """
    parts = re.split(r'\s*(?:&&|\|\||\;)\s*', command)
    return [p.strip() for p in parts if p.strip()]


def get_protected_paths() -> list[str]:
    """Paths that are always blocked for Edit/Write -- autopilot infrastructure files.

    Protects the guard script itself and the settings files that configure it.
    Belt-and-suspenders: the guard script lives outside AUTOPILOT_ROOT by design,
    but we protect it anyway in case someone moves it or uses a broad root.
    """
    guard_script = os.path.abspath(__file__)
    paths = [normalize_path(guard_script)]
    if AUTOPILOT_ROOT:
        claude_dir = os.path.join(AUTOPILOT_ROOT, ".claude")
        paths.extend([
            normalize_path(os.path.join(claude_dir, "settings.local.json")),
            normalize_path(os.path.join(claude_dir, "settings.json")),
            normalize_path(os.path.join(claude_dir, "settings.local.json.autopilot-backup")),
        ])
    return paths


def extract_paths_from_command(command: str) -> list[str]:
    """Best-effort extraction of file paths from a shell command.

    Not foolproof -- compound commands and variable expansion can bypass this.
    The goal is to catch obvious directory escapes, not be a sandbox.
    """
    paths = []

    # look for cd targets
    cd_matches = re.findall(r'\bcd\s+("([^"]+)"|\'([^\']+)\'|(\S+))', command)
    for match in cd_matches:
        target = match[1] or match[2] or match[3]
        if target:
            paths.append(target)

    # look for absolute paths (windows or unix style)
    abs_paths = re.findall(r'(?:^|\s)([A-Za-z]:\\[^\s"\'|&;]+|/[a-zA-Z]/[^\s"\'|&;]+|/(?:etc|home|root|tmp|var|usr|opt)/[^\s"\'|&;]*)', command)
    paths.extend(abs_paths)

    # look for ~ home references
    home_refs = re.findall(r'(?:^|\s)(~[^\s"\'|&;]*)', command)
    for ref in home_refs:
        expanded = os.path.expanduser(ref)
        paths.append(expanded)

    return paths


# ---------------------------------------------------------------------------
# TOOL CHECKS
# ---------------------------------------------------------------------------

def check_bash(command: str):
    """Validate a Bash tool call."""
    # split compound commands and check each segment independently
    segments = split_compound(command)
    if len(segments) > 1:
        for segment in segments:
            check_bash(segment)
        return

    # check dangerous patterns first
    for pattern, description in DANGEROUS_BASH:
        if pattern.search(command):
            block(f"dangerous command pattern: {description}")

    # git: allow only known reads, block everything else
    if re.match(r"^\s*git\s", command):
        if GIT_READ_COMMANDS.search(command):
            return  # explicitly allowed read operation
        parts = command.split()
        subcmd = parts[1] if len(parts) > 1 else "unknown"
        block(f"git operation not on the read allowlist: {subcmd}")

    # directory escape detection
    paths = extract_paths_from_command(command)
    for path in paths:
        if is_sensitive(path):
            block(f"access to sensitive path: {path}")
        if not is_under_root(path) and not is_claude_memory_path(path):
            block(f"path outside autopilot root: {path}")


def check_file_tool(file_path: str, tool_name: str):
    """Validate a Read, Edit, or Write tool call."""
    # block edits to autopilot infrastructure files (self-modification escape)
    if tool_name in ("Edit", "Write"):
        norm = normalize_path(file_path)
        for protected in get_protected_paths():
            if norm == protected:
                block(f"{tool_name} blocked: {file_path} is a protected autopilot infrastructure file")
    if is_sensitive(file_path):
        block(f"{tool_name} blocked: sensitive path {file_path}")
    if not is_under_root(file_path) and not is_claude_memory_path(file_path):
        block(f"{tool_name} blocked: {file_path} is outside autopilot root ({AUTOPILOT_ROOT})")


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    if not AUTOPILOT_ROOT:
        # not an autopilot session -- nothing to guard, allow through
        sys.exit(0)

    try:
        data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        block("could not parse hook input -- failing closed")

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    if tool_name == "Bash":
        command = tool_input.get("command", "")
        check_bash(command)

    elif tool_name in ("Read", "Edit", "Write"):
        file_path = tool_input.get("file_path", "")
        if file_path:
            check_file_tool(file_path, tool_name)

    # tool not in our checklist -- allow it through
    sys.exit(0)


if __name__ == "__main__":
    main()
