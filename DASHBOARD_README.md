# Smart Inbox Dashboard

A comprehensive Streamlit dashboard that fetches, classifies, and manages your emails with AI-powered categorization.

## Features

### 📊 Summary Metrics
- Total emails processed
- Meeting scheduled count and percentage
- Emails needing replies count and percentage
- Other/ignored emails count and percentage

### 📅 Meeting Scheduled Section
- Displays emails that require scheduling a meeting
- Shows: From, Subject, Priority, Summary, Date, Start Time
- Action: Create Google Meet and send invite automatically

### ✉️ Needs Reply Section
- Displays emails that need a response
- Shows: From, Subject, Priority, Summary, Suggested Reply
- Action: Edit and send reply directly from dashboard

### 📋 Other Emails Section
- Displays emails that can be ignored (newsletters, promotions, etc.)
- Shows: From, Subject, Priority, Summary, Reason for ignoring

### 🔍 Filtering
- Filter by priority (LOW, NORMAL, HIGH)
- Adjustable email fetch count (5-50 emails)

## How to Run

1. Make sure you have all dependencies installed:
   ```bash
   pip install -r requirements.txt
   ```

2. Ensure your `.env` file contains your `GROQ_API_KEY`

3. Make sure you have `credentials.json` for Gmail API access

4. Run the dashboard:
   ```bash
   streamlit run dashboard.py
   ```

5. In the sidebar:
   - Adjust the number of emails to fetch
   - Click "Fetch & Classify Emails"
   - Wait for AI to process all emails
   - Use filters to narrow down results

6. Interact with emails:
   - Expand action sections to schedule meetings or send replies
   - Edit suggested replies before sending
   - View all emails organized by category

## Dashboard Layout

```
┌─────────────────────────────────────────────────┐
│  📊 Smart Inbox Dashboard                       │
├─────────────────────────────────────────────────┤
│  📈 Summary Metrics                             │
│  [Total] [Meetings] [Replies] [Other]          │
├─────────────────────────────────────────────────┤
│  📅 Meeting Scheduled                           │
│  [Table with meeting emails]                    │
│  [Actions: Create Google Meet]                  │
├─────────────────────────────────────────────────┤
│  ✉️ Needs Reply                                 │
│  [Table with emails needing replies]            │
│  [Actions: Edit & Send Reply]                   │
├─────────────────────────────────────────────────┤
│  📋 Other Emails (Ignored)                      │
│  [Table with other emails]                      │
└─────────────────────────────────────────────────┘
```

## Sidebar Controls

- **Max emails to fetch**: Slider (5-50)
- **Fetch & Classify Emails**: Button to start processing
- **Priority Filter**: Multi-select for LOW/NORMAL/HIGH

## Notes

- The dashboard uses session state to maintain processed emails
- AI classification happens once when you click "Fetch & Classify"
- All actions (meeting creation, sending replies) happen in real-time
- The dashboard automatically handles email threading for replies
