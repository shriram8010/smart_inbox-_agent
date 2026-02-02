# 📬 Smart Inbox Agent - Complete Demo Guide

## 🎯 Overview

An AI-powered email management system that automatically classifies emails, generates replies, and schedules meetings with conflict detection.

---

## � Queick Start

### Prerequisites
1. Python 3.8+
2. Gmail API credentials (`credentials.json`)
3. Google Calendar API access
4. Groq API key

### Installation

```bash
# Navigate to project directory
cd smart-inbox-agent/smart-inbox-agent

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
# Create .env file with:
GROQ_API_KEY=your_groq_api_key_here
```

### Run the Application

```bash
streamlit run main_v2.py
```

The app will open at `http://localhost:8501`

---

## 📊 Features Overview

### 1. **Two View Modes**

#### Single Email View
- Process one email at a time
- Manual review and action
- Detailed AI analysis

#### Dashboard View
- Bulk email processing
- Categorized tables
- Batch operations
- Summary metrics

---

## 🎬 Demo Walkthrough

### **Step 1: Navigate to Dashboard**

1. Open the app
2. In the sidebar, select **"Dashboard"**
3. You'll see the main dashboard interface

---

### **Step 2: Fetch & Classify Emails**

1. **Sidebar Controls:**
   - Adjust slider: "Max emails to fetch" (5-50)
   - Click **"🔄 Fetch & Classify Emails"**

2. **What Happens:**
   - Fetches emails from Gmail
   - AI analyzes each email
   - Progress bar shows processing
   - Emails categorized automatically

3. **Processing Time:**
   - ~2-3 seconds per email
   - 20 emails ≈ 40-60 seconds

---

### **Step 3: View Summary Metrics**

After processing, you'll see 4 key metrics:

```
┌─────────────────────────────────────────────────┐
│  Total Emails: 20                               │
│  Meeting Scheduled: 3                           │
│  Needs Reply: 8                                 │
│  Other/Ignored: 9                               │
└─────────────────────────────────────────────────┘
```

---

### **Step 4: Meeting Scheduled Section**

#### View Meetings
- Table shows all emails requiring meetings
- Columns: #, From, Subject, Priority

#### Individual Meeting Actions
1. Click on any email row to expand
2. View details:
   - From, Priority, Summary
   - AI Extracted Time Info (debug)
   - Full email body

3. Click **"📆 Schedule Meeting"**

#### Conflict Detection
If time slot is busy:
- ⚠️ Warning appears
- Shows conflicting meeting names
- Two options:
  - **🔄 Find Next Available Slot** - Auto-reschedule
  - **✅ Schedule Anyway** - Double-book

#### Success Display
```
✅ Meeting scheduled!

📅 Date: 27 December 2025
⏰ Time: 04:00 PM - 04:30 PM IST
🔗 Meet Link: https://meet.google.com/xxx-xxxx-xxx
```

#### Bulk Scheduling
- Click **"📆 Schedule All Meetings"** (top right)
- Automatically schedules all meetings
- Auto-resolves conflicts
- Shows summary with rescheduled meetings

---

### **Step 5: Needs Reply Section**

#### View Replies
- Table shows emails needing responses
- Columns: #, From, Subject, Priority

#### Individual Reply Actions
1. Click on any email to expand
2. View AI-generated reply
3. Edit reply text if needed
4. Click **"📤 Send Reply"**

#### Bulk Replies
- Click **"📤 Send All Replies"** (top right)
- Sends all AI-generated replies at once
- Shows progress bar
- Displays success count

---

### **Step 6: Other Emails (Ignored)**

- View newsletters, promotions, FYI emails
- Table shows: #, From, Subject, Priority, Reason
- No actions needed - informational only

---

## 🔍 Advanced Features

### **Priority Filtering**

**Sidebar Filter:**
```
🔍 Filters
Priority: [LOW] [NORMAL] [HIGH]
```

**Use Cases:**
- Uncheck LOW → Hide newsletters/spam
- Select only HIGH → Focus on urgent emails
- Mix and match for custom views

---

### **AI Time Extraction**

The AI automatically extracts dates and times from email body:

**Examples:**

| Email Body | Extracted |
|------------|-----------|
| "Meet on 27-12-2025 at 4pm" | Date: 2025-12-27<br>Time: 16:00-16:30 IST |
| "December 25 at 2:30 PM" | Date: 2025-12-25<br>Time: 14:30-15:00 IST |
| "Tomorrow at 10am" | Date: (calculated)<br>Time: 10:00-10:30 IST |

**Supported Formats:**
- Dates: DD-MM-YYYY, Month DD, "tomorrow", "next Monday"
- Times: 4pm, 4:00 PM, 16:00, "at 4", "4 o'clock"

---

### **Conflict Detection Logic**

**How It Works:**
1. Checks Google Calendar for existing events
2. Compares requested time slot
3. If conflict found:
   - Shows warning with conflicting event names
   - Offers options to user

**Bulk Scheduling:**
- Auto-resolves conflicts
- Finds next available 30-minute slot
- Checks up to 24 hours ahead
- Notifies attendee of time change

---

## 🐛 Debugging Features

### **AI Extracted Time Info**

In each meeting email, expand **"🔍 AI Extracted Time Info (Debug)"**:

```json
{
  "date": "2025-12-27",
  "start_time": "2025-12-27T16:00:00",
  "end_time": "2025-12-27T16:30:00"
}
```

**What to Check:**
- ✅ start_time shows 16:00 for 4pm → AI correct
- ❌ start_time shows wrong time → AI extraction issue

### **Console Debug Output**

Check terminal for detailed logs:

```
[DEBUG] AI Extracted from email:
  Subject: Schedule meeting for demo
  Body: Schedule meeting for demo on 27-12-2025 at 4pm
  Extracted date: 2025-12-27
  Extracted start_time: 2025-12-27T16:00:00
  Extracted end_time: 2025-12-27T16:30:00

[DEBUG] Converting IST to UTC: 2025-12-27T16:00:00 (IST) → 2025-12-27T10:30:00Z (UTC)
```

---

## 📝 Email Classification Rules

### **SCHEDULE_MEET**
- Meeting requests
- "Let's discuss", "Can we connect"
- Complex issues requiring conversation
- Explicit meeting mentions

### **REPLY**
- Questions
- Requests needing response
- Deadlines
- Action items

### **IGNORE**
- Newsletters
- Promotional emails
- Shipping updates
- FYI/informational emails
- Automated notifications

---

## 🎨 Priority Levels

### **HIGH Priority**
- Urgent requests with deadlines
- Important meetings
- Critical issues
- Time-sensitive matters
- Emails from key stakeholders

### **NORMAL Priority**
- Regular questions
- Standard meeting requests
- General inquiries
- Follow-ups

### **LOW Priority**
- Newsletters
- Promotions
- Non-urgent updates
- Automated messages

---

## 🌍 Timezone Handling

**Storage:** All times stored in UTC in Google Calendar

**Display:** Automatically converted to IST (Indian Standard Time)

**Conversion Flow:**
```
Email: "4pm" 
  ↓
AI: 16:00 IST
  ↓
Storage: 10:30 UTC (Google Calendar)
  ↓
Display: 04:00 PM IST (Dashboard)
```

---

## 🔧 Troubleshooting

### **Issue: Wrong Time Scheduled**

**Check:**
1. Expand email → View "AI Extracted Time Info"
2. Verify start_time shows correct 24-hour format
3. Check console debug output
4. Ensure email clearly states time (e.g., "4pm" not "4")

**Fix:**
- Make email body more explicit: "27-12-2025 at 4:00 PM"
- AI works best with clear date/time formats

---

### **Issue: Meeting Not in Calendar**

**Check:**
1. Verify you're looking at primary Google Calendar
2. Check calendar permissions
3. Look for console errors
4. Verify credentials.json is valid

**Fix:**
- Re-authenticate: Delete `token.pickle` and restart
- Check Google Calendar API is enabled
- Verify calendar sharing settings

---

### **Issue: Conflict Detection Not Working**

**Check:**
1. Console shows "[DEBUG] Checking calendar..."
2. Verify check_conflicts=True in code
3. Check calendar API permissions

**Fix:**
- Ensure Calendar API has read permissions
- Check if events are in "primary" calendar

---

## 📊 Performance Tips

### **Optimize Email Fetching**
- Start with 10-20 emails for testing
- Increase to 50 for production use
- Processing time: ~2-3 seconds per email

### **Bulk Operations**
- Use bulk scheduling for 3+ meetings
- Use bulk replies for 5+ responses
- Saves time vs individual actions

### **Priority Filtering**
- Filter out LOW priority to focus on important emails
- Use HIGH filter for urgent-only view
- Reduces cognitive load

---

## 🎯 Demo Script (5 Minutes)

### **Minute 1: Introduction**
"This is an AI-powered email management system that automatically classifies emails and takes actions."

### **Minute 2: Fetch & Classify**
1. Navigate to Dashboard
2. Set slider to 20 emails
3. Click "Fetch & Classify Emails"
4. Show progress bar and processing

### **Minute 3: Meetings**
1. Show summary metrics
2. Expand a meeting email
3. Show AI extracted time
4. Schedule meeting
5. Show conflict detection (if applicable)
6. Display scheduled meeting details in IST

### **Minute 4: Replies**
1. Show reply section
2. Expand an email
3. Show AI-generated reply
4. Edit if needed
5. Send reply
6. Show bulk reply option

### **Minute 5: Wrap-up**
1. Show other/ignored emails
2. Demonstrate priority filtering
3. Show bulk operations
4. Highlight time saved

---

## 📚 API Usage

### **Gmail API**
- Fetch emails: `users().messages().list()`
- Get email details: `users().messages().get()`
- Send replies: `users().messages().send()`

### **Google Calendar API**
- Create events: `events().insert()`
- Check availability: `events().list()`
- Add Google Meet: `conferenceData`

### **Groq API**
- Model: LLaMA 3.3 70B Versatile
- Temperature: 0.2 (consistent results)
- JSON output mode

---

## 🔐 Security Notes

- Credentials stored locally in `credentials.json`
- OAuth tokens in `token.pickle`
- API keys in `.env` file (not committed to git)
- All communication over HTTPS
- No email data stored permanently

---

## 📞 Support

**Common Issues:**
- Authentication errors → Delete `token.pickle`, restart
- API rate limits → Reduce email fetch count
- Wrong timezone → Check IST conversion in code
- Missing meetings → Verify calendar permissions

**Debug Mode:**
- Check console output for detailed logs
- Use "AI Extracted Time Info" in dashboard
- Enable verbose logging if needed

---

## 🎉 Success Metrics

After using the dashboard:
- ✅ 20 emails processed in ~60 seconds
- ✅ 3 meetings scheduled automatically
- ✅ 8 replies sent with one click
- ✅ 9 newsletters filtered out
- ✅ Zero manual email reading required

**Time Saved:** ~30-45 minutes per session!

---

## 📝 Next Steps

1. **Customize AI Prompts** - Edit `agent.py` for your use case
2. **Add More Actions** - Extend with labels, forwarding, etc.
3. **Integrate Other Services** - Slack, Teams, etc.
4. **Train on Your Data** - Fine-tune for your email patterns
5. **Add Analytics** - Track response times, meeting stats

---

## 🏁 Conclusion

The Smart Inbox Agent transforms email management from a manual, time-consuming task into an automated, intelligent workflow. With AI-powered classification, conflict detection, and bulk operations, you can process dozens of emails in minutes instead of hours.

**Key Takeaway:** Let AI handle the routine, you focus on what matters.

---

*Last Updated: December 2025*
*Version: 2.0*
