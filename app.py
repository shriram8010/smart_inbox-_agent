import streamlit as st
from gmail_client import fetch_emails, send_reply
from agent import run_agent
from calendar_client import create_meet   # 👈 NEW

st.set_page_config(layout="wide")

# Header with dashboard link
col_title, col_button = st.columns([3, 1])
with col_title:
    st.title("📬 Smart Inbox Agent")
with col_button:
    st.markdown("###")  # Spacing
    if st.button("📊 Open Dashboard", type="primary"):
        st.info("💡 Run the dashboard in a new terminal:\n\n`streamlit run dashboard.py --server.port 8502`")
        st.markdown("[Click here if dashboard is already running](http://localhost:8502)", unsafe_allow_html=True)

# ---- SESSION STATE INIT ----
if "agent_result" not in st.session_state:
    st.session_state.agent_result = None

emails = fetch_emails()

if not emails:
    st.warning("No emails found")
    st.stop()

col1, col2 = st.columns([1, 2])

# ---------------- LEFT PANE ----------------
with col1:
    st.subheader("Inbox")
    selected = st.radio(
        "Select Email",
        emails,
        format_func=lambda e: e["subject"]
    )

# ---------------- RIGHT PANE ----------------
with col2:
    st.subheader("Email Content")
    st.markdown(f"**From:** {selected['from']}")
    st.markdown(f"**Subject:** {selected['subject']}")
    st.write(selected["body"])

    auto_send = st.checkbox("🚀 Auto-send reply when needed", value=False)

    # ---- RUN AGENT ----
    if st.button("🤖 Run Smart Agent"):
        with st.spinner("Agent thinking..."):
            st.session_state.agent_result = run_agent(selected)

    result = st.session_state.agent_result

    if result:
        st.success(f"Action: {result['action']}")

        st.markdown("### 🧠 Summary")
        st.write(result.get("summary", ""))

        st.markdown("### 🚦 Priority")
        st.write(result.get("priority", ""))

        st.markdown("### 🤔 Reason")
        st.write(result.get("reason", ""))

        # ---------------- REPLY FLOW ----------------
        if result["action"] == "REPLY":
            st.markdown("### ✉️ Generated Reply")

            edited_reply = st.text_area(
                "Reply (you can edit before sending)",
                result.get("reply", ""),
                height=220
            )

            if auto_send and st.button("📤 Send Reply Automatically"):
                with st.spinner("Sending reply via Gmail..."):
                    send_reply(selected, edited_reply)
                st.success("✅ Reply sent successfully!")

        # ---------------- MEETING FLOW ----------------
        if result["action"] == "SCHEDULE_MEET":

            st.warning("📅 Agent decided a meeting is required")

            if st.button("📆 Schedule Google Meet"):
                # Use all three (date, start_time, end_time) only if all are present and non-empty
                date = result.get("date")
                start_time = result.get("start_time")
                end_time = result.get("end_time")
                if date and start_time and end_time:
                    # All present, use as is
                    pass
                elif date and not (start_time or end_time):
                    # Only date present, use default 10:00-10:30 UTC
                    start_time = f"{date}T10:00:00Z"
                    end_time = f"{date}T10:30:00Z"
                else:
                    # Not enough info, use defaults (by passing None)
                    start_time = None
                    end_time = None
                with st.spinner("Creating meeting..."):
                    meet_link = create_meet(
                        subject=selected["subject"],
                        description=selected["body"],
                        attendee_email=selected["from"],
                        start_time=start_time,
                        end_time=end_time
                    )
                    # Show extracted meeting details for verification
                    st.info(f"**Meeting details extracted:**\n- Date: {date or 'N/A'}\n- Start Time: {start_time or 'N/A'}\n- End Time: {end_time or 'N/A'}")

                    reply_text = f"""
    Hi,

    Thanks for reaching out. I’ve scheduled a short meeting so we can discuss this further.

    Google Meet link:
    {meet_link}

    Looking forward to connecting.
    """

                    send_reply(selected, reply_text)

                    st.success("✅ Meeting scheduled and invite sent!")
                    st.markdown(f"🔗 **Meet link:** {meet_link}")
