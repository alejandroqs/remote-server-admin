#!/bin/bash

# ==============================================================================
# SYNOPSIS
#    Sets up the AI Agents environment (SSOT - Single Source of Truth).
#
# DESCRIPTION
#    1. Checks if AGENTS.md and the skills/ folder exist in the root.
#       If not, creates them.
#    2. Links popular agent configuration files (Cursor, Cline, Copilot, etc.)
#       to these central resources using symbolic links.
#
# USAGE
#    Run from the project root: ./setup-agent-links.sh
# ==============================================================================

# --- CONFIGURATION ---
CENTRAL_CONTEXT_FILE="AGENTS.md"
CENTRAL_SKILLS_FOLDER="skills"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color

# --- FUNCTIONS ---

# Function to create a symbolic link
# Arguments: $1 = Target (Source), $2 = Link Name (Destination)
create_symlink() {
    local target=$1
    local link=$2

    # Check if destination exists
    if [ -e "$link" ] || [ -L "$link" ]; then
        echo -e " ${YELLOW}[!] Destination already exists: $link (Skipping)${NC}"
        return
    fi

    # Check if parent directory needs to be created
    local parent_dir
    parent_dir=$(dirname "$link")
    
    if [ ! -d "$parent_dir" ]; then
        mkdir -p "$parent_dir"
        echo -e " ${CYAN}[+] Parent directory created: $parent_dir${NC}"
    fi

    # Create the symlink
    # We use absolute paths ($PWD) for the target to ensure links inside folders 
    # (like .github/) point correctly to the root file.
    ln -s "$PWD/$target" "$link"

    if [ $? -eq 0 ]; then
        echo -e " ${GREEN}[OK] Link created: $link -> $target${NC}"
    else
        echo -e " ${RED}[X] Error creating link $link.${NC}"
    fi
}

# --- EXECUTION ---

echo -e "${CYAN}=== Starting AI Agents Context Setup ===${NC}"

# 1. AUTO-CREATION: Verify and create base resources if missing
echo -e "\n${CYAN}Verifying base resources (SSOT)...${NC}"

if [ ! -f "$CENTRAL_CONTEXT_FILE" ]; then
    touch "$CENTRAL_CONTEXT_FILE"
    echo -e " ${GREEN}[+] File '$CENTRAL_CONTEXT_FILE' did not exist. Created (empty).${NC}"
else
    echo -e " ${GRAY}[v] File '$CENTRAL_CONTEXT_FILE' found.${NC}"
fi

if [ ! -d "$CENTRAL_SKILLS_FOLDER" ]; then
    mkdir -p "$CENTRAL_SKILLS_FOLDER"
    echo -e " ${GREEN}[+] Folder '$CENTRAL_SKILLS_FOLDER' did not exist. Created (empty).${NC}"
else
    echo -e " ${GRAY}[v] Folder '$CENTRAL_SKILLS_FOLDER' found.${NC}"
fi

# 2. LINKS: Iterate through agents
echo -e "\n${CYAN}Creating links for Agents...${NC}"

# --- Cursor AI ---
echo -e "${GRAY}Processing: Cursor AI${NC}"
create_symlink "$CENTRAL_CONTEXT_FILE" ".cursorrules"

# --- Roo Code (Cline) ---
echo -e "${GRAY}Processing: Roo Code (Cline)${NC}"
create_symlink "$CENTRAL_CONTEXT_FILE" ".clinerules"

# --- Windsurf ---
echo -e "${GRAY}Processing: Windsurf${NC}"
create_symlink "$CENTRAL_CONTEXT_FILE" ".windsurfrules"

# --- GitHub Copilot ---
echo -e "${GRAY}Processing: GitHub Copilot${NC}"
create_symlink "$CENTRAL_CONTEXT_FILE" ".github/copilot-instructions.md"

# --- Gemini (Custom) ---
echo -e "${GRAY}Processing: Gemini (Custom)${NC}"
create_symlink "$CENTRAL_CONTEXT_FILE" "GEMINI.md"
create_symlink "$CENTRAL_SKILLS_FOLDER" ".gemini/skills"

# --- OpenAI (Custom) ---
echo -e "${GRAY}Processing: OpenAI (Custom)${NC}"
create_symlink "$CENTRAL_SKILLS_FOLDER" ".openai/skills"

echo -e "\n${CYAN}=== Setup Completed ===${NC}"
echo -e "${GRAY}Note: If using Git, remember to add generated symlinks or folders to .gitignore.${NC}"