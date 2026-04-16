# sync.ps1 -- commit and push any changes in ~/.claude to GitHub
# Run via Windows Task Scheduler

$logFile = "$env:USERPROFILE\.claude\sync.log"
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

function Log($msg) {
    "$timestamp  $msg" | Add-Content $logFile
}

try {
    $repoPath = "$env:USERPROFILE\.claude"
    Set-Location $repoPath
    Log "Starting sync from $repoPath"

    # check for changes
    $status = git status --porcelain 2>&1
    if (-not $status) {
        Log "No changes, nothing to do"
        exit 0
    }

    Log "Changes detected: $($status -join ', ')"
    git add skills/ hooks/ settings.json statusline-command.sh .gitignore sync.ps1 2>&1 | ForEach-Object { Log $_ }
    git diff --cached --quiet
    if ($LASTEXITCODE -ne 0) {
        $commitTime = Get-Date -Format "yyyy-MM-dd HH:mm"
        git commit -m "auto-sync $commitTime" 2>&1 | ForEach-Object { Log $_ }
        git push 2>&1 | ForEach-Object { Log $_ }
        Log "Done"
    }
} catch {
    Log "ERROR: $_"
    exit 1
}
