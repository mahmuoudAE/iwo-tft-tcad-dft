<#
.SYNOPSIS
  One step of the Claude <-> Codex relay for one task, then stop. Never pushes.

.DESCRIPTION
  own     : the owner does the task and writes a handoff                     -> 1 commit
  review  : the other agent writes an independent assessment, then verdicts  -> 2 commits
  respond : the owner answers the review                                     -> 1 commit
  full    : own -> review -> respond, then stop
  After each agent run the relay undoes any commit the agent made itself, reverts every file outside the agent's
  area, checks that the public repository was not touched, and commits with the agent named in the message.
  Prompts are built from prompts/relay/*.md; prompts, final answers and a run summary are kept in relay_logs/<run>/.

.EXAMPLE
  pwsh -ExecutionPolicy Bypass -File tools\relay.ps1 -Task RQ-001 -Owner claude -Step own -DryRun
.EXAMPLE
  pwsh -ExecutionPolicy Bypass -File tools\relay.ps1 -Task RQ-001 -Owner claude -Step full
#>
[CmdletBinding()]
param(
  [Parameter(Mandatory)][ValidatePattern('^[A-Z]+-\d{3}$')][string]$Task,
  [Parameter(Mandatory)][ValidateSet('claude', 'codex')][string]$Owner,
  [Parameter(Mandatory)][ValidateSet('own', 'review', 'respond', 'full')][string]$Step,
  [switch]$DryRun,             # print the prompts and commands; run nothing, change nothing
  [switch]$CodexInWsl,         # run Codex inside WSL "Ubuntu" instead of Windows
  [string]$CodexProfile = '',  # a profile from %USERPROFILE%\.codex\config.toml, e.g. 'review'
  [int]$ClaudeMaxTurns = 80,
  [switch]$FakeAgent           # TEST ONLY: each agent is replaced by a stub that writes one allowed and one forbidden file
)
Set-StrictMode -Version 3.0
$ErrorActionPreference = 'Stop'

$Repo    = Split-Path -Parent $PSScriptRoot
$Public  = Join-Path (Split-Path -Parent $Repo) 'IWO_PHYSICS_CONSTRAINED_MODEL_V1'
$RunId   = '{0}_{1}_{2}' -f (Get-Date -Format 'yyyyMMdd_HHmmss'), $Task, $Step
$RunDir  = Join-Path $Repo "relay_logs\$RunId"
$Other   = @{ claude = 'codex'; codex = 'claude' }
$Summary = [System.Collections.Generic.List[string]]::new()
$script:LastCommit = ''

# Where each agent may write (repo-relative, forward slashes). Everything else it touches is reverted.
$Allowed = @{
  claude = @('^claude/', '^handoffs/CLAUDE_TO_CODEX\.md$', '^predictions/(registered|revealed)/', '^data_private/derived/',
             '^01_CURRENT_STATE\.md$', '^02_RESEARCH_QUESTIONS\.md$', '^03_CLAIMS_LEDGER\.yaml$', '^04_TASK_QUEUE\.yaml$')
  codex  = @('^codex/', '^handoffs/CODEX_TO_CLAUDE\.md$')
}
$AllowedText = @{
  claude = 'claude/, handoffs/CLAUDE_TO_CODEX.md, predictions/, data_private/derived/, 01_CURRENT_STATE.md, 02_RESEARCH_QUESTIONS.md, 03_CLAIMS_LEDGER.yaml, 04_TASK_QUEUE.yaml'
  codex  = 'codex/ and handoffs/CODEX_TO_CLAUDE.md'
}
$ReviewDir    = @{ claude = 'claude/reviews/'; codex = 'codex/independent_reviews/' }
$ResponseFile = @{ claude = "claude/responses_to_codex/${Task}_response.md"; codex = "codex/responses_to_claude/${Task}_response.md" }
$HandoffOut   = @{ claude = 'handoffs/CLAUDE_TO_CODEX.md'; codex = 'handoffs/CODEX_TO_CLAUDE.md' }

function Say([string]$m) { Write-Host "[relay] $m"; $Summary.Add($m) }

# ------------------------------------------------------------ git: Git for Windows if installed, else WSL "Ubuntu"
$NativeGit = [bool](Get-Command git -ErrorAction SilentlyContinue)
function ConvertTo-WslPath([string]$p) { '/mnt/' + $p.Substring(0, 1).ToLower() + ($p.Substring(2) -replace '\\', '/') }
function GitPath([string]$p) { if ($NativeGit) { $p } else { ConvertTo-WslPath $p } }
function Invoke-Git([string]$Dir, [string[]]$GitArgs) {
  if ($NativeGit) { $out = & git -C $Dir @GitArgs 2>$null }
  else { $out = & wsl -d Ubuntu -- git -C (ConvertTo-WslPath $Dir) @GitArgs 2>$null }
  if ($LASTEXITCODE -ne 0) { throw "git $($GitArgs -join ' ') failed in $Dir (exit $LASTEXITCODE)" }
  return , @($out)   # the comma keeps a one-line result an array (otherwise [0] would return its first character)
}
function Get-ChangedPaths {
  foreach ($l in (Invoke-Git $Repo @('status', '--porcelain', '--untracked-files=all'))) {
    if (-not $l) { continue }
    $p = $l.Substring(3)
    if ($p -like '* -> *') { $p = ($p -split ' -> ')[-1] }
    $p.Trim('"')
  }
}
function Get-PublicState {
  if (Test-Path $Public) { (Invoke-Git $Public @('status', '--porcelain', '--untracked-files=all')) -join "`n" } else { '<missing>' }
}

# ------------------------------------------------------------ prompts
function Get-Prompt([string]$Name, [string]$Agent) {
  $o = $Other[$Agent]
  $vars = @{
    TASK = $Task; AGENT = $Agent; OTHER = $o
    INSTR = $(if ($Agent -eq 'claude') { 'CLAUDE.md' } else { 'AGENTS.md' })
    AREA = $(if ($Agent -eq 'claude') { 'claude/evidence/' } else { 'codex/' })
    HANDOFF_OUT = $HandoffOut[$Agent]; HANDOFF_IN = $HandoffOut[$o]
    ALLOWED = $AllowedText[$Agent]
    PUBLIC = $(if ($Agent -eq 'codex' -and $CodexInWsl) { ConvertTo-WslPath $Public } else { $Public })
    MY_REVIEW_DIR = $ReviewDir[$Agent]; OTHER_REVIEW_DIR = $ReviewDir[$o]
    RESPONSE_FILE = $ResponseFile[$Agent]
    PREV_COMMIT = $(if ($script:LastCommit) { $script:LastCommit } else { 'the phase-1 commit' })
    LEDGER_RULE = $(if ($Agent -eq 'claude') { 'Apply accepted ledger status changes in 03_CLAIMS_LEDGER.yaml, each with a history line.' }
                    else { 'Propose ledger status changes in the response; do not edit the ledger.' })
  }
  $t = Get-Content -LiteralPath (Join-Path $Repo "prompts\relay\$Name.md") -Raw
  foreach ($k in $vars.Keys) { $t = $t.Replace('{' + $k + '}', [string]$vars[$k]) }
  if ($t -match '\{[A-Z_]+\}') { throw "unfilled placeholder $($Matches[0]) in prompts/relay/$Name.md" }
  return $t
}

# ------------------------------------------------------------ agents
function Get-Exe([string]$Name) {
  foreach ($n in @("$Name.cmd", $Name)) { $c = Get-Command $n -ErrorAction SilentlyContinue; if ($c) { return $c.Source } }
  throw "'$Name' is not installed or not on PATH (SETUP_AGENTS.md, step 2)."
}
function Test-AgentInstalled([string]$Agent) {
  if ($FakeAgent) { return }
  if ($Agent -eq 'codex' -and $CodexInWsl) {
    & wsl -d Ubuntu -- bash -lc 'command -v codex >/dev/null'
    if ($LASTEXITCODE -ne 0) { throw 'codex is not installed in WSL "Ubuntu" (SETUP_AGENTS.md, troubleshooting).' }
  } else { Get-Exe $Agent | Out-Null }
}

function Invoke-Agent([string]$Agent, [string]$PromptName, [string]$Tag) {
  $prompt     = Get-Prompt $PromptName $Agent
  $promptFile = Join-Path $RunDir "$Tag.prompt.md"
  $finalFile  = Join-Path $RunDir "$Tag.final.md"
  $streamFile = Join-Path $RunDir "$Tag.stream.log"
  if ($Agent -eq 'claude') {
    $cli = @('-p', '--permission-mode', 'acceptEdits', '--allowedTools', 'Read,Grep,Glob,Edit,Write,Bash,PowerShell',
             '--add-dir', $Public, '--max-turns', "$ClaudeMaxTurns", '--output-format', 'text')
    $shown = 'claude ' + ($cli -join ' ')
  } elseif ($CodexInWsl) {
    $cli = @('-d', 'Ubuntu', '--', 'codex', 'exec', '--sandbox', 'workspace-write', '--cd', (ConvertTo-WslPath $Repo),
             '--output-last-message', (ConvertTo-WslPath $finalFile))
    if ($CodexProfile) { $cli += @('--profile', $CodexProfile) }
    $cli += '-'
    $shown = 'wsl ' + ($cli -join ' ')
  } else {
    $cli = @('exec', '--sandbox', 'workspace-write', '--cd', $Repo, '--output-last-message', $finalFile)
    if ($CodexProfile) { $cli += @('--profile', $CodexProfile) }
    $cli += '-'
    $shown = 'codex ' + ($cli -join ' ')
  }
  if ($DryRun) {
    Write-Host "`n===== $Tag : $Agent ====="
    Write-Host "$shown   (prompt below goes on stdin)"
    Write-Host '----- prompt -----'
    Write-Host $prompt
    return $true
  }
  New-Item -ItemType Directory -Force $RunDir | Out-Null
  Set-Content -LiteralPath $promptFile -Value $prompt -Encoding utf8
  Say "$Tag : running $Agent"
  $t0 = Get-Date
  if ($FakeAgent) {
    $area = if ($Agent -eq 'claude') { 'claude/evidence' } else { 'codex' }
    New-Item -ItemType Directory -Force (Join-Path $Repo "$area/$Task") | Out-Null
    Set-Content -LiteralPath (Join-Path $Repo "$area/$Task/fake_$Tag.md") -Value "fake output of $Agent for $Tag" -Encoding utf8
    Set-Content -LiteralPath (Join-Path $Repo '05_DECISION_LOG.md') -Value 'forbidden edit' -Encoding utf8
    Set-Content -LiteralPath $finalFile -Value "fake final answer ($Agent, $Tag)" -Encoding utf8
    $code = 0
  } elseif ($Agent -eq 'claude') {
    Push-Location $Repo
    try { $prompt | & (Get-Exe 'claude') @cli 1> $finalFile 2> $streamFile; $code = $LASTEXITCODE } finally { Pop-Location }
  } elseif ($CodexInWsl) {
    $prompt | & wsl @cli *> $streamFile; $code = $LASTEXITCODE
  } else {
    $prompt | & (Get-Exe 'codex') @cli *> $streamFile; $code = $LASTEXITCODE
  }
  Say ("$Tag : $Agent finished in {0:N1} min (exit code $code)" -f ((Get-Date) - $t0).TotalMinutes)
  return ($code -eq 0)
}

# ------------------------------------------------------------ check, revert, commit
function Complete-Step([string]$Agent, [string]$Tag, [string]$HeadBefore, [bool]$AgentOk) {
  if ($DryRun) { return $true }
  $head = (Invoke-Git $Repo @('rev-parse', 'HEAD'))[0]
  if ($head -ne $HeadBefore) {
    Invoke-Git $Repo @('reset', '--soft', $HeadBefore) | Out-Null
    Say "$Tag : $Agent committed by itself; its commit(s) were undone and the changes kept for checking"
  }
  Invoke-Git $Repo @('reset', '-q') | Out-Null
  $reverted = @()
  foreach ($p in @(Get-ChangedPaths)) {
    if ($p -match '^relay_logs/') { continue }
    if (@($Allowed[$Agent] | Where-Object { $p -match $_ }).Count -gt 0) { continue }
    $tracked = $true
    try { Invoke-Git $Repo @('ls-files', '--error-unmatch', '--', $p) | Out-Null } catch { $tracked = $false }
    if ($tracked) { Invoke-Git $Repo @('checkout', '--', $p) | Out-Null }
    else { Remove-Item -LiteralPath (Join-Path $Repo $p) -Force -Recurse }
    $reverted += $p
  }
  if ($reverted) { Say "$Tag : reverted $($reverted.Count) path(s) outside the $Agent area: $($reverted -join ', ')" }
  if ((Get-PublicState) -ne $script:PublicBefore) {
    Say "$Tag : STOP - the public repository changed during this step; inspect it with git status before anything else"
    return $false
  }
  if (-not $AgentOk) {
    Say "$Tag : STOP - $Agent failed; its allowed changes are left uncommitted for you to inspect (relay_logs/$RunId)"
    return $false
  }
  Invoke-Git $Repo @('add', '-A') | Out-Null
  if (-not ((Invoke-Git $Repo @('diff', '--cached', '--name-only')) -join '')) { Say "$Tag : $Agent changed nothing"; return $false }
  $trailer = if ($Agent -eq 'claude') { 'Co-Authored-By: Claude <noreply@anthropic.com>' } else { 'Agent: Codex' }
  $rev = if ($reverted) { $reverted -join ', ' } else { 'none' }
  $msg = "$Task ${Tag}: $Agent (relay)`n`nRun log: relay_logs/$RunId`nReverted outside the agent's area: $rev`n`n$trailer`n"
  $msgFile = [System.IO.Path]::GetTempFileName()
  [System.IO.File]::WriteAllText($msgFile, $msg)
  try { Invoke-Git $Repo @('-c', "user.name=$script:AuthorName", '-c', "user.email=$script:AuthorEmail", 'commit', '-q', '-F', (GitPath $msgFile)) | Out-Null }
  finally { Remove-Item -LiteralPath $msgFile -Force }
  $script:LastCommit = (Invoke-Git $Repo @('rev-parse', '--short', 'HEAD'))[0]
  Say "$Tag : committed $script:LastCommit"
  return $true
}

function Invoke-RelayStep([string]$Agent, [string]$PromptName, [string]$Tag) {
  $before = if ($DryRun) { '' } else { (Invoke-Git $Repo @('rev-parse', 'HEAD'))[0] }
  $ok = Invoke-Agent $Agent $PromptName $Tag
  return (Complete-Step $Agent $Tag $before $ok)
}
function Step-Own     { Invoke-RelayStep $Owner 'own' 'own' }
function Step-Review  { (Invoke-RelayStep $Other[$Owner] 'review_a' 'review-a') -and (Invoke-RelayStep $Other[$Owner] 'review_b' 'review-b') }
function Step-Respond { Invoke-RelayStep $Owner 'respond' 'respond' }

# ------------------------------------------------------------ preflight
$queue = Join-Path $Repo '04_TASK_QUEUE.yaml'
if (-not (Test-Path $queue)) { throw "not the private research repo: $Repo" }
if (-not (Select-String -LiteralPath $queue -Pattern "task_id:\s*$Task\b" -Quiet)) { throw "$Task is not in 04_TASK_QUEUE.yaml" }
if ($Step -in @('review', 'respond')) {
  if (-not (Select-String -LiteralPath (Join-Path $Repo $HandoffOut[$Owner]) -Pattern $Task -SimpleMatch -Quiet)) {
    throw "no handoff for $Task in $($HandoffOut[$Owner]); run -Step own first" }
}
if ($Step -eq 'respond') {
  $rf = Join-Path $Repo ($ReviewDir[$Other[$Owner]] + "${Task}_review.md")
  if (-not (Test-Path -LiteralPath $rf)) { throw "no review found at $rf; run -Step review first" }
}
$need = switch ($Step) { 'own' { @($Owner) } 'review' { @($Other[$Owner]) } 'respond' { @($Owner) } 'full' { @('claude', 'codex') } }
if (-not $DryRun) {
  foreach ($a in $need) { Test-AgentInstalled $a }
  $dirty = @(Get-ChangedPaths)
  if ($dirty.Count) { throw "working tree not clean ($($dirty.Count) changed path(s)); commit or discard them first" }
  if (-not (Test-Path $Public)) { Write-Warning "public repository not found at $Public; the public-repo check compares nothing" }
  $script:AuthorName   = (Invoke-Git $Repo @('log', '-1', '--format=%an'))[0]
  $script:AuthorEmail  = (Invoke-Git $Repo @('log', '-1', '--format=%ae'))[0]
  $script:PublicBefore = Get-PublicState
}
$start = if ($DryRun) { '' } else { (Invoke-Git $Repo @('rev-parse', '--short', 'HEAD'))[0] }

# ------------------------------------------------------------ run
$mode = if ($DryRun) { ' (dry run)' } elseif ($FakeAgent) { ' (FAKE AGENTS - test only)' } else { '' }
Say "task $Task, owner $Owner, reviewer $($Other[$Owner]), step $Step$mode"
$ok = switch ($Step) {
  'own'     { Step-Own }
  'review'  { Step-Review }
  'respond' { Step-Respond }
  'full'    { (Step-Own) -and (Step-Review) -and (Step-Respond) }
}

if (-not $DryRun -and (Test-Path $RunDir)) {
  $text = "# Relay run $RunId`n`n" + (($Summary | ForEach-Object { "- $_" }) -join "`n") + "`n"
  [System.IO.File]::WriteAllText((Join-Path $RunDir 'RUN_SUMMARY.md'), $text)
  if ($ok) {
    Invoke-Git $Repo @('add', '--', "relay_logs/$RunId") | Out-Null
    $msgFile = [System.IO.Path]::GetTempFileName()
    [System.IO.File]::WriteAllText($msgFile, "$Task relay log ($Step)`n`nRun log: relay_logs/$RunId`n")
    try { Invoke-Git $Repo @('-c', "user.name=$script:AuthorName", '-c', "user.email=$script:AuthorEmail", 'commit', '-q', '-F', (GitPath $msgFile)) | Out-Null }
    finally { Remove-Item -LiteralPath $msgFile -Force }
    Write-Host "`n[relay] files changed in this run:"
    foreach ($l in (Invoke-Git $Repo @('diff', '--stat', "$start..HEAD"))) { Write-Host "  $l" }
  }
}
Write-Host ''
if ($DryRun) { Write-Host '[relay] dry run finished: nothing was run or changed.' }
elseif ($ok) { Write-Host '[relay] done. Read the new files, decide, record decisions in 05_DECISION_LOG.md. Nothing was pushed.' }
else { Write-Host "[relay] stopped. See relay_logs/$RunId and 'git status'." }
