# Smart Inbox Agent - Setup Document

## 📋 Table of Contents
1. Prerequisites
2. Installation Steps
3. API Configuration
4. Google Cloud Setup
5. Environment Configuration
6. Running the Application
7. Troubleshooting

---

## 1. Prerequisites

### System Requirements
- **Operating System:** Windows 10/11, macOS, or Linux
- **Python Version:** Python 3.8 or higher
- **Internet Connection:** Required for API calls
- **Browser:** Chrome, Firefox, or Edge (for OAuth authentication)

### Required Accounts
- **Gmail Account:** For email access
- **Google Cloud Account:** For Gmail & Calendar API access
- **Groq Account:** For AI processing (free tier available)

---

## 2. Installation Steps

### Step 2.1: Clone the Repository
```bash
# Navigate to your desired folder
cd D:\AI-POCs

# Clone the repository
git clone <repository-url>
cd smart-inbox-agent
```

### Step 2.2: Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# For Windows:
venv\Scripts\activate

# For macOS/Linux:
source venv/bin/activate
```

### Step 2.3: Install Dependencies
```bash
# Install all required packages
pip install -r requirements.txt
```

**Dependencies installed:**
- streamlit (Web UI framework)
- pandas (Data processing)
- google-api-python-client (Gmail & Calendar APIs)
- google-auth, google-auth-oauthlib, google-auth-httplib2 (Authentication)
- groq (AI model API)
- python-dotenv (Environment variables)

---

## 3. API Configuration

### Step 3.1: Groq API Setup

1. **Create Groq Account:**
   - Visit: https://console.groq.com/
   - Sign up for free account
   - Navigate to "API Keys" section

2. **Generate API Key:**
   - Click "Create API Key"
   - Copy the generated key (starts with `gsk_`)
   - Save it securely (you'll need it in Step 5)

3. **Free Tier Limits:**
   - 100,000 tokens per day
   - ~30-50 emails can be processed
   - Resets every 24 hours

---

## 4. Google Cloud Setup

### Step 4.1: Create Google Cloud Project

1. **Go to Google Cloud Console:**
   - Visit: https://console.cloud.google.com/
   - Sign in with your Gmail account

2. **Create New Project:**
   - Click "Select a project" → "New Project"
   - Project Name: `Smart-Inbox-Agent`
   - Click "Create"

### Step 4.2: Enable Required APIs

1. **Enable Gmail API:**
   - Go to "APIs & Services" → "Library"
   - Search for "Gmail API"
   - Click "Enable"

2. **Enable Google Calendar API:**
   - Search for "Google Calendar API"
   - Click "Enable"

### Step 4.3: Create OAuth Credentials

1. **Configure OAuth Consent Screen:**
   - Go to "APIs & Services" → "OAuth consent screen"
   - Select "External" → Click "Create"
   - Fill in required fields:
     - App name: `Smart Inbox Agent`
     - User support email: Your email
     - Developer contact: Your email
   - Click "Save and Continue"
   - Skip "Scopes" section → Click "Save and Continue"
   - Add Test Users: Add your Gmail address
   - Click "Save and Continue"

2. **Create OAuth Client ID:**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth client ID"
   - Application type: "Desktop app"
   - Name: `Smart Inbox Desktop Client`
   - Click "Create"

3. **Download Credentials:**
   - Click "Download JSON" button
   - Rename downloaded file to `credentials.json`
   - Move `credentials.json` to project root folder:
     ```
     smart-inbox-agent/
     └── credentials.json  ← Place here
     ```

---

## 5. Environment Configuration

### Step 5.1: Create .env File

1. **Create file named `.env` in project root:**
   ```
   smart-inbox-agent/
   └── .env  ← Create this file
   ```

2. **Add Groq API Key:**
   ```env
   GROQ_API_KEY=gsk_your_actual_api_key_here
   ```

3. **Save the file**

### Step 5.2: Verify File Structure

Your project should look like this:
```
smart-inbox-agent/
├── venv/                    (virtual environment)
├── credentials.json         ← Google OAuth credentials
├── .env                     ← Groq API key
├── requirements.txt
├── agent.py
├── auth.py
├── gmail_client.py
├── calendar_client.py
├── main_v2.py
└── (other files)
```

---

## 6. Running the Application

### Step 6.1: First-Time Authentication

1. **Activate Virtual Environment:**
   ```bash
   # Windows:
   venv\Scripts\activate
   
   # macOS/Linux:
   source venv/bin/activate
   ```

2. **Run the Application:**
   ```bash
   streamlit run main_v2.py
   ```

3. **OAuth Authentication Flow:**
   - Browser will automatically open
   - You'll see "Google hasn't verified this app" warning
   - Click "Advanced" → "Go to Smart Inbox Agent (unsafe)"
   - Click "Allow" for Gmail permissions
   - Click "Allow" for Calendar permissions
   - Browser will show "You may close this window"
   - Return to terminal

4. **Token Storage:**
   - A `token.pickle` file will be created
   - This stores your authentication
   - You won't need to authenticate again unless you delete this file

### Step 6.2: Access the Application

1. **Application URL:**
   - Automatically opens: `http://localhost:8501`
   - Or manually visit this URL in your browser

2. **Interface:**
   - Sidebar: Navigation and controls
   - Main area: Email dashboard

---

## 7. Troubleshooting

### Issue 1: "GROQ_API_KEY not found"
**Solution:**
- Verify `.env` file exists in project root
- Check file content: `GROQ_API_KEY=gsk_...`
- No spaces around `=` sign
- Restart the application

### Issue 2: "credentials.json not found"
**Solution:**
- Download credentials from Google Cloud Console
- Rename to exactly `credentials.json`
- Place in project root folder (same level as main_v2.py)

### Issue 3: "Token has been expired or revoked"
**Solution:**
```bash
# Delete the token file
del token.pickle    # Windows
rm token.pickle     # macOS/Linux

# Restart application - will re-authenticate
streamlit run main_v2.py
```

### Issue 4: "Rate limit reached"
**Solution:**
- Groq free tier: 100,000 tokens/day
- Wait 3-5 minutes and try again
- Or upgrade to Dev tier at https://console.groq.com/settings/billing
- Or use fewer emails (reduce slider value)

### Issue 5: "No module named 'streamlit'"
**Solution:**
```bash
# Ensure virtual environment is activated
venv\Scripts\activate    # Windows
source venv/bin/activate # macOS/Linux

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue 6: Port 8501 already in use
**Solution:**
```bash
# Use different port
streamlit run main_v2.py --server.port 8502
```

### Issue 7: "Access blocked: This app's request is invalid"
**Solution:**
- Go to Google Cloud Console
- OAuth consent screen → Add your email to "Test users"
- Try authentication again

---

## 8. Verification Checklist

Before testing, verify:

- [ ] Python 3.8+ installed (`python --version`)
- [ ] Virtual environment activated (see `(venv)` in terminal)
- [ ] All dependencies installed (`pip list`)
- [ ] `credentials.json` file present
- [ ] `.env` file with valid Groq API key
- [ ] Gmail API enabled in Google Cloud
- [ ] Calendar API enabled in Google Cloud
- [ ] Test user added in OAuth consent screen
- [ ] Application runs without errors
- [ ] Browser opens to `http://localhost:8501`
- [ ] OAuth authentication completed
- [ ] `token.pickle` file created

---

## 9. Next Steps

Once setup is complete:
1. Refer to **"02_READY_TO_USE_PROMPTS.md"** for testing flows
2. Refer to **"03_POC_SUMMARY.md"** for feature overview

---

## 10. Support Resources

- **Groq Documentation:** https://console.groq.com/docs
- **Gmail API Docs:** https://developers.google.com/gmail/api
- **Calendar API Docs:** https://developers.google.com/calendar/api
- **Streamlit Docs:** https://docs.streamlit.io

---

**Document Version:** 1.0  
**Last Updated:** February 2026  
**Status:** Production Ready
