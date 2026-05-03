#!/usr/bin/env python3
"""
Smily Daily Briefing
Fetches Jira tickets and Slack messages, generates a briefing via Claude API,
and posts it to Slack.
"""

import os
import requests
from datetime import datetime, timedelta

# Configuration
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
JIRA_BASE_URL = "https://bookingsync.atlassian.net"
JIRA_TOKEN = os.environ["JIRA_API_TOKEN"]
JIRA_EMAIL = os.environ["JIRA_EMAIL"]
SLACK_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_OUTPUT_CHANNEL = "C0B0HFGJXC5"  # Daily briefing channel

BASILE_ACCOUNT_ID = "712020:f167fc0d-062a-4eeb-81e0-033668dce1b4"


def fetch_jira():
    """
    Fetch relevant Jira tickets from CMA and CMB projects.
    Returns formatted string with two sections:
    - New To Do tickets created in last 24h
    - Tickets where Basile was mentioned in comments
    """
    auth = (JIRA_EMAIL, JIRA_TOKEN)
    headers = {"Accept": "application/json"}

    results = {
        "new_tickets": [],
        "mentioned_tickets": [],
        "ready_to_dev": []
    }

    # Call A: New To Do tickets created in last 24h
    try:
        jql_new = 'project in (CMA, CMB) AND status = "To Do" AND created >= -1d ORDER BY created ASC'
        params_new = {
            "jql": jql_new,
            "fields": "summary,status,creator,created,assignee,priority,project,issuetype",
            "maxResults": 30
        }

        url = f"{JIRA_BASE_URL}/rest/api/3/search/jql"
        response = requests.get(
            url,
            auth=auth,
            headers=headers,
            params=params_new,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            for issue in data.get("issues", []):
                key = issue["key"]
                fields = issue["fields"]
                summary = fields.get("summary", "No summary")

                # Parse created date
                created_str = fields.get("created", "")
                try:
                    created_dt = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
                    created_fmt = created_dt.strftime("%b %d %H:%M")
                except:
                    created_fmt = "Unknown"

                # Creator
                creator = fields.get("creator", {})
                creator_name = creator.get("displayName", "Unknown") if creator else "Unknown"

                # Assignee
                assignee = fields.get("assignee", {})
                assignee_name = assignee.get("displayName", "Unassigned") if assignee else "Unassigned"

                # Priority
                priority = fields.get("priority", {})
                priority_name = priority.get("name", "Medium") if priority else "Medium"

                # Issue type
                issuetype = fields.get("issuetype", {})
                issuetype_name = issuetype.get("name", "Task") if issuetype else "Task"

                ticket_url = f"{JIRA_BASE_URL}/browse/{key}"
                results["new_tickets"].append(
                    f"• [{key}]({ticket_url}) {summary}\n"
                    f"  Type: {issuetype_name} | Created: {created_fmt} by {creator_name} | Assignee: {assignee_name} | Priority: {priority_name}"
                )
        else:
            print(f"Warning: Jira new tickets query failed with status {response.status_code}")
    except Exception as e:
        print(f"Warning: Failed to fetch new Jira tickets: {e}")

    # Call B: Tickets where Basile is mentioned in comments
    try:
        jql_mentioned = 'project in (CMA, CMB) AND comment ~ "Basile" AND updated >= -1d ORDER BY created ASC'
        params_mentioned = {
            "jql": jql_mentioned,
            "fields": "summary,status,assignee,priority,updated,created,project,creator,issuetype",
            "maxResults": 20
        }

        response = requests.get(
            f"{JIRA_BASE_URL}/rest/api/3/search/jql",
            auth=auth,
            headers=headers,
            params=params_mentioned,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            for issue in data.get("issues", []):
                key = issue["key"]
                fields = issue["fields"]
                summary = fields.get("summary", "No summary")

                # Status
                status = fields.get("status", {})
                status_name = status.get("name", "Unknown") if status else "Unknown"

                # Assignee
                assignee = fields.get("assignee", {})
                assignee_name = assignee.get("displayName", "Unassigned") if assignee else "Unassigned"

                # Priority
                priority = fields.get("priority", {})
                priority_name = priority.get("name", "Medium") if priority else "Medium"

                # Updated date
                updated_str = fields.get("updated", "")
                try:
                    updated_dt = datetime.fromisoformat(updated_str.replace("Z", "+00:00"))
                    updated_fmt = updated_dt.strftime("%b %d %H:%M")
                except:
                    updated_fmt = "Unknown"

                # Created date
                created_str = fields.get("created", "")
                try:
                    created_dt = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
                    created_fmt = created_dt.strftime("%b %d %H:%M")
                    # Calculate age in days
                    age_days = (datetime.now(created_dt.tzinfo) - created_dt).days
                    age_str = f"{age_days}d ago" if age_days > 0 else "today"
                except:
                    created_fmt = "Unknown"
                    age_str = ""

                # Creator
                creator = fields.get("creator", {})
                creator_name = creator.get("displayName", "Unknown") if creator else "Unknown"

                # Issue type
                issuetype = fields.get("issuetype", {})
                issuetype_name = issuetype.get("name", "Task") if issuetype else "Task"

                ticket_url = f"{JIRA_BASE_URL}/browse/{key}"
                results["mentioned_tickets"].append(
                    f"• [{key}]({ticket_url}) {summary}\n"
                    f"  Type: {issuetype_name} | Created: {created_fmt} ({age_str}) by {creator_name} | Status: {status_name} | Assignee: {assignee_name} | Last update: {updated_fmt}"
                )
        else:
            print(f"Warning: Jira mentioned tickets query failed with status {response.status_code}")
    except Exception as e:
        print(f"Warning: Failed to fetch mentioned Jira tickets: {e}")

    # Call C: Tickets in "Ready for Dev" status
    try:
        jql_ready = 'project in (CMA, CMB) AND status = "Ready for Dev" ORDER BY created ASC'
        params_ready = {
            "jql": jql_ready,
            "fields": "summary,status,assignee,priority,updated,created,project,creator,issuetype",
            "maxResults": 30
        }

        response = requests.get(
            f"{JIRA_BASE_URL}/rest/api/3/search/jql",
            auth=auth,
            headers=headers,
            params=params_ready,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            for issue in data.get("issues", []):
                key = issue["key"]
                fields = issue["fields"]
                summary = fields.get("summary", "No summary")

                # Assignee
                assignee = fields.get("assignee", {})
                assignee_name = assignee.get("displayName", "Unassigned") if assignee else "Unassigned"

                # Priority
                priority = fields.get("priority", {})
                priority_name = priority.get("name", "Medium") if priority else "Medium"

                # Created date and age
                created_str = fields.get("created", "")
                try:
                    created_dt = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
                    created_fmt = created_dt.strftime("%b %d %H:%M")
                    age_days = (datetime.now(created_dt.tzinfo) - created_dt).days
                    age_str = f"{age_days}d ago" if age_days > 0 else "today"
                except:
                    created_fmt = "Unknown"
                    age_str = ""

                # Updated date
                updated_str = fields.get("updated", "")
                try:
                    updated_dt = datetime.fromisoformat(updated_str.replace("Z", "+00:00"))
                    updated_fmt = updated_dt.strftime("%b %d %H:%M")
                except:
                    updated_fmt = "Unknown"

                # Creator
                creator = fields.get("creator", {})
                creator_name = creator.get("displayName", "Unknown") if creator else "Unknown"

                # Issue type
                issuetype = fields.get("issuetype", {})
                issuetype_name = issuetype.get("name", "Task") if issuetype else "Task"

                ticket_url = f"{JIRA_BASE_URL}/browse/{key}"
                results["ready_to_dev"].append(
                    f"• [{key}]({ticket_url}) {summary}\n"
                    f"  Type: {issuetype_name} | Created: {created_fmt} ({age_str}) by {creator_name} | Assignee: {assignee_name} | Priority: {priority_name} | Last update: {updated_fmt}"
                )
        else:
            print(f"Warning: Jira ready to dev query failed with status {response.status_code}")
    except Exception as e:
        print(f"Warning: Failed to fetch ready to dev Jira tickets: {e}")

    # Format output
    output = "NEW TICKETS (To Do, created last 24h):\n"
    if results["new_tickets"]:
        output += "\n".join(results["new_tickets"])
    else:
        output += "  none"

    output += "\n\nTICKETS WHERE YOU WERE MENTIONED IN COMMENTS (last 24h, sorted by age):\n"
    if results["mentioned_tickets"]:
        output += "\n".join(results["mentioned_tickets"])
    else:
        output += "  none"

    output += "\n\nREADY FOR DEV (sorted by age, oldest first):\n"
    if results["ready_to_dev"]:
        output += "\n".join(results["ready_to_dev"])
    else:
        output += "  none"

    return output


def fetch_slack_channel(channel_id, channel_name):
    """
    Fetch recent messages from a specific Slack channel.
    Returns list of message texts (excluding bot messages).
    """
    try:
        # Get messages from last 24h
        oldest_timestamp = (datetime.now() - timedelta(days=1)).timestamp()

        response = requests.get(
            "https://slack.com/api/conversations.history",
            headers={"Authorization": f"Bearer {SLACK_TOKEN}"},
            params={
                "channel": channel_id,
                "oldest": str(oldest_timestamp),
                "limit": 20
            },
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                messages = []
                for msg in data.get("messages", []):
                    # Skip bot messages
                    if "bot_id" in msg:
                        continue

                    text = msg.get("text", "").strip()
                    if text:
                        # Truncate to 200 chars
                        if len(text) > 200:
                            text = text[:200] + "..."
                        messages.append(text)

                return messages
            else:
                print(f"Warning: Slack API error for {channel_name}: {data.get('error')}")
        else:
            print(f"Warning: Slack channel {channel_name} query failed with status {response.status_code}")
    except Exception as e:
        print(f"Warning: Failed to fetch Slack channel {channel_name}: {e}")

    return []


def fetch_slack():
    """
    Auto-discover all channels the bot is a member of and fetch their recent messages.
    Returns formatted string with messages grouped by channel.
    """
    try:
        # Get list of all channels the bot is a member of
        response = requests.get(
            "https://slack.com/api/conversations.list",
            headers={"Authorization": f"Bearer {SLACK_TOKEN}"},
            params={
                "types": "public_channel,private_channel",
                "exclude_archived": "true",
                "limit": 200
            },
            timeout=30
        )

        if response.status_code != 200:
            print(f"Warning: Failed to list Slack channels (status {response.status_code})")
            return "No Slack data available"

        data = response.json()
        if not data.get("ok"):
            print(f"Warning: Slack API error: {data.get('error')}")
            return "No Slack data available"

        channels = data.get("channels", [])

        # Filter to channels the bot is a member of
        member_channels = [ch for ch in channels if ch.get("is_member", False)]

        print(f"Found {len(member_channels)} channels bot is member of")

        # Fetch messages from each channel
        all_messages = {}
        for channel in member_channels:
            channel_id = channel["id"]
            channel_name = channel.get("name", "unknown")

            messages = fetch_slack_channel(channel_id, channel_name)
            if messages:
                all_messages[channel_name] = messages

        # Format output
        if not all_messages:
            return "No recent messages in monitored channels"

        output_parts = []
        for channel_name, messages in sorted(all_messages.items()):
            output_parts.append(f"#{channel_name}:")
            for msg in messages:
                output_parts.append(f"  - {msg}")

        return "\n".join(output_parts)

    except Exception as e:
        print(f"Warning: Failed to fetch Slack data: {e}")
        return "No Slack data available"


def generate_briefing(jira_data, slack_data):
    """
    Use Claude API to generate a concise daily briefing.
    """
    today = datetime.now().strftime("%A, %B %d, %Y")

    prompt = f"""You are the daily briefing assistant for Basile, Senior PM at Smily (vacation rental SaaS).
Smily is a property management and channel management platform serving vacation rental property managers.
Today is {today}.

JIRA — CMA (Channels Management A) and CMB (Channels Management B) projects:
{jira_data}

SLACK — recent messages from key channels:
{slack_data}

Write a concise morning briefing in this format:
1. 🆕 New tickets to triage (from the To Do list above — summarise each in one line)
2. 💬 Tickets where you were mentioned (action required? highlight old tickets)
3. 🛠️ Ready for Dev tickets (highlight old ones waiting for dev)
4. 🔴 Blockers / urgent signals from Slack
5. 📋 Suggested focus for today (top 2–3 items max, prioritize old tickets)

Rules:
- Bullet points only, no prose paragraphs
- Max 35 lines total
- If a section has nothing to report, write "nothing to report"
- Highlight tickets that are >7 days old as requiring urgent attention
- Write in English"""

    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 1000,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            },
            timeout=60
        )

        if response.status_code == 200:
            data = response.json()
            return data["content"][0]["text"]
        else:
            print(f"Warning: Claude API failed with status {response.status_code}")
            print(f"Debug: Claude error response: {response.text[:500]}")
            return f"Failed to generate briefing. Raw data:\n\nJIRA:\n{jira_data}\n\nSLACK:\n{slack_data}"

    except Exception as e:
        print(f"Warning: Failed to generate briefing: {e}")
        return f"Failed to generate briefing. Raw data:\n\nJIRA:\n{jira_data}\n\nSLACK:\n{slack_data}"


def post_to_slack(text):
    """
    Post the briefing to the configured Slack channel.
    """
    date = datetime.now().strftime("%A, %B %d, %Y")

    try:
        response = requests.post(
            "https://slack.com/api/chat.postMessage",
            headers={
                "Authorization": f"Bearer {SLACK_TOKEN}",
                "Content-Type": "application/json"
            },
            json={
                "channel": SLACK_OUTPUT_CHANNEL,
                "text": f"*📬 Daily briefing — {date}*\n\n{text}",
                "mrkdwn": True
            },
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                print(f"✅ Briefing posted to Slack successfully")
            else:
                print(f"Warning: Slack post failed: {data.get('error')}")
        else:
            print(f"Warning: Slack post failed with status {response.status_code}")

    except Exception as e:
        print(f"Warning: Failed to post to Slack: {e}")


if __name__ == "__main__":
    print("🚀 Starting daily briefing generation...")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    print("\n📊 Fetching Jira tickets...")
    jira_data = fetch_jira()

    print("\n💬 Fetching Slack messages...")
    slack_data = fetch_slack()

    print("\n🤖 Generating briefing with Claude...")
    briefing = generate_briefing(jira_data, slack_data)

    print("\n📤 Posting to Slack...")
    post_to_slack(briefing)

    print("\n" + "="*60)
    print("GENERATED BRIEFING:")
    print("="*60)
    print(briefing)
    print("="*60)
    print("\n✅ Done!")
