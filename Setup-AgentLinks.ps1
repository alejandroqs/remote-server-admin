<#
.SYNOPSIS
    Sets up the AI Agents environment (SSOT - Single Source of Truth).
.DESCRIPTION
    1. Checks if AGENTS.md and the skills/ folder exist in the root. If not, creates them.
    2. Links popular agent configuration files (Cursor, Cline, Copilot, etc.)
       to these central resources.
    Requires Administrator privileges to create Symlinks.
#>

# --- CONFIGURATION ---
$CentralContextFile = "AGENTS.md"
$CentralSkillsFolder = "skills"

# Agent Map: Name -> Configuration
# 'RuleFile': The filename/link the agent looks for (e.g., .cursorrules)
# 'SkillPath': (Optional) Path where the agent looks for tools/skills
$Agents = @{
    "Cursor AI" = @{
        RuleFile = ".cursorrules"
    }
    "Roo Code (Cline)" = @{
        RuleFile = ".clinerules"
    }
    "Windsurf" = @{
        RuleFile = ".windsurfrules"
    }
    "GitHub Copilot" = @{
        RuleFile = ".github\copilot-instructions.md"
    }
    "Gemini (Custom)" = @{
        RuleFile = "GEMINI.md"
        SkillPath = ".gemini\skills"
    }
    "OpenAI (Custom)" = @{
        SkillPath = ".openai\skills"
    }
}

# --- FUNCTIONS ---

function New-SymLink {
    param (
        [string]$Target, # The actual file/folder (Source)
        [string]$Link    # The link name (Destination)
    )

    # Check if the destination link/file already exists
    if (Test-Path -Path $Link) {
        Write-Host " [!] Destination already exists: $Link (Skipping)" -ForegroundColor Yellow
        return
    }

    # Check if the destination requires a parent folder (e.g., .github/copilot...)
    $ParentDir = Split-Path -Path $Link -Parent
    if (-not [string]::IsNullOrEmpty($ParentDir)) {
        if (-not (Test-Path $ParentDir)) {
            New-Item -ItemType Directory -Path $ParentDir | Out-Null
            Write-Host " [+] Parent directory created: $ParentDir" -ForegroundColor Cyan
        }
    }

    try {
        New-Item -ItemType SymbolicLink -Path $Link -Target $Target | Out-Null
        Write-Host " [OK] Link created: $Link -> $Target" -ForegroundColor Green
    }
    catch {
        Write-Host " [X] Error creating link $Link. Do you have Administrator privileges?" -ForegroundColor Red
        Write-Host "     Detail: $_" -ForegroundColor DarkGray
    }
}

# --- EXECUTION ---

Write-Host "=== Starting AI Agents Context Setup ===" -ForegroundColor Magenta

# 1. AUTO-CREATION: Verify and create base resources if missing
Write-Host "`nVerifying base resources (SSOT)..." -ForegroundColor Cyan

if (-not (Test-Path $CentralContextFile)) {
    try {
        New-Item -ItemType File -Path $CentralContextFile | Out-Null
        Write-Host " [+] File '$CentralContextFile' did not exist. Created (empty)." -ForegroundColor Green
    }
    catch {
        Write-Error "Could not create $CentralContextFile. Check permissions."
        exit
    }
} else {
    Write-Host " [v] File '$CentralContextFile' found." -ForegroundColor Gray
}

if (-not (Test-Path $CentralSkillsFolder)) {
    try {
        New-Item -ItemType Directory -Path $CentralSkillsFolder | Out-Null
        Write-Host " [+] Folder '$CentralSkillsFolder' did not exist. Created (empty)." -ForegroundColor Green
    }
    catch {
        Write-Error "Could not create folder $CentralSkillsFolder. Check permissions."
        exit
    }
} else {
    Write-Host " [v] Folder '$CentralSkillsFolder' found." -ForegroundColor Gray
}

# 2. LINKS: Iterate through each agent and create symlinks
Write-Host "`nCreating links for Agents..." -ForegroundColor Cyan

foreach ($AgentName in $Agents.Keys) {
    Write-Host "Processing: $AgentName" -ForegroundColor DarkCyan
    $Config = $Agents[$AgentName]

    # A. Rules/Instructions Link (Context)
    if ($Config.ContainsKey("RuleFile")) {
        New-SymLink -Target (Resolve-Path $CentralContextFile).Path -Link $Config.RuleFile
    }

    # B. Skills/Tools Link
    if ($Config.ContainsKey("SkillPath")) {
        # Resolve-Path ensures the symlink points to the correct absolute path
        New-SymLink -Target (Resolve-Path $CentralSkillsFolder).Path -Link $Config.SkillPath
    }
}

Write-Host "`n=== Setup Completed ===" -ForegroundColor Magenta
Write-Host "Note: If using Git, remember to add generated symlinks or folders to .gitignore to avoid duplication." -ForegroundColor Gray