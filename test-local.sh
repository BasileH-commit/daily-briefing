#!/bin/bash
# Local testing script for Smily Briefing

echo "🧪 Testing Smily Briefing Locally"
echo "=================================="
echo ""

# Check if .env file exists
if [ -f ".env" ]; then
    echo "✅ Found .env file"
    echo "   Loading environment variables..."
    echo ""

    # Check if python-dotenv is installed
    if python3 -c "import dotenv" 2>/dev/null; then
        echo "✅ python-dotenv is installed"
    else
        echo "⚠️  python-dotenv not installed"
        echo "   Installing it now..."
        pip install python-dotenv
    fi

    # Modify briefing.py to load .env
    if ! grep -q "from dotenv import load_dotenv" briefing.py; then
        echo "   Adding dotenv support to briefing.py..."
        # Add dotenv import after other imports
        sed -i '' '1a\
from dotenv import load_dotenv\
load_dotenv()
' briefing.py
    fi

    echo ""
    echo "🚀 Running briefing.py..."
    python3 briefing.py

else
    echo "❌ No .env file found"
    echo ""
    echo "Option 1: Create .env file from template"
    echo "  cp .env.example .env"
    echo "  # Then edit .env with your real API tokens"
    echo "  # Then run this script again"
    echo ""
    echo "Option 2: Set environment variables manually"
    echo "  export ANTHROPIC_API_KEY='sk-ant-...'"
    echo "  export JIRA_API_TOKEN='your-token'"
    echo "  export JIRA_EMAIL='basile.hamon@smily.com'"
    echo "  export SLACK_BOT_TOKEN='xoxb-...'"
    echo "  python3 briefing.py"
    echo ""
    exit 1
fi
