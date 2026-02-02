import streamlit as st

st.set_page_config(
    page_title="Smart Inbox Agent",
    page_icon="📬",
    layout="wide"
)

# Navigation
st.sidebar.title("📬 Smart Inbox Agent")
page = st.sidebar.radio(
    "Navigate",
    ["Single Email View", "Dashboard"],
    label_visibility="collapsed"
)

if page == "Single Email View":
    # Import and run single email view
    from gmail_client import fetch_emails, send_reply
    from agent import run_agent
    from calendar_client import create_meet
    
    st.title("📬 Smart Inbox Agent - Single Email View")
    
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
                    date = result.get("date")
                    start_time = result.get("start_time")
                    end_time = result.get("end_time")
                    if date and start_time and end_time:
                        pass
                    elif date and not (start_time or end_time):
                        start_time = f"{date}T10:00:00Z"
                        end_time = f"{date}T10:30:00Z"
                    else:
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
                        st.info(f"**Meeting details extracted:**\n- Date: {date or 'N/A'}\n- Start Time: {start_time or 'N/A'}\n- End Time: {end_time or 'N/A'}")
    
                        reply_text = f"""Hi,

Thanks for reaching out. I've scheduled a short meeting so we can discuss this further.

Google Meet link:
{meet_link}

Looking forward to connecting.
"""
    
                        send_reply(selected, reply_text)
    
                        st.success("✅ Meeting scheduled and invite sent!")
                        st.markdown(f"🔗 **Meet link:** {meet_link}")

elif page == "Dashboard":
    # Import and run dashboard
    import pandas as pd
    from gmail_client import fetch_emails, send_reply
    from agent import run_agent
    from calendar_client import create_meet
    from datetime import datetime
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
        .metric-card {
            background-color: #f0f2f6;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        .stDataFrame {
            font-size: 14px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.title("📊 Smart Inbox Dashboard")
    
    # Initialize session state
    if "processed_emails" not in st.session_state:
        st.session_state.processed_emails = []
    if "processing_done" not in st.session_state:
        st.session_state.processing_done = False
    
    # Sidebar controls
    with st.sidebar:
        st.header("⚙️ Controls")
        max_emails = st.slider("Max emails to fetch", 5, 50, 20)
        
        if st.button("🔄 Fetch & Classify Emails", type="primary"):
            with st.spinner("Fetching emails..."):
                emails = fetch_emails(max_results=max_emails)
            
            if emails:
                with st.spinner("Classifying emails with AI..."):
                    processed = []
                    progress_bar = st.progress(0)
                    for idx, email in enumerate(emails):
                        # Check if email is empty or has no meaningful content
                        if not email.get("body", "").strip() and not email.get("subject", "").strip():
                            # Auto-classify empty emails as IGNORE
                            result = {
                                "action": "IGNORE",
                                "priority": "LOW",
                                "reason": "Empty email with no content",
                                "summary": "No content to process",
                                "reply": "",
                                "date": "",
                                "start_time": "",
                                "end_time": ""
                            }
                        else:
                            # Process with AI
                            result = run_agent(email)
                        
                        processed.append({
                            **email,
                            **result
                        })
                        progress_bar.progress((idx + 1) / len(emails))
                    
                    st.session_state.processed_emails = processed
                    st.session_state.processing_done = True
                    st.success(f"✅ Processed {len(processed)} emails")
            else:
                st.warning("No emails found")
        
        st.divider()
        st.header("🔍 Filters")
        priority_filter = st.multiselect(
            "Priority",
            ["LOW", "NORMAL", "HIGH"],
            default=["LOW", "NORMAL", "HIGH"]
        )
    
    # Main dashboard
    if not st.session_state.processing_done:
        st.info("👈 Click 'Fetch & Classify Emails' in the sidebar to start")
        st.stop()
    
    emails_data = st.session_state.processed_emails
    
    if not emails_data:
        st.warning("No emails to display")
        st.stop()
    
    # Convert to DataFrame
    df = pd.DataFrame(emails_data)
    
    # Debug: Show unique actions to verify categorization
    unique_actions = df["action"].unique()
    
    # Apply filters
    df_filtered = df[df["priority"].isin(priority_filter)]
    
    # Categorize emails
    meeting_emails = df_filtered[df_filtered["action"] == "SCHEDULE_MEET"]
    replied_emails = df_filtered[df_filtered["action"] == "REPLY"]
    other_emails = df_filtered[df_filtered["action"] == "IGNORE"]
    
    # Validation: Check if all emails are categorized
    total_categorized = len(meeting_emails) + len(replied_emails) + len(other_emails)
    uncategorized = df_filtered[~df_filtered["action"].isin(["SCHEDULE_MEET", "REPLY", "IGNORE"])]
    
    # Summary Metrics
    st.header("📈 Summary Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Emails", len(df_filtered))
    with col2:
        st.metric("Meeting Scheduled", len(meeting_emails), 
                  delta=f"{len(meeting_emails)/len(df_filtered)*100:.1f}%" if len(df_filtered) > 0 else "0%")
    with col3:
        st.metric("Needs Reply", len(replied_emails),
                  delta=f"{len(replied_emails)/len(df_filtered)*100:.1f}%" if len(df_filtered) > 0 else "0%")
    with col4:
        st.metric("Other/Ignored", len(other_emails),
                  delta=f"{len(other_emails)/len(df_filtered)*100:.1f}%" if len(df_filtered) > 0 else "0%")
    
    # Show warning if counts don't match
    if total_categorized != len(df_filtered):
        st.warning(f"⚠️ Categorization mismatch: {len(df_filtered)} total emails, but only {total_categorized} categorized. Uncategorized actions: {uncategorized['action'].tolist()}")
    
    st.divider()
    
    # Meeting Scheduled Emails
    st.header("📅 Meeting Scheduled")
    if len(meeting_emails) > 0:
        meeting_display = meeting_emails[["from", "subject", "priority", "summary", "date", "start_time"]].copy()
        meeting_display.columns = ["From", "Subject", "Priority", "Summary", "Date", "Start Time"]
        
        st.dataframe(
            meeting_display,
            use_container_width=True,
            hide_index=True
        )
        
        # Action buttons for meetings
        with st.expander("🔧 Actions for Meeting Emails"):
            col_action1, col_action2 = st.columns(2)
            
            with col_action1:
                st.subheader("Schedule Individual Meeting")
                selected_meeting = st.selectbox(
                    "Select email to schedule meeting",
                    range(len(meeting_emails)),
                    format_func=lambda i: meeting_emails.iloc[i]["subject"],
                    key="individual_meeting"
                )
                
                if st.button("📆 Create Google Meet", key="single_meet"):
                    email = meeting_emails.iloc[selected_meeting]
                    date = email.get("date")
                    start_time = email.get("start_time")
                    end_time = email.get("end_time")
                    
                    if date and start_time and end_time:
                        pass
                    elif date and not (start_time or end_time):
                        start_time = f"{date}T10:00:00Z"
                        end_time = f"{date}T10:30:00Z"
                    else:
                        start_time = None
                        end_time = None
                    
                    with st.spinner("Creating meeting..."):
                        meet_link = create_meet(
                            subject=email["subject"],
                            description=email["body"],
                            attendee_email=email["from"],
                            start_time=start_time,
                            end_time=end_time,
                            check_conflicts=True  # Enable conflict checking for bulk scheduling
                        )
                        
                        reply_text = f"""Hi,

Thanks for reaching out. I've scheduled a meeting to discuss this further.

Google Meet link: {meet_link}

Looking forward to connecting.
"""
                        send_reply(email.to_dict(), reply_text)
                        st.success(f"✅ Meeting created: {meet_link}")
            
            with col_action2:
                st.subheader("Schedule All Meetings")
                st.info(f"📊 {len(meeting_emails)} meeting(s) to schedule")
                
                if st.button("📆 Create All Google Meets", type="primary", key="bulk_meet"):
                    success_count = 0
                    failed_count = 0
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for idx, (_, email) in enumerate(meeting_emails.iterrows()):
                        try:
                            status_text.text(f"Scheduling meeting {idx + 1}/{len(meeting_emails)}: {email['subject'][:50]}...")
                            
                            date = email.get("date")
                            start_time = email.get("start_time")
                            end_time = email.get("end_time")
                            
                            if date and start_time and end_time:
                                pass
                            elif date and not (start_time or end_time):
                                start_time = f"{date}T10:00:00Z"
                                end_time = f"{date}T10:30:00Z"
                            else:
                                start_time = None
                                end_time = None
                            
                            meet_link = create_meet(
                                subject=email["subject"],
                                description=email["body"],
                                attendee_email=email["from"],
                                start_time=start_time,
                                end_time=end_time
                            )
                            
                            reply_text = f"""Hi,

Thanks for reaching out. I've scheduled a meeting to discuss this further.

Google Meet link: {meet_link}

Looking forward to connecting.
"""
                            send_reply(email.to_dict(), reply_text)
                            success_count += 1
                            
                        except Exception as e:
                            st.error(f"Failed to schedule meeting for: {email['subject'][:50]} - {str(e)}")
                            failed_count += 1
                        
                        progress_bar.progress((idx + 1) / len(meeting_emails))
                    
                    status_text.empty()
                    progress_bar.empty()
                    
                    if success_count > 0:
                        st.success(f"✅ Successfully scheduled {success_count} meeting(s)!")
                    if failed_count > 0:
                        st.warning(f"⚠️ Failed to schedule {failed_count} meeting(s)")
    else:
        st.info("No emails requiring meetings")
    
    st.divider()
    
    # Replied Emails
    st.header("✉️ Needs Reply")
    if len(replied_emails) > 0:
        replied_display = replied_emails[["from", "subject", "priority", "summary", "reply"]].copy()
        replied_display.columns = ["From", "Subject", "Priority", "Summary", "Suggested Reply"]
        
        st.dataframe(
            replied_display,
            use_container_width=True,
            hide_index=True
        )
        
        # Action buttons for replies
        with st.expander("🔧 Actions for Reply Emails"):
            col_reply1, col_reply2 = st.columns(2)
            
            with col_reply1:
                st.subheader("Send Individual Reply")
                selected_reply = st.selectbox(
                    "Select email to reply",
                    range(len(replied_emails)),
                    format_func=lambda i: replied_emails.iloc[i]["subject"],
                    key="individual_reply"
                )
                
                email = replied_emails.iloc[selected_reply]
                edited_reply = st.text_area(
                    "Edit reply before sending",
                    email["reply"],
                    height=150,
                    key="single_reply_text"
                )
                
                if st.button("📤 Send Reply", key="single_reply"):
                    with st.spinner("Sending reply..."):
                        send_reply(email.to_dict(), edited_reply)
                        st.success("✅ Reply sent successfully!")
            
            with col_reply2:
                st.subheader("Send All Replies")
                st.info(f"📊 {len(replied_emails)} reply(ies) to send")
                st.warning("⚠️ All suggested replies will be sent as-is")
                
                if st.button("📤 Send All Replies", type="primary", key="bulk_reply"):
                    success_count = 0
                    failed_count = 0
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for idx, (_, email) in enumerate(replied_emails.iterrows()):
                        try:
                            status_text.text(f"Sending reply {idx + 1}/{len(replied_emails)}: {email['subject'][:50]}...")
                            
                            send_reply(email.to_dict(), email["reply"])
                            success_count += 1
                            
                        except Exception as e:
                            st.error(f"Failed to send reply for: {email['subject'][:50]} - {str(e)}")
                            failed_count += 1
                        
                        progress_bar.progress((idx + 1) / len(replied_emails))
                    
                    status_text.empty()
                    progress_bar.empty()
                    
                    if success_count > 0:
                        st.success(f"✅ Successfully sent {success_count} reply(ies)!")
                    if failed_count > 0:
                        st.warning(f"⚠️ Failed to send {failed_count} reply(ies)")
    else:
        st.info("No emails requiring replies")
    
    st.divider()
    
    # Other/Ignored Emails
    st.header("📋 Other Emails (Ignored)")
    if len(other_emails) > 0:
        other_display = other_emails[["from", "subject", "priority", "summary", "reason"]].copy()
        other_display.columns = ["From", "Subject", "Priority", "Summary", "Reason"]
        
        st.dataframe(
            other_display,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No other emails")
    
    # Footer
    st.divider()
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
