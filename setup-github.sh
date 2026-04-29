#!/bin/bash
# Setup script to create GitHub repo and push code

echo "🚀 Smily Briefing - GitHub Setup"
echo "================================"
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed."
    echo ""
    echo "Install it with:"
    echo "  brew install gh"
    echo ""
    echo "Or follow manual setup below:"
    echo "1. Go to https://github.com/new"
    echo "2. Repository name: smily-briefing"
    echo "3. Description: Daily PM briefing - Jira + Slack + Claude AI"
    echo "4. Private repository: ✅ (recommended)"
    echo "5. Do NOT initialize with README (we have one)"
    echo "6. Click 'Create repository'"
    echo ""
    echo "Then run these commands:"
    echo "  cd /Users/basilehamon/smily-briefing"
    echo "  git remote add origin https://github.com/YOUR_USERNAME/smily-briefing.git"
    echo "  git push -u origin main"
    exit 1
fi

echo "✅ GitHub CLI found!"
echo ""

# Login check
if ! gh auth status &> /dev/null; then
    echo "🔐 Not logged into GitHub. Logging in..."
    gh auth login
fi

echo ""
echo "📦 Creating GitHub repository..."
gh repo create smily-briefing \
    --private \
    --description "Daily PM briefing - Jira + Slack + Claude AI" \
    --source=. \
    --push

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Repository created and code pushed!"
    echo ""
    echo "📍 Next steps:"
    echo "1. Get your API tokens (see SETUP_CHECKLIST.md)"
    echo "2. Add them as GitHub secrets:"
    echo "   https://github.com/$(gh repo view --json owner,name -q '.owner.login + "/" + .name')/settings/secrets/actions"
    echo ""
    echo "3. Add these 4 secrets:"
    echo "   - ANTHROPIC_API_KEY"
    echo "   - JIRA_API_TOKEN"
    echo "   - JIRA_EMAIL (basile.hamon@smily.com)"
    echo "   - SLACK_BOT_TOKEN"
    echo ""
    echo "4. Test the workflow:"
    echo "   https://github.com/$(gh repo view --json owner,name -q '.owner.login + "/" + .name')/actions"
else
    echo ""
    echo "❌ Failed to create repository."
    echo "You can create it manually:"
    echo "1. Go to https://github.com/new"
    echo "2. Name: smily-briefing"
    echo "3. Private: ✅"
    echo "4. Create, then run:"
    echo "   git remote add origin https://github.com/YOUR_USERNAME/smily-briefing.git"
    echo "   git push -u origin main"
fi
