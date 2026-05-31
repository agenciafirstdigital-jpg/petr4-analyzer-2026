Set-Location "C:\Users\Felipe\Downloads\Claudinho\Teste 1"

$status = git status --porcelain 2>&1
if (-not $status) { exit 0 }

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
git add app.py data.py analysis.py charts.py requirements.txt CLAUDE.md .gitignore 2>&1 | Out-Null
git add ".claude/settings.json" 2>&1 | Out-Null

$staged = git diff --cached --name-only 2>&1
if (-not $staged) { exit 0 }

git commit -m "chore: auto-update $timestamp" 2>&1 | Out-Null
git push origin main 2>&1 | Out-Null
