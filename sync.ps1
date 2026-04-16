# sync.ps1 -- commit and push any changes in ~/.claude to GitHub
# Run via Windows Task Scheduler

$repoPath = "$env:USERPROFILE\.claude"

Set-Location $repoPath

# check for changes
$status = git status --porcelain
if (-not $status) {
    exit 0  # nothing to do
}

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
git add skills/ hooks/ settings.json statusline-command.sh .gitignore sync.ps1
git diff --cached --quiet
if ($LASTEXITCODE -ne 0) {
    git commit -m "auto-sync $timestamp"
    git push
}
