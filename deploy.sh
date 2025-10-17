#!/bin/bash

# Kenya SHIF Analyzer - Production Deployment Script
# Deploys to Streamlit Cloud and optional Vercel dashboard

set -e

echo "🚀 Kenya SHIF Healthcare Policy Analyzer - Deployment Script"
echo "==========================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "\n${YELLOW}Checking prerequisites...${NC}"

if ! command -v git &> /dev/null; then
    echo -e "${RED}Git not found. Please install Git.${NC}"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 not found. Please install Python 3.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Git found${NC}"
echo -e "${GREEN}✓ Python found${NC}"

# Verify key files exist
echo -e "\n${YELLOW}Verifying deployment files...${NC}"

required_files=(
    "streamlit_comprehensive_analyzer.py"
    "integrated_comprehensive_analyzer.py"
    "requirements.txt"
    "README.md"
    ".env.example"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓ $file${NC}"
    else
        echo -e "${RED}✗ $file not found${NC}"
        exit 1
    fi
done

# Create .streamlit directory if not exists
if [ ! -d ".streamlit" ]; then
    echo -e "\n${YELLOW}Creating .streamlit configuration...${NC}"
    mkdir -p .streamlit
    echo -e "${GREEN}✓ .streamlit directory created${NC}"
fi

# Verify git status
echo -e "\n${YELLOW}Checking Git status...${NC}"
git status

# Commit and push
echo -e "\n${YELLOW}Preparing for deployment...${NC}"

if [ -z "$(git status --porcelain)" ]; then
    echo -e "${GREEN}✓ Working directory clean${NC}"
else
    echo -e "${YELLOW}Found uncommitted changes. Committing...${NC}"
    git add -A
    git commit -m "deploy: Complete deployment configuration for Streamlit and Vercel" || true
fi

echo -e "\n${YELLOW}Pushing to GitHub...${NC}"
git push origin main

echo -e "\n${GREEN}✓ Git push complete${NC}"

# Deployment instructions
echo -e "\n${GREEN}==========================================================="
echo -e "Deployment Ready! Next Steps:"
echo -e "===========================================================${NC}"

echo -e "\n${YELLOW}1. STREAMLIT CLOUD (Recommended):${NC}"
echo -e "   - Go to: https://streamlit.io/cloud"
echo -e "   - Sign in with GitHub (pranaysuyash)"
echo -e "   - New app → Select streamlit_comprehensive_analyzer.py"
echo -e "   - Add OPENAI_API_KEY to Secrets"
echo -e "   - Deploy!"

echo -e "\n${YELLOW}2. VERCEL (Optional Dashboard):${NC}"
echo -e "   - Go to: https://vercel.com"
echo -e "   - Connect GitHub repository"
echo -e "   - Add OPENAI_API_KEY environment variable"
echo -e "   - Deploy!"

echo -e "\n${YELLOW}3. SEND TO ASSIGNMENT GIVER:${NC}"
echo -e "   - Streamlit URL: https://kenya-shif-XXXXX.streamlit.app"
echo -e "   - GitHub Repo: https://github.com/pranaysuyash/kenya-shif"
echo -e "   - Latest Commit: $(git rev-parse --short HEAD)"

echo -e "\n${GREEN}✓ Deployment configuration complete!${NC}\n"
