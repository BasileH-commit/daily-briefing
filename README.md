# Smily Daily Briefing

Automated daily briefing for Product Management - fetches Jira tickets and Slack messages, generates a concise briefing using Claude AI, and posts to Slack.

## What It Does

Every weekday morning (9 AM Paris time), this script:
1. 📊 Fetches new Jira tickets from CMA/CMB projects
2. 💬 Finds tickets where you were mentioned
3. 🔍 Scans Slack channels the bot is in for recent activity
4. 🤖 Uses Claude AI to synthesize a concise briefing
5. 📬 Posts it to Slack channel `C0B0HFGJXC5`

## Features

- **Auto-discovery**: Automatically includes ALL Slack channels the bot is invited to (no manual configuration!)
- **Smart filtering**: Excludes bot messages, truncates long messages
- **Error handling**: Continues even if individual API calls fail
- **Manual trigger**: Run on-demand via GitHub Actions UI

## Setup Instructions

### 1. Get API Credentials

#### Jira API Token
1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Name it "Daily Briefing Bot"
4. Copy the token (save it securely)

#### Slack Bot Token
1. Go to https://api.slack.com/apps
2. Create new app (from scratch) or use existing
3. Required scopes (OAuth & Permissions):
   - `channels:history` - Read public channel messages
   - `groups:history` - Read private channel messages
   - `chat:write` - Post messages
   - `conversations:read` - List channels
4. Install app to workspace
5. Copy the "Bot User OAuth Token" (starts with `xoxb-`)

#### Anthropic API Key
1. Go to https://console.anthropic.com/
2. Navigate to API Keys
3. Create a new key
4. Copy it

### 2. Add GitHub Secrets

In your GitHub repository:
1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add these 4 secrets:

| Secret Name | Value |
|-------------|-------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key |
| `JIRA_API_TOKEN` | Your Jira API token |
| `JIRA_EMAIL` | `basile.hamon@smily.com` |
| `SLACK_BOT_TOKEN` | Your Slack bot token (xoxb-...) |

### 3. Invite Slack Bot to Channels

For the bot to read channels, it must be invited:

1. Go to each Slack channel you want monitored
2. Type: `/invite @yourbotname`
3. Press Enter

**Example channels to invite to:**
- `#channel-airbnb`
- `#channel-bookingcom`
- `#channel-dev`
- `#team-product`
- Any others you want in the briefing

The script will **automatically discover** all channels the bot is in - no code changes needed!

### 4. Test It

#### Option A: Manual Test Locally
```bash
cd smily-briefing

# Set environment variables
export ANTHROPIC_API_KEY="your-key"
export JIRA_API_TOKEN="your-token"
export JIRA_EMAIL="basile.hamon@smily.com"
export SLACK_BOT_TOKEN="xoxb-your-token"

# Run
python briefing.py
```

#### Option B: Test via GitHub Actions
1. Push this code to GitHub
2. Go to **Actions** tab
3. Select **Daily PM Briefing** workflow
4. Click **Run workflow** → **Run workflow**
5. Watch the logs

### 5. Verify Schedule

The workflow runs automatically:
- **Time**: 7:00 AM UTC = 9:00 AM Paris (winter) / 10:00 AM (summer)
- **Days**: Monday - Friday (weekdays only)
- **Cron**: `0 7 * * 1-5`

Check the Actions tab to see past/upcoming runs.

## Briefing Format

The generated briefing includes:

1. 🆕 **New tickets to triage** - To Do tickets created in last 24h
2. 💬 **Tickets where you were mentioned** - Comments mentioning "Basile"
3. 🔴 **Blockers / urgent signals from Slack** - Critical discussions
4. 📋 **Suggested focus for today** - Top 2-3 priorities

Max 30 lines, bullet points only.

## Troubleshooting

### "No channels found"
→ Make sure bot is invited to channels with `/invite @botname`

### "Slack API error: not_in_channel"
→ Bot needs to be invited to that specific channel

### "Jira authentication failed"
→ Check JIRA_EMAIL and JIRA_API_TOKEN are correct

### "Claude API failed"
→ Check ANTHROPIC_API_KEY is valid and has credits

### Briefing not posting
→ Check SLACK_BOT_TOKEN and that bot has `chat:write` scope

## Files

```
smily-briefing/
├── briefing.py                    # Main script
├── requirements.txt               # Python dependencies
├── .github/
│   └── workflows/
│       └── daily-briefing.yml    # GitHub Actions schedule
└── README.md                      # This file
```

## Modifying the Briefing

### Change output channel
Edit `briefing.py`, line 13:
```python
SLACK_OUTPUT_CHANNEL = "C0B0HFGJXC5"  # Change this
```

### Change schedule
Edit `.github/workflows/daily-briefing.yml`, line 5:
```yaml
- cron: '0 7 * * 1-5'  # Modify this
```

Cron format: `minute hour day month day-of-week`

### Add more Jira projects
Edit `briefing.py`, modify the JQL queries (lines ~35, ~95):
```python
jql_new = 'project in (CMA, CMB, NEWPROJECT) AND ...'
```

### Customize briefing format
Edit the prompt in `generate_briefing()` function (line ~217)

## License

Internal Smily tool - not for public distribution.

## Support

Contact: Basile Hamon (basile.hamon@smily.com)
