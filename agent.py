import os
import json
from groq import Groq
from dotenv import load_dotenv

# --------------------------------------------------
# Load environment variables
# --------------------------------------------------
load_dotenv()

# Explicitly read API key (important for Windows + Streamlit)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise RuntimeError(
        "❌ GROQ_API_KEY not found. "
        "Make sure .env file exists and contains GROQ_API_KEY=your_key"
    )

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

# --------------------------------------------------
# System prompt (STRICT JSON, agentic decision)
# --------------------------------------------------
SYSTEM_PROMPT = """
You are a smart inbox agent.

Your task:
- Read the email
- Decide the best action: IGNORE, REPLY, or SCHEDULE_MEET
- Generate a reply ONLY if action is REPLY or SCHEDULE_MEET

Actions:
- IGNORE: newsletters, promotions, shipping updates, FYI emails
- REPLY: questions, deadlines, requests that can be resolved via email
- SCHEDULE_MEET: requests to discuss, connect, align, call, or resolve complex issues

Rules for extracting meeting times:
- ALWAYS look for dates in the email body (e.g., "25-12-2025", "December 25", "tomorrow", "next Monday")
- ALWAYS look for times (e.g., "4 pm", "4:00 PM", "16:00", "at 4", "4 o'clock")
- Convert dates to YYYY-MM-DD format
- Convert times to ISO 8601 format with timezone (e.g., 4pm = 16:00:00Z)
- If only start time given, assume 30-minute duration (4pm = 16:00 to 16:30)
- If date mentioned without time, use 10:00 AM as default
- Extract ALL date/time information you can find in the email

Priority Rules:
- HIGH: Urgent requests, deadlines, important meetings, critical issues
- NORMAL: Regular questions, standard meetings, general inquiries
- LOW: Newsletters, promotions, FYI emails, automated messages

Output Rules:
- Be concise and professional
- Output VALID JSON ONLY
- Do NOT include markdown, explanations, or extra text
"""


# --------------------------------------------------
# Agent function
# --------------------------------------------------
def run_agent(email: dict) -> dict:
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # fast + free tier friendly
            temperature=0.2,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"From: {email.get('from', '')}\n"
                        f"Subject: {email.get('subject', '')}\n"
                        f"Body: {email.get('body', '')}\n"
                        "\n"
                        "Return JSON with extracted date and time:\n"
                        "{\n"
                        "  \"action\": \"IGNORE | REPLY | SCHEDULE_MEET\",\n"
                        "  \"priority\": \"LOW | NORMAL | HIGH\",\n"
                        "  \"reason\": \"\",\n"
                        "  \"summary\": \"\",\n"
                        "  \"reply\": \"\",\n"
                        "  \"date\": \"\",         // YYYY-MM-DD format (e.g., 2025-12-27)\n"
                        "  \"start_time\": \"\",   // ISO 8601 format: YYYY-MM-DDTHH:MM:SS (e.g., 2025-12-27T16:00:00 for 4pm)\n"
                        "  \"end_time\": \"\"      // ISO 8601 format: YYYY-MM-DDTHH:MM:SS (e.g., 2025-12-27T16:30:00 for 4:30pm)\n"
                        "}\n"
                        "\n"
                        "IMPORTANT: If email mentions '4pm' or '4 PM', use 16:00:00 in 24-hour format.\n"
                        "Examples:\n"
                        "- '27-12-2025 at 4pm' → start_time: '2025-12-27T16:00:00', end_time: '2025-12-27T16:30:00'\n"
                        "- 'December 27 at 2:30 PM' → start_time: '2025-12-27T14:30:00', end_time: '2025-12-27T15:00:00'\n"
                        "- 'tomorrow at 10am' → calculate tomorrow's date, start_time: 'YYYY-MM-DDT10:00:00'\n"
                    )
                }
            ],
        )

        raw_output = response.choices[0].message.content.strip()

        # --------------------------------------------------
        # SAFETY: JSON extraction (never crash demo)
        # --------------------------------------------------
        try:
            # If model adds text, extract JSON safely
            if not raw_output.startswith("{"):
                raw_output = raw_output[
                    raw_output.find("{") : raw_output.rfind("}") + 1
                ]

            # Parse JSON
            data = json.loads(raw_output)
            
            # Debug: Print what AI extracted
            print(f"\n[DEBUG] AI Extracted from email:")
            print(f"  Subject: {email.get('subject', '')[:50]}")
            print(f"  Body: {email.get('body', '')[:100]}")
            print(f"  Extracted date: {data.get('date', 'NONE')}")
            print(f"  Extracted start_time: {data.get('start_time', 'NONE')}")
            print(f"  Extracted end_time: {data.get('end_time', 'NONE')}\n")

            # Ensure all expected keys are present in the output
            for k in ["action", "priority", "reason", "summary", "reply", "date", "start_time", "end_time"]:
                if k not in data:
                    data[k] = ""
            
            # Normalize action to ensure it's one of the three valid values
            action = str(data.get("action", "")).upper().strip()
            if action not in ["IGNORE", "REPLY", "SCHEDULE_MEET"]:
                # Default to IGNORE if action is invalid
                data["action"] = "IGNORE"
                data["reason"] = f"Invalid action '{action}' normalized to IGNORE. {data.get('reason', '')}"
            else:
                data["action"] = action
            
            return data

        except Exception as e:
            print(f"[DEBUG] JSON parsing failed: {e}")
            # Absolute fallback – demo must never break
            return {
                "action": "IGNORE",
                "priority": "LOW",
                "reason": "Model returned invalid JSON",
                "summary": raw_output[:200],
                "reply": "",
                "date": "",
                "start_time": "",
                "end_time": ""
            }
    
    except Exception as e:
        error_msg = str(e)
        print(f"[ERROR] Groq API call failed: {error_msg}")
        
        # Check if it's a rate limit error
        if "rate_limit" in error_msg.lower() or "429" in error_msg:
            return {
                "action": "IGNORE",
                "priority": "LOW",
                "reason": "⚠️ Rate limit reached. Please wait a few minutes or upgrade your Groq plan.",
                "summary": f"Email from {email.get('from', 'Unknown')}: {email.get('subject', 'No subject')[:100]}",
                "reply": "",
                "date": "",
                "start_time": "",
                "end_time": ""
            }
        else:
            # Other API errors
            return {
                "action": "IGNORE",
                "priority": "LOW",
                "reason": f"API Error: {error_msg[:100]}",
                "summary": f"Email from {email.get('from', 'Unknown')}: {email.get('subject', 'No subject')[:100]}",
                "reply": "",
                "date": "",
                "start_time": "",
                "end_time": ""
            }