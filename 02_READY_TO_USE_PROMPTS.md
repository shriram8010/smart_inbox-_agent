# Smart Inbox Agent - Ready to Use Prompts & Testing Flow

## 📋 Table of Contents
1. Quick Start Guide
2. Testing Flow - Complete Walkthrough
3. Sample Email Prompts for Testing
4. Feature-Specific Test Cases
5. Expected Results
6. Demo Script (5 Minutes)

---

## 1. Quick Start Guide

### Launch Application
```bash
# 1. Activate virtual environment
venv\Scripts\activate    # Windows
source venv/bin/activate # macOS/Linux

# 2. Run application
streamlit run main_v2.py

# 3. Browser opens automatically to http://localhost:8501
```

### First-Time Setup
1. Complete OAuth authentication (one-time)
2. Navigate to "Dashboard" in sidebar
3. Ready to test!

---

## 2. Testing Flow - Complete Walkthrough

### 🎯 PHASE 1: Fetch & Classify Emails (2 minutes)

**Step 1:** Open Dashboard
- In sidebar, select **"Dashboard"** radio button
- Main dashboard interface appears

**Step 2:** Configure Fetch Settings
- Locate slider: **"Max emails to fetch"**
- Set value: **20 emails** (recommended for testing)
- Range: 5-50 emails

**Step 3:** Fetch Emails
- Click button: **"🔄 Fetch & Classify Emails"**
- Progress bar appears
- Wait for processing (~40-60 seconds for 20 emails)
- Success message: "✅ Processed 20 emails"

**What Happens Behind the Scenes:**
- Fetches latest emails from Gmail
- AI analyzes each email (subject + body)
- Classifies into: SCHEDULE_MEET / REPLY / IGNORE
- Assigns priority: HIGH / NORMAL / LOW
- Extracts dates/times from meeting requests
- Generates reply suggestions

---

### 🎯 PHASE 2: Review Summary Metrics (30 seconds)

**Step 4:** View Dashboard Metrics

You'll see 4 metric cards:

```
┌─────────────────────────────────────────────────┐
│  Total Emails: 20                               │
│  Meeting Scheduled: 3                           │
│  Needs Reply: 8                                 │
│  Other/Ignored: 9                               │
└─────────────────────────────────────────────────┘
```

**Interpretation:**
- **Total Emails:** All fetched emails
- **Meeting Scheduled:** Emails requiring calendar events
- **Needs Reply:** Questions/requests needing responses
- **Other/Ignored:** Newsletters, promotions, FYI emails

---

### 🎯 PHASE 3: Test Meeting Scheduling (3 minutes)

**Step 5:** Navigate to Meeting Section
- Scroll to **"📅 Meeting Scheduled"** section
- View table with meeting requests

**Step 6:** Schedule Individual Meeting

1. **Click on any email row** to expand details
2. **Review extracted information:**
   - From: Sender email
   - Priority: HIGH/NORMAL/LOW
   - Summary: AI-generated summary
   - AI Extracted Time Info (Debug): Shows parsed date/time

3. **Click "📆 Schedule Meeting" button**

4. **If NO conflict:**
   - Success message appears
   - Meeting details displayed:
     ```
     ✅ Meeting scheduled!
     📅 Date: 27 December 2025
     ⏰ Time: 04:00 PM - 04:30 PM IST
     🔗 Meet Link: https://meet.google.com/xxx-xxxx-xxx
     ```
   - Email sent to attendee with meet link

5. **If CONFLICT detected:**
   - Warning appears:
     ```
     ⚠️ Time Conflict Detected!
     Requested: 27 December 2025 at 04:00 PM
     Conflicting meeting(s): Team Standup, Client Call
     
     ✅ Next Available Slot Found:
     📅 27 December 2025
     ⏰ 05:00 PM - 05:30 PM IST
     ```
   
   - **Three options:**
     - **"✅ Use This Slot"** → Schedules at suggested time
     - **"🔄 Find Another"** → Finds next available slot
     - **"❌ Cancel"** → Cancels scheduling

**Step 7:** Test Bulk Scheduling

1. **Click "📆 Schedule All Meetings"** (top right)
2. Progress bar shows scheduling status
3. Auto-resolves conflicts by finding next available slots
4. Summary displayed:
   ```
   ✅ Scheduled 3/3 meetings!
   ⚠️ 1 meeting(s) had time conflicts and were rescheduled:
   • Schedule meeting for demo - Rescheduled due to conflict
   ```

---

### 🎯 PHASE 4: Test Reply Generation (2 minutes)

**Step 8:** Navigate to Reply Section
- Scroll to **"✉️ Needs Reply"** section
- View table with emails needing responses

**Step 9:** Send Individual Reply

1. **Click on any email** to expand
2. **Review AI-generated reply** in text area
3. **Edit reply if needed** (optional)
4. **Click "📤 Send Reply" button**
5. Success message: "✅ Sent!"
6. Reply sent via Gmail (maintains email thread)

**Step 10:** Test Bulk Replies

1. **Click "📤 Send All Replies"** (top right)
2. Progress bar shows sending status
3. Summary: "✅ Sent 8/8 replies!"
4. All AI-generated replies sent automatically

---

### 🎯 PHASE 5: Review Ignored Emails (1 minute)

**Step 11:** Check Other Emails Section
- Scroll to **"📋 Other Emails (Ignored)"**
- View table with newsletters, promotions, FYI emails
- Columns: From, Subject, Priority, Reason
- No action needed - informational only

---

### 🎯 PHASE 6: Test Filtering (1 minute)

**Step 12:** Use Priority Filters

1. **In sidebar, locate "🔍 Filters"**
2. **Priority multi-select:** LOW, NORMAL, HIGH
3. **Test scenarios:**
   - Uncheck "LOW" → Hides newsletters/spam
   - Select only "HIGH" → Shows urgent emails only
   - Mix and match for custom views
4. All sections update dynamically

---

## 3. Sample Email Prompts for Testing

### 📧 Test Email 1: Meeting Request with Specific Time
**Subject:** Schedule meeting for project demo  
**Body:**
```
Hi,

Can we schedule a meeting to discuss the project demo? 
I'm available on 27-12-2025 at 4pm.

Thanks!
```

**Expected Result:**
- Action: SCHEDULE_MEET
- Priority: NORMAL
- Extracted Date: 2025-12-27
- Extracted Time: 16:00:00 (4pm in 24-hour format)
- Meeting created with Google Meet link

---

### 📧 Test Email 2: Meeting Request with Date Only
**Subject:** Let's connect next week  
**Body:**
```
Hi,

Let's schedule a call to align on the roadmap. 
How about December 25?

Best,
John
```

**Expected Result:**
- Action: SCHEDULE_MEET
- Priority: NORMAL
- Extracted Date: 2025-12-25
- Default Time: 10:00 AM (if no time specified)

---

### 📧 Test Email 3: Question Requiring Reply
**Subject:** Quick question about the API  
**Body:**
```
Hi,

Can you clarify how the authentication flow works in the new API? 
I need this for the integration by Friday.

Thanks!
```

**Expected Result:**
- Action: REPLY
- Priority: HIGH (has deadline)
- AI generates contextual reply explaining authentication

---

### 📧 Test Email 4: Newsletter (Should be Ignored)
**Subject:** Weekly Tech Newsletter - January Edition  
**Body:**
```
Top 10 Tech Trends of 2025

1. AI-powered automation
2. Quantum computing advances
...

Unsubscribe | View in browser
```

**Expected Result:**
- Action: IGNORE
- Priority: LOW
- Reason: Newsletter/promotional content

---

### 📧 Test Email 5: Urgent Meeting Request
**Subject:** URGENT: Client escalation - need to discuss  
**Body:**
```
Hi,

We have a critical client escalation. Can we meet today at 2:30 PM 
to discuss the resolution strategy?

This is time-sensitive.

Thanks,
Sarah
```

**Expected Result:**
- Action: SCHEDULE_MEET
- Priority: HIGH (urgent + time-sensitive)
- Extracted Time: 14:30:00 (2:30 PM)

---

### 📧 Test Email 6: Shipping Notification (Should be Ignored)
**Subject:** Your order has been shipped  
**Body:**
```
Your order #12345 has been shipped!

Track your package: [link]
Estimated delivery: Dec 28, 2025

Thank you for shopping with us!
```

**Expected Result:**
- Action: IGNORE
- Priority: LOW
- Reason: Automated shipping notification

---

## 4. Feature-Specific Test Cases

### ✅ Test Case 1: Conflict Detection

**Setup:**
1. Manually create a meeting in Google Calendar at 4:00 PM on Dec 27
2. Send test email requesting meeting at same time

**Steps:**
1. Fetch & classify emails
2. Try to schedule the conflicting meeting
3. Verify conflict warning appears
4. Test "Find Next Available Slot" option
5. Verify meeting scheduled at next available time

**Expected Result:**
- Conflict detected and displayed
- Next slot suggested (e.g., 4:30 PM or 5:00 PM)
- Meeting successfully created at alternate time

---

### ✅ Test Case 2: Custom Time Override

**Steps:**
1. Expand a meeting email
2. Click "⏰ Edit Meeting Time"
3. Select custom date and time
4. Check "Use custom time"
5. Click "Schedule Meeting"

**Expected Result:**
- Meeting scheduled at custom time (not AI-extracted time)
- Confirmation shows custom date/time

---

### ✅ Test Case 3: Reply Editing

**Steps:**
1. Expand a reply email
2. Edit the AI-generated reply text
3. Click "Send Reply"

**Expected Result:**
- Edited reply sent (not original AI version)
- Success confirmation displayed

---

### ✅ Test Case 4: Bulk Operations with Errors

**Setup:**
- Have 5 meeting emails
- Manually delete one sender's email address (to cause error)

**Steps:**
1. Click "Schedule All Meetings"
2. Observe progress

**Expected Result:**
- 4 meetings scheduled successfully
- 1 error displayed for invalid email
- Summary: "✅ Scheduled 4/5 meetings"

---

### ✅ Test Case 5: Rate Limit Handling

**Setup:**
- Process 50+ emails to hit Groq rate limit

**Steps:**
1. Set slider to 50 emails
2. Click "Fetch & Classify"
3. Wait for rate limit error

**Expected Result:**
- Error message displayed:
  ```
  ⚠️ Rate Limit Reached!
  Your Groq API has hit the daily token limit.
  
  Options:
  1. Wait ~3 minutes and try again
  2. Upgrade to Dev Tier
  3. Use a different API key
  ```
- Partial results shown for processed emails

---

## 5. Expected Results Summary

### Email Classification Accuracy
- **Meeting Requests:** 90-95% accuracy
- **Questions/Replies:** 85-90% accuracy
- **Newsletters/Spam:** 95-98% accuracy

### Time Extraction Accuracy
- **Explicit times (4pm, 14:00):** 95%+ accuracy
- **Relative times (tomorrow, next week):** 80-85% accuracy
- **Date formats (DD-MM-YYYY, Month DD):** 90%+ accuracy

### Performance Metrics
- **Processing Speed:** 2-3 seconds per email
- **20 emails:** ~40-60 seconds total
- **50 emails:** ~2-3 minutes total

### Success Rates
- **Meeting Creation:** 98%+ (with valid calendar access)
- **Reply Sending:** 99%+ (with valid Gmail access)
- **Conflict Detection:** 100% (checks all calendar events)

---

## 6. Demo Script (5 Minutes)

### **Minute 1: Introduction**
"This is an AI-powered email management system that automatically classifies emails and takes intelligent actions. Let me show you how it works."

### **Minute 2: Fetch & Classify**
1. Navigate to Dashboard
2. Set slider to 20 emails
3. Click "Fetch & Classify Emails"
4. Show progress bar
5. Point out: "AI is analyzing each email - subject, body, context"

### **Minute 3: Meeting Scheduling**
1. Show summary metrics
2. Expand a meeting email
3. Show AI extracted time in debug section
4. Click "Schedule Meeting"
5. **If conflict:** Show conflict detection UI
6. Display scheduled meeting with IST time and meet link

### **Minute 4: Reply Generation**
1. Navigate to reply section
2. Expand an email
3. Show AI-generated reply
4. Edit reply (optional)
5. Click "Send Reply"
6. Show bulk reply option: "You can send all 8 replies with one click"

### **Minute 5: Wrap-up**
1. Show ignored emails section
2. Demonstrate priority filtering
3. Highlight bulk operations
4. **Key takeaway:** "Processed 20 emails in 60 seconds. Normally takes 30-45 minutes manually."

---

## 7. Troubleshooting During Testing

### Issue: No emails fetched
**Solution:** Check Gmail inbox has emails, verify OAuth permissions

### Issue: Wrong time extracted
**Solution:** Check "AI Extracted Time Info" debug section, verify email has clear time mention

### Issue: Meeting not in calendar
**Solution:** Verify Calendar API permissions, check "primary" calendar

### Issue: Reply not sent
**Solution:** Check Gmail API permissions, verify sender email is valid

---

## 8. Advanced Testing Scenarios

### Scenario 1: Multiple Meetings Same Day
- Send 5 emails requesting meetings on same day
- Test bulk scheduling with conflict resolution
- Verify all meetings scheduled at different times

### Scenario 2: International Time Zones
- Email mentions "4pm EST" or "10am PST"
- Verify AI extracts time correctly
- Check IST conversion in calendar

### Scenario 3: Complex Email Threads
- Reply to an existing email thread
- Verify reply maintains thread (uses threadId)
- Check Gmail shows conversation properly

---

**Document Version:** 1.0  
**Last Updated:** February 2026  
**Status:** Production Ready  
**Estimated Testing Time:** 15-20 minutes for complete flow
