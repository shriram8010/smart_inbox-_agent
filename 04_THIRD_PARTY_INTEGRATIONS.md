# Smart Inbox Agent - Third Party Integrations Guide

## 📋 Table of Contents
1. Overview
2. Current Integrations
3. MCP (Model Context Protocol) Integration
4. Jira Integration
5. Slack Integration
6. Microsoft Teams Integration
7. CRM Integrations (Salesforce, HubSpot)
8. Webhook Integration
9. Custom API Integration
10. Integration Architecture

---

## 1. Overview

### What are Third Party Integrations?

Third party integrations extend the Smart Inbox Agent's capabilities by connecting it to external tools and services. This enables:
- **Automated Workflows:** Trigger actions in other systems
- **Data Synchronization:** Keep information consistent across platforms
- **Enhanced Context:** Pull data from external sources for better AI decisions
- **Unified Experience:** Manage everything from one interface

### Integration Types

**1. API-Based Integrations**
- Direct REST API calls to external services
- OAuth authentication
- Webhook callbacks

**2. MCP (Model Context Protocol) Integrations**
- Standardized protocol for AI tool integration
- Server-based architecture
- Dynamic tool discovery

**3. Database Integrations**
- Direct database connections
- Data warehouses
- Analytics platforms

---

## 2. Current Integrations

### ✅ Active Integrations

**Gmail API**
- **Purpose:** Email fetching and sending
- **Authentication:** OAuth 2.0
- **Scope:** gmail.modify
- **Status:** Production Ready

**Google Calendar API**
- **Purpose:** Meeting scheduling and conflict detection
- **Authentication:** OAuth 2.0
- **Scope:** calendar.events
- **Status:** Production Ready

**Groq API**
- **Purpose:** AI-powered email classification and reply generation
- **Authentication:** API Key
- **Model:** LLaMA 3.3 70B Versatile
- **Status:** Production Ready

---

## 3. MCP (Model Context Protocol) Integration

### What is MCP?

Model Context Protocol (MCP) is an open standard for connecting AI systems to external tools and data sources. It provides:
- **Standardized Interface:** Consistent way to expose tools to AI
- **Dynamic Discovery:** AI can discover available tools at runtime
- **Type Safety:** Structured input/output schemas
- **Server Architecture:** Tools run as separate processes


### MCP Architecture for Smart Inbox

```
┌─────────────────────────────────────────┐
│      Smart Inbox Agent (Client)         │
│  - Email Classification                 │
│  - Reply Generation                     │
│  - Meeting Scheduling                   │
└──────────────┬──────────────────────────┘
               │
               │ MCP Protocol
               │
    ┌──────────┴──────────┐
    │                     │
┌───▼────────┐    ┌──────▼──────┐
│ MCP Server │    │ MCP Server  │
│   (Jira)   │    │   (Slack)   │
└────────────┘    └─────────────┘
```

### Setting Up MCP Integration

#### Step 1: Install MCP Python SDK

```bash
pip install mcp
```

#### Step 2: Create MCP Configuration File

Create `.kiro/settings/mcp.json` in your project:

```json
{
  "mcpServers": {
    "jira-server": {
      "command": "uvx",
      "args": ["mcp-server-jira@latest"],
      "env": {
        "JIRA_URL": "https://your-domain.atlassian.net",
        "JIRA_EMAIL": "your-email@company.com",
        "JIRA_API_TOKEN": "your-jira-api-token"
      },
      "disabled": false,
      "autoApprove": ["jira_search_issues", "jira_get_issue"]
    },
    "slack-server": {
      "command": "uvx",
      "args": ["mcp-server-slack@latest"],
      "env": {
        "SLACK_BOT_TOKEN": "xoxb-your-bot-token",
        "SLACK_APP_TOKEN": "xapp-your-app-token"
      },
      "disabled": false,
      "autoApprove": ["slack_send_message"]
    }
  }
}
```


#### Step 3: Integrate MCP Client in Smart Inbox

Create `mcp_client.py`:

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class MCPIntegration:
    def __init__(self):
        self.sessions = {}
    
    async def connect_server(self, server_name, command, args, env):
        """Connect to an MCP server"""
        server_params = StdioServerParameters(
            command=command,
            args=args,
            env=env
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                self.sessions[server_name] = session
                return session
    
    async def call_tool(self, server_name, tool_name, arguments):
        """Call a tool on an MCP server"""
        session = self.sessions.get(server_name)
        if not session:
            raise Exception(f"Server {server_name} not connected")
        
        result = await session.call_tool(tool_name, arguments)
        return result

# Usage example
async def main():
    mcp = MCPIntegration()
    
    # Connect to Jira server
    await mcp.connect_server(
        "jira-server",
        "uvx",
        ["mcp-server-jira@latest"],
        {
            "JIRA_URL": "https://your-domain.atlassian.net",
            "JIRA_EMAIL": "your-email@company.com",
            "JIRA_API_TOKEN": "your-token"
        }
    )
    
    # Create Jira ticket from email
    result = await mcp.call_tool(
        "jira-server",
        "jira_create_issue",
        {
            "project": "PROJ",
            "summary": "Bug reported via email",
            "description": "Email body content here",
            "issue_type": "Bug"
        }
    )
    
    print(f"Created Jira ticket: {result}")

if __name__ == "__main__":
    asyncio.run(main())
```


#### Step 4: Update Agent to Use MCP Tools

Modify `agent.py` to include MCP tool calls:

```python
from mcp_client import MCPIntegration

async def run_agent_with_mcp(email: dict):
    """Enhanced agent with MCP integration"""
    
    # Standard AI classification
    result = run_agent(email)
    
    # If email mentions bug/issue, create Jira ticket
    if "bug" in email["subject"].lower() or "issue" in email["subject"].lower():
        mcp = MCPIntegration()
        
        # Create Jira ticket
        ticket = await mcp.call_tool(
            "jira-server",
            "jira_create_issue",
            {
                "project": "SUPPORT",
                "summary": email["subject"],
                "description": email["body"],
                "issue_type": "Bug",
                "priority": result.get("priority", "Normal")
            }
        )
        
        result["jira_ticket"] = ticket["key"]
        result["jira_url"] = ticket["url"]
    
    return result
```

### Available MCP Servers

**Official MCP Servers:**
- `mcp-server-jira` - Jira integration
- `mcp-server-slack` - Slack integration
- `mcp-server-github` - GitHub integration
- `mcp-server-postgres` - PostgreSQL database
- `mcp-server-filesystem` - File system access
- `mcp-server-fetch` - HTTP requests

**Installation:**
```bash
# Install uv (Python package manager)
pip install uv

# MCP servers are auto-installed via uvx when first used
# No manual installation needed
```

---

## 4. Jira Integration

### Use Cases

1. **Auto-Create Tickets from Emails**
   - Bug reports → Jira bugs
   - Feature requests → Jira stories
   - Support requests → Jira service desk tickets

2. **Email-to-Jira Linking**
   - Link email threads to existing tickets
   - Update ticket status via email
   - Add comments from email replies

3. **Notification Management**
   - Filter Jira notification emails
   - Summarize daily Jira updates
   - Priority-based routing


### Setup: Jira API Integration

#### Step 1: Generate Jira API Token

1. Go to: https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Name: `Smart Inbox Agent`
4. Copy the generated token

#### Step 2: Configure Jira Credentials

Add to `.env` file:

```env
JIRA_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@company.com
JIRA_API_TOKEN=your-api-token-here
JIRA_PROJECT_KEY=PROJ
```

#### Step 3: Install Jira Python Library

```bash
pip install jira
```

#### Step 4: Create Jira Client Module

Create `jira_client.py`:

```python
import os
from jira import JIRA
from dotenv import load_dotenv

load_dotenv()

class JiraIntegration:
    def __init__(self):
        self.jira = JIRA(
            server=os.getenv("JIRA_URL"),
            basic_auth=(
                os.getenv("JIRA_EMAIL"),
                os.getenv("JIRA_API_TOKEN")
            )
        )
        self.project_key = os.getenv("JIRA_PROJECT_KEY")
    
    def create_issue(self, summary, description, issue_type="Task", priority="Medium"):
        """Create a Jira issue from email"""
        issue_dict = {
            'project': {'key': self.project_key},
            'summary': summary,
            'description': description,
            'issuetype': {'name': issue_type},
            'priority': {'name': priority}
        }
        
        new_issue = self.jira.create_issue(fields=issue_dict)
        return {
            'key': new_issue.key,
            'url': f"{os.getenv('JIRA_URL')}/browse/{new_issue.key}"
        }
    
    def search_issues(self, query):
        """Search for existing issues"""
        issues = self.jira.search_issues(query, maxResults=10)
        return [{'key': issue.key, 'summary': issue.fields.summary} for issue in issues]
    
    def add_comment(self, issue_key, comment):
        """Add comment to existing issue"""
        self.jira.add_comment(issue_key, comment)
        return True
    
    def update_status(self, issue_key, status):
        """Update issue status"""
        issue = self.jira.issue(issue_key)
        transitions = self.jira.transitions(issue)
        
        for transition in transitions:
            if transition['name'].lower() == status.lower():
                self.jira.transition_issue(issue, transition['id'])
                return True
        return False

# Usage example
if __name__ == "__main__":
    jira = JiraIntegration()
    
    # Create issue
    issue = jira.create_issue(
        summary="Bug: Login page not loading",
        description="User reported login page shows blank screen",
        issue_type="Bug",
        priority="High"
    )
    print(f"Created: {issue['url']}")
```


#### Step 5: Integrate with Smart Inbox Agent

Modify `agent.py` to include Jira logic:

```python
from jira_client import JiraIntegration

def run_agent_with_jira(email: dict) -> dict:
    """Enhanced agent with Jira integration"""
    
    # Standard AI classification
    result = run_agent(email)
    
    # Jira integration logic
    jira = JiraIntegration()
    
    # Auto-create Jira tickets for bugs
    if "bug" in email["subject"].lower() or "error" in email["body"].lower():
        issue = jira.create_issue(
            summary=email["subject"],
            description=f"Reported by: {email['from']}\n\n{email['body']}",
            issue_type="Bug",
            priority=result.get("priority", "Medium")
        )
        
        result["jira_ticket"] = issue["key"]
        result["jira_url"] = issue["url"]
        result["action"] = "JIRA_CREATED"
    
    # Link to existing Jira tickets mentioned in email
    import re
    jira_pattern = r'[A-Z]+-\d+'
    matches = re.findall(jira_pattern, email["body"])
    
    if matches:
        result["linked_tickets"] = matches
        # Add email as comment to Jira ticket
        for ticket_key in matches:
            jira.add_comment(
                ticket_key,
                f"Email from {email['from']}:\n\n{email['body'][:500]}"
            )
    
    return result
```

### Jira Workflow Examples

**Example 1: Bug Report Email → Jira Bug**

```
Email Subject: "Bug: Payment processing fails"
Email Body: "When I try to checkout, I get error 500"

↓ Smart Inbox Agent ↓

1. AI classifies as bug report
2. Creates Jira bug ticket
3. Assigns priority based on severity
4. Sends reply with ticket number
5. Links email thread to Jira ticket

Result:
- Jira ticket: PROJ-123
- Reply sent: "Thanks! Created ticket PROJ-123"
```

**Example 2: Feature Request → Jira Story**

```
Email Subject: "Feature request: Dark mode"
Email Body: "Would love to have dark mode option"

↓ Smart Inbox Agent ↓

1. AI classifies as feature request
2. Creates Jira story
3. Adds to product backlog
4. Sends acknowledgment reply

Result:
- Jira story: PROJ-124
- Reply: "Great idea! Tracked as PROJ-124"
```


---

## 5. Slack Integration

### Use Cases

1. **Email-to-Slack Notifications**
   - Forward important emails to Slack channels
   - Notify team of urgent emails
   - Share meeting invites in team channels

2. **Slack-to-Email Responses**
   - Reply to emails from Slack
   - Approve/reject requests via Slack buttons
   - Schedule meetings from Slack commands

3. **Team Collaboration**
   - Discuss emails in Slack threads
   - Assign email actions to team members
   - Track email response status

### Setup: Slack API Integration

#### Step 1: Create Slack App

1. Go to: https://api.slack.com/apps
2. Click "Create New App" → "From scratch"
3. App Name: `Smart Inbox Agent`
4. Select your workspace

#### Step 2: Configure Bot Permissions

1. Go to "OAuth & Permissions"
2. Add Bot Token Scopes:
   - `chat:write` - Send messages
   - `chat:write.public` - Send to public channels
   - `channels:read` - List channels
   - `users:read` - Get user info

3. Install App to Workspace
4. Copy "Bot User OAuth Token" (starts with `xoxb-`)

#### Step 3: Configure Slack Credentials

Add to `.env`:

```env
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_CHANNEL_ID=C01234567  # Channel ID for notifications
```

#### Step 4: Install Slack SDK

```bash
pip install slack-sdk
```

#### Step 5: Create Slack Client Module

Create `slack_client.py`:

```python
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

load_dotenv()

class SlackIntegration:
    def __init__(self):
        self.client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
        self.default_channel = os.getenv("SLACK_CHANNEL_ID")
    
    def send_message(self, channel, text, blocks=None):
        """Send message to Slack channel"""
        try:
            response = self.client.chat_postMessage(
                channel=channel,
                text=text,
                blocks=blocks
            )
            return response["ts"]  # Message timestamp
        except SlackApiError as e:
            print(f"Error sending message: {e.response['error']}")
            return None
    
    def send_email_notification(self, email, priority="NORMAL"):
        """Send email notification to Slack"""
        
        # Color based on priority
        color = {
            "HIGH": "#ff0000",
            "NORMAL": "#36a64f",
            "LOW": "#cccccc"
        }.get(priority, "#36a64f")
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"📧 New Email: {priority} Priority"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*From:*\n{email['from']}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Subject:*\n{email['subject']}"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Body:*\n{email['body'][:300]}..."
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Reply"
                        },
                        "value": email["id"],
                        "action_id": "reply_email"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Schedule Meeting"
                        },
                        "value": email["id"],
                        "action_id": "schedule_meeting"
                    }
                ]
            }
        ]
        
        return self.send_message(self.default_channel, f"New email from {email['from']}", blocks)
    
    def send_meeting_notification(self, meeting_details):
        """Notify about scheduled meeting"""
        text = f"""
📅 *Meeting Scheduled*

*Date:* {meeting_details['date_formatted']}
*Time:* {meeting_details['start_time_ist']} - {meeting_details['end_time_ist']} IST
*Meet Link:* {meeting_details['meet_link']}
*Attendee:* {meeting_details['attendee']}
        """
        
        return self.send_message(self.default_channel, text)

# Usage example
if __name__ == "__main__":
    slack = SlackIntegration()
    
    # Test notification
    email = {
        "id": "12345",
        "from": "john@example.com",
        "subject": "Urgent: Server down",
        "body": "Production server is not responding..."
    }
    
    slack.send_email_notification(email, priority="HIGH")
```


#### Step 6: Integrate with Smart Inbox

Modify `main_v2.py` to add Slack notifications:

```python
from slack_client import SlackIntegration

# After email classification
slack = SlackIntegration()

# Send high priority emails to Slack
if result["priority"] == "HIGH":
    slack.send_email_notification(email, priority="HIGH")

# Notify about scheduled meetings
if result["action"] == "SCHEDULE_MEET":
    meeting_result = create_meet(...)
    slack.send_meeting_notification({
        **meeting_result,
        "attendee": email["from"]
    })
```

---

## 6. Microsoft Teams Integration

### Use Cases

1. **Email Notifications in Teams**
2. **Meeting Coordination**
3. **Team Collaboration on Emails**

### Setup: Teams Webhook Integration

#### Step 1: Create Incoming Webhook in Teams

1. Open Teams channel
2. Click "..." → "Connectors"
3. Search "Incoming Webhook"
4. Configure webhook
5. Copy webhook URL

#### Step 2: Configure Teams Credentials

Add to `.env`:

```env
TEAMS_WEBHOOK_URL=https://outlook.office.com/webhook/...
```

#### Step 3: Create Teams Client Module

Create `teams_client.py`:

```python
import os
import requests
from dotenv import load_dotenv

load_dotenv()

class TeamsIntegration:
    def __init__(self):
        self.webhook_url = os.getenv("TEAMS_WEBHOOK_URL")
    
    def send_message(self, title, text, color="0078D4"):
        """Send message to Teams channel"""
        
        payload = {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions",
            "themeColor": color,
            "title": title,
            "text": text
        }
        
        response = requests.post(self.webhook_url, json=payload)
        return response.status_code == 200
    
    def send_email_notification(self, email, priority="NORMAL"):
        """Send email notification to Teams"""
        
        color = {
            "HIGH": "FF0000",
            "NORMAL": "0078D4",
            "LOW": "CCCCCC"
        }.get(priority, "0078D4")
        
        title = f"📧 New Email: {priority} Priority"
        text = f"""
**From:** {email['from']}
**Subject:** {email['subject']}

**Body:**
{email['body'][:300]}...
        """
        
        return self.send_message(title, text, color)

# Usage
teams = TeamsIntegration()
teams.send_email_notification(email, priority="HIGH")
```

---

## 7. CRM Integrations (Salesforce, HubSpot)

### Salesforce Integration

#### Use Cases
- Create leads from inquiry emails
- Update contact records
- Log email activities
- Sync meeting schedules

#### Setup

```bash
pip install simple-salesforce
```

Create `salesforce_client.py`:

```python
import os
from simple_salesforce import Salesforce
from dotenv import load_dotenv

load_dotenv()

class SalesforceIntegration:
    def __init__(self):
        self.sf = Salesforce(
            username=os.getenv("SALESFORCE_USERNAME"),
            password=os.getenv("SALESFORCE_PASSWORD"),
            security_token=os.getenv("SALESFORCE_TOKEN")
        )
    
    def create_lead(self, email):
        """Create lead from email"""
        
        # Extract name from email
        name_parts = email['from'].split('@')[0].split('.')
        first_name = name_parts[0].title() if len(name_parts) > 0 else "Unknown"
        last_name = name_parts[1].title() if len(name_parts) > 1 else "Lead"
        
        lead = {
            'FirstName': first_name,
            'LastName': last_name,
            'Email': email['from'],
            'Company': email['from'].split('@')[1],
            'Description': email['body'][:1000],
            'LeadSource': 'Email'
        }
        
        result = self.sf.Lead.create(lead)
        return result['id']
    
    def log_email_activity(self, contact_email, email_subject, email_body):
        """Log email as activity"""
        
        # Find contact by email
        contact = self.sf.query(
            f"SELECT Id FROM Contact WHERE Email = '{contact_email}' LIMIT 1"
        )
        
        if contact['totalSize'] > 0:
            contact_id = contact['records'][0]['Id']
            
            # Create task
            task = {
                'WhoId': contact_id,
                'Subject': f"Email: {email_subject}",
                'Description': email_body[:32000],
                'Status': 'Completed',
                'ActivityDate': datetime.now().strftime('%Y-%m-%d')
            }
            
            self.sf.Task.create(task)
            return True
        
        return False

# Usage
sf = SalesforceIntegration()
lead_id = sf.create_lead(email)
```


### HubSpot Integration

#### Setup

```bash
pip install hubspot-api-client
```

Create `hubspot_client.py`:

```python
import os
from hubspot import HubSpot
from hubspot.crm.contacts import SimplePublicObjectInput
from dotenv import load_dotenv

load_dotenv()

class HubSpotIntegration:
    def __init__(self):
        self.client = HubSpot(access_token=os.getenv("HUBSPOT_ACCESS_TOKEN"))
    
    def create_contact(self, email):
        """Create contact from email"""
        
        properties = {
            "email": email['from'],
            "firstname": email['from'].split('@')[0].split('.')[0].title(),
            "lastname": email['from'].split('@')[0].split('.')[-1].title(),
            "lifecyclestage": "lead"
        }
        
        contact_input = SimplePublicObjectInput(properties=properties)
        
        try:
            contact = self.client.crm.contacts.basic_api.create(
                simple_public_object_input=contact_input
            )
            return contact.id
        except Exception as e:
            print(f"Error creating contact: {e}")
            return None
    
    def log_email(self, contact_email, email_subject, email_body):
        """Log email as engagement"""
        
        # Search for contact
        search_request = {
            "filterGroups": [{
                "filters": [{
                    "propertyName": "email",
                    "operator": "EQ",
                    "value": contact_email
                }]
            }]
        }
        
        results = self.client.crm.contacts.search_api.do_search(
            public_object_search_request=search_request
        )
        
        if results.total > 0:
            contact_id = results.results[0].id
            
            # Create email engagement
            engagement = {
                "engagement": {
                    "type": "EMAIL"
                },
                "associations": {
                    "contactIds": [contact_id]
                },
                "metadata": {
                    "subject": email_subject,
                    "body": email_body[:65536]
                }
            }
            
            # Note: Engagements API requires additional setup
            return True
        
        return False

# Usage
hubspot = HubSpotIntegration()
contact_id = hubspot.create_contact(email)
```

---

## 8. Webhook Integration

### Generic Webhook Support

Create `webhook_client.py`:

```python
import os
import requests
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class WebhookIntegration:
    def __init__(self):
        self.webhooks = {
            "email_classified": os.getenv("WEBHOOK_EMAIL_CLASSIFIED"),
            "meeting_scheduled": os.getenv("WEBHOOK_MEETING_SCHEDULED"),
            "reply_sent": os.getenv("WEBHOOK_REPLY_SENT")
        }
    
    def trigger_webhook(self, event_type: str, payload: Dict[str, Any]):
        """Trigger webhook for specific event"""
        
        webhook_url = self.webhooks.get(event_type)
        if not webhook_url:
            return False
        
        try:
            response = requests.post(
                webhook_url,
                json={
                    "event": event_type,
                    "timestamp": datetime.now().isoformat(),
                    "data": payload
                },
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Webhook error: {e}")
            return False
    
    def on_email_classified(self, email, classification):
        """Trigger when email is classified"""
        return self.trigger_webhook("email_classified", {
            "email_id": email["id"],
            "from": email["from"],
            "subject": email["subject"],
            "action": classification["action"],
            "priority": classification["priority"]
        })
    
    def on_meeting_scheduled(self, email, meeting):
        """Trigger when meeting is scheduled"""
        return self.trigger_webhook("meeting_scheduled", {
            "email_id": email["id"],
            "attendee": email["from"],
            "date": meeting["date_formatted"],
            "time": f"{meeting['start_time_ist']} - {meeting['end_time_ist']}",
            "meet_link": meeting["meet_link"]
        })
    
    def on_reply_sent(self, email, reply_text):
        """Trigger when reply is sent"""
        return self.trigger_webhook("reply_sent", {
            "email_id": email["id"],
            "to": email["from"],
            "subject": email["subject"],
            "reply_preview": reply_text[:200]
        })

# Usage in main_v2.py
webhook = WebhookIntegration()

# After classification
webhook.on_email_classified(email, result)

# After meeting scheduled
webhook.on_meeting_scheduled(email, meeting_result)

# After reply sent
webhook.on_reply_sent(email, reply_text)
```

### Webhook Configuration

Add to `.env`:

```env
WEBHOOK_EMAIL_CLASSIFIED=https://your-server.com/webhooks/email-classified
WEBHOOK_MEETING_SCHEDULED=https://your-server.com/webhooks/meeting-scheduled
WEBHOOK_REPLY_SENT=https://your-server.com/webhooks/reply-sent
```

---

## 9. Custom API Integration

### Template for Custom Integration

Create `custom_integration.py`:

```python
import os
import requests
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class CustomAPIIntegration:
    def __init__(self):
        self.base_url = os.getenv("CUSTOM_API_URL")
        self.api_key = os.getenv("CUSTOM_API_KEY")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def make_request(self, method: str, endpoint: str, data: Dict[str, Any] = None):
        """Generic API request method"""
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers, params=data)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            elif method == "PUT":
                response = requests.put(url, headers=self.headers, json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=self.headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return None
    
    def sync_email(self, email: Dict[str, Any]):
        """Sync email to custom system"""
        return self.make_request("POST", "emails", {
            "from": email["from"],
            "subject": email["subject"],
            "body": email["body"],
            "timestamp": email.get("timestamp")
        })
    
    def get_user_preferences(self, email_address: str):
        """Get user preferences from custom system"""
        return self.make_request("GET", f"users/{email_address}/preferences")

# Usage
custom_api = CustomAPIIntegration()
custom_api.sync_email(email)
```


---

## 10. Integration Architecture

### Unified Integration Layer

Create `integration_manager.py`:

```python
from typing import Dict, Any, List
from jira_client import JiraIntegration
from slack_client import SlackIntegration
from teams_client import TeamsIntegration
from salesforce_client import SalesforceIntegration
from webhook_client import WebhookIntegration

class IntegrationManager:
    """Centralized integration management"""
    
    def __init__(self):
        self.integrations = {}
        self.enabled_integrations = []
        
        # Initialize integrations based on environment
        self._init_integrations()
    
    def _init_integrations(self):
        """Initialize available integrations"""
        
        # Jira
        if os.getenv("JIRA_URL"):
            self.integrations["jira"] = JiraIntegration()
            self.enabled_integrations.append("jira")
        
        # Slack
        if os.getenv("SLACK_BOT_TOKEN"):
            self.integrations["slack"] = SlackIntegration()
            self.enabled_integrations.append("slack")
        
        # Teams
        if os.getenv("TEAMS_WEBHOOK_URL"):
            self.integrations["teams"] = TeamsIntegration()
            self.enabled_integrations.append("teams")
        
        # Salesforce
        if os.getenv("SALESFORCE_USERNAME"):
            self.integrations["salesforce"] = SalesforceIntegration()
            self.enabled_integrations.append("salesforce")
        
        # Webhooks
        if os.getenv("WEBHOOK_EMAIL_CLASSIFIED"):
            self.integrations["webhook"] = WebhookIntegration()
            self.enabled_integrations.append("webhook")
    
    def process_email(self, email: Dict[str, Any], classification: Dict[str, Any]):
        """Process email through all enabled integrations"""
        
        results = {}
        
        # Jira: Create tickets for bugs/features
        if "jira" in self.enabled_integrations:
            if "bug" in email["subject"].lower() or "feature" in email["subject"].lower():
                issue = self.integrations["jira"].create_issue(
                    summary=email["subject"],
                    description=email["body"],
                    issue_type="Bug" if "bug" in email["subject"].lower() else "Story",
                    priority=classification.get("priority", "Medium")
                )
                results["jira_ticket"] = issue["key"]
        
        # Slack: Notify high priority emails
        if "slack" in self.enabled_integrations:
            if classification.get("priority") == "HIGH":
                self.integrations["slack"].send_email_notification(
                    email, 
                    priority="HIGH"
                )
                results["slack_notified"] = True
        
        # Teams: Notify high priority emails
        if "teams" in self.enabled_integrations:
            if classification.get("priority") == "HIGH":
                self.integrations["teams"].send_email_notification(
                    email,
                    priority="HIGH"
                )
                results["teams_notified"] = True
        
        # Salesforce: Create leads from inquiries
        if "salesforce" in self.enabled_integrations:
            if "inquiry" in email["subject"].lower() or "interested" in email["body"].lower():
                lead_id = self.integrations["salesforce"].create_lead(email)
                results["salesforce_lead"] = lead_id
        
        # Webhooks: Trigger for all classifications
        if "webhook" in self.enabled_integrations:
            self.integrations["webhook"].on_email_classified(email, classification)
            results["webhook_triggered"] = True
        
        return results
    
    def process_meeting(self, email: Dict[str, Any], meeting: Dict[str, Any]):
        """Process meeting through integrations"""
        
        results = {}
        
        # Slack: Notify about meeting
        if "slack" in self.enabled_integrations:
            self.integrations["slack"].send_meeting_notification(meeting)
            results["slack_notified"] = True
        
        # Webhooks: Trigger meeting scheduled
        if "webhook" in self.enabled_integrations:
            self.integrations["webhook"].on_meeting_scheduled(email, meeting)
            results["webhook_triggered"] = True
        
        return results
    
    def get_enabled_integrations(self) -> List[str]:
        """Get list of enabled integrations"""
        return self.enabled_integrations

# Usage in main_v2.py
integration_manager = IntegrationManager()

# After email classification
integration_results = integration_manager.process_email(email, result)

# After meeting scheduled
meeting_results = integration_manager.process_meeting(email, meeting_result)
```

### Integration Flow Diagram

```
┌─────────────────────────────────────────────────┐
│         Smart Inbox Agent (Core)                │
│  - Fetch Emails                                 │
│  - AI Classification                            │
│  - Reply Generation                             │
│  - Meeting Scheduling                           │
└──────────────┬──────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────┐
│       Integration Manager (Orchestrator)         │
│  - Route to appropriate integrations             │
│  - Handle errors and retries                     │
│  - Aggregate results                             │
└──────┬───────┬───────┬───────┬───────┬───────────┘
       │       │       │       │       │
       ▼       ▼       ▼       ▼       ▼
   ┌────┐  ┌────┐  ┌────┐  ┌────┐  ┌────┐
   │Jira│  │Slack│ │Teams│ │ CRM │  │Web │
   │    │  │     │ │     │ │     │  │hook│
   └────┘  └─────┘ └─────┘ └─────┘  └────┘
```

---

## 11. Integration Testing

### Test Checklist

**Jira Integration:**
- [ ] Create bug ticket from email
- [ ] Create feature request
- [ ] Link to existing ticket
- [ ] Add comment to ticket
- [ ] Update ticket status

**Slack Integration:**
- [ ] Send high priority notification
- [ ] Send meeting notification
- [ ] Format message correctly
- [ ] Handle errors gracefully

**Teams Integration:**
- [ ] Send webhook message
- [ ] Format adaptive card
- [ ] Handle webhook failures

**CRM Integration:**
- [ ] Create lead from email
- [ ] Log email activity
- [ ] Update contact record

**Webhook Integration:**
- [ ] Trigger on classification
- [ ] Trigger on meeting scheduled
- [ ] Trigger on reply sent
- [ ] Handle timeout errors

### Test Script

Create `test_integrations.py`:

```python
import asyncio
from integration_manager import IntegrationManager

async def test_all_integrations():
    """Test all integrations"""
    
    manager = IntegrationManager()
    
    print(f"Enabled integrations: {manager.get_enabled_integrations()}")
    
    # Test email
    test_email = {
        "id": "test123",
        "from": "test@example.com",
        "subject": "Bug: Login not working",
        "body": "I can't log in to the system. Getting error 500."
    }
    
    test_classification = {
        "action": "REPLY",
        "priority": "HIGH",
        "summary": "Login issue reported"
    }
    
    # Test email processing
    print("\n--- Testing Email Processing ---")
    results = manager.process_email(test_email, test_classification)
    print(f"Results: {results}")
    
    # Test meeting processing
    print("\n--- Testing Meeting Processing ---")
    test_meeting = {
        "date_formatted": "27 December 2025",
        "start_time_ist": "04:00 PM",
        "end_time_ist": "04:30 PM",
        "meet_link": "https://meet.google.com/test-link"
    }
    
    meeting_results = manager.process_meeting(test_email, test_meeting)
    print(f"Meeting Results: {meeting_results}")

if __name__ == "__main__":
    asyncio.run(test_all_integrations())
```

Run tests:
```bash
python test_integrations.py
```

---

## 12. Best Practices

### Security
1. **Never commit API keys** - Use `.env` file
2. **Rotate tokens regularly** - Update every 90 days
3. **Use minimal permissions** - Only required scopes
4. **Validate webhook signatures** - Verify authenticity
5. **Encrypt sensitive data** - Use encryption at rest

### Performance
1. **Async operations** - Use asyncio for parallel calls
2. **Retry logic** - Handle transient failures
3. **Rate limiting** - Respect API limits
4. **Caching** - Cache frequently accessed data
5. **Batch operations** - Group API calls when possible

### Error Handling
1. **Graceful degradation** - Continue if one integration fails
2. **Detailed logging** - Log all integration attempts
3. **User notifications** - Inform users of failures
4. **Fallback mechanisms** - Have backup options
5. **Monitoring** - Track integration health

### Maintenance
1. **Version pinning** - Lock dependency versions
2. **Regular updates** - Keep libraries current
3. **Documentation** - Document all integrations
4. **Testing** - Automated integration tests
5. **Monitoring** - Track usage and errors

---

## 13. Troubleshooting

### Common Issues

**Issue: Jira authentication fails**
```
Solution:
1. Verify JIRA_URL is correct (include https://)
2. Check API token is valid
3. Ensure email matches Jira account
4. Test with curl:
   curl -u email:token https://your-domain.atlassian.net/rest/api/3/myself
```

**Issue: Slack messages not sending**
```
Solution:
1. Verify bot token starts with xoxb-
2. Check bot has chat:write permission
3. Ensure bot is added to channel
4. Test with Slack API tester
```

**Issue: Webhook timeout**
```
Solution:
1. Increase timeout value (default 10s)
2. Check webhook endpoint is accessible
3. Verify webhook URL is correct
4. Test with curl or Postman
```

**Issue: MCP server not connecting**
```
Solution:
1. Install uv: pip install uv
2. Check mcp.json syntax
3. Verify environment variables
4. Check server logs for errors
```

---

## 14. Future Integrations

### Planned Integrations

**Phase 2:**
- GitHub (issue creation, PR notifications)
- Trello (card creation from emails)
- Asana (task management)
- Notion (documentation sync)
- Discord (community notifications)

**Phase 3:**
- Zendesk (support ticket creation)
- Intercom (customer communication)
- Zapier (no-code automation)
- Make.com (workflow automation)
- n8n (self-hosted automation)

**Phase 4:**
- Custom LLM integrations
- Database connectors (PostgreSQL, MongoDB)
- Cloud storage (Dropbox, OneDrive)
- Analytics platforms (Mixpanel, Amplitude)
- Payment processors (Stripe, PayPal)

---

**Document Version:** 1.0  
**Last Updated:** February 2026  
**Status:** Production Ready  
**Integration Count:** 8+ supported integrations
