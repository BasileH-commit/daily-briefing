# Setup Checklist for Smily Daily Briefing

Complete these steps to get your daily briefing running:

## ✅ Step 1: Get API Credentials

### Jira API Token
- [ ] Go to https://id.atlassian.com/manage-profile/security/api-tokens
- [ ] Click "Create API token"
- [ ] Name it "Daily Briefing Bot"
- [ ] Copy the token (save securely)

### Slack Bot Token
- [ ] Go to https://api.slack.com/apps
- [ ] Create app or use existing
- [ ] Add these OAuth scopes:
  - [ ] `channels:history`
  - [ ] `groups:history`
  - [ ] `chat:write`
  - [ ] `conversations:read`
- [ ] Install app to workspace
- [ ] Copy "Bot User OAuth Token" (starts with `xoxb-`)

### Anthropic API Key
- [ ] Go to https://console.anthropic.com/
- [ ] Create API key
- [ ] Copy it

---

## ✅ Step 2: Create GitHub Repository

- [ ] Create new repo on GitHub (can be private)
- [ ] Name it `smily-briefing` or similar
- [ ] Don't initialize with README (we already have one)

### Push code to GitHub:
```bash
cd /Users/basilehamon/smily-briefing
git remote add origin https://github.com/YOUR_USERNAME/smily-briefing.git
git push -u origin main
```

---

## ✅ Step 3: Add GitHub Secrets

In your GitHub repo:
- [ ] Go to **Settings** → **Secrets and variables** → **Actions**
- [ ] Click **New repository secret**

Add these 4 secrets:

- [ ] `ANTHROPIC_API_KEY` = (your Anthropic key)
- [ ] `JIRA_API_TOKEN` = (your Jira token)
- [ ] `JIRA_EMAIL` = `basile.hamon@smily.com`
- [ ] `SLACK_BOT_TOKEN` = (your Slack token starting with xoxb-)

---

## ✅ Step 4: Invite Slack Bot to Channels

The bot **auto-discovers** channels it's invited to. Just invite it:

In each Slack channel you want monitored:
- [ ] Type: `/invite @yourbotname`

**Suggested channels:**
- [ ] `#channel-airbnb`
- [ ] `#channel-bookingcom`
- [ ] `#channel-dev`
- [ ] (any other channels you want in briefing)

**Note:** You DON'T need to configure channel IDs manually!

---

## ✅ Step 5: Test It!

### Option A: Test Locally First (Recommended)

```bash
cd /Users/basilehamon/smily-briefing

# Set environment variables (replace with your real values)
export ANTHROPIC_API_KEY="sk-ant-..."
export JIRA_API_TOKEN="your-jira-token"
export JIRA_EMAIL="basile.hamon@smily.com"
export SLACK_BOT_TOKEN="xoxb-..."

# Run the script
python briefing.py
```

**Expected output:**
- ✅ Finds channels bot is in
- ✅ Fetches Jira tickets
- ✅ Fetches Slack messages
- ✅ Generates briefing with Claude
- ✅ Posts to Slack channel C0B0HFGJXC5

### Option B: Test via GitHub Actions

- [ ] Go to GitHub repo → **Actions** tab
- [ ] Select "Daily PM Briefing" workflow
- [ ] Click **Run workflow** → **Run workflow**
- [ ] Check logs for errors
- [ ] Check Slack channel for the briefing

---

## ✅ Step 6: Verify Schedule

The briefing runs automatically:
- **Time:** 7:00 AM UTC = 9:00 AM Paris (winter) / 10:00 AM (summer)
- **Days:** Monday - Friday only
- **Where:** GitHub Actions tab

- [ ] Check GitHub Actions for scheduled runs
- [ ] Wait for first automated run tomorrow morning

---

## 🎉 You're Done!

Your daily briefing will now run every weekday morning automatically.

### Next Morning

Check Slack channel `C0B0HFGJXC5` around 9-10 AM Paris time for:

```
📬 Daily briefing — Monday, April 28, 2026

🆕 New tickets to triage
• [CMA-123] Add Airbnb sync retry logic
  Created: Apr 27 16:30 by Greg | Assignee: Unassigned | Priority: High

💬 Tickets where you were mentioned
• [CMB-456] Booking.com API rate limit issue
  Status: In Analysis | Assignee: Basile | Last update: Apr 27 18:22

🔴 Blockers / urgent signals from Slack
• Nothing to report

📋 Suggested focus for today
• Triage new high-priority Airbnb sync ticket
• Follow up on Booking.com API rate limit analysis
```

---

## Troubleshooting

**"No channels found"**
→ Invite bot to channels with `/invite @botname`

**"Jira authentication failed"**
→ Check JIRA_EMAIL and JIRA_API_TOKEN secrets

**"Slack post failed"**
→ Check SLACK_BOT_TOKEN and bot has `chat:write` scope

**Briefing not arriving**
→ Check GitHub Actions logs for errors

---

## Need Help?

- Check `README.md` for detailed documentation
- Review GitHub Actions logs for error messages
- Test locally first to debug API issues
