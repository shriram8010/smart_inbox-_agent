import streamlit as st
from datetime import timedelta

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
                        result = create_meet(
                            subject=selected["subject"],
                            description=selected["body"],
                            attendee_email=selected["from"],
                            start_time=start_time,
                            end_time=end_time
                        )
                        st.info(f"**Meeting details:**\n- Date: {result.get('date_formatted', date or 'N/A')}\n- Time: {result.get('start_time_ist', 'N/A')} - {result.get('end_time_ist', 'N/A')} IST")
    
                        reply_text = f"""Hi,

Thanks for reaching out. I've scheduled a short meeting so we can discuss this further.

Google Meet link:
{result["meet_link"]}

Looking forward to connecting.
"""
    
                        send_reply(selected, reply_text)
    
                        st.success("✅ Meeting scheduled and invite sent!")
                        st.info(f"📅 **Date:** {result['date_formatted']}")
                        st.info(f"⏰ **Time:** {result['start_time_ist']} - {result['end_time_ist']} IST")
                        st.info(f"🔗 **Meet Link:** {result['meet_link']}")

elif page == "Dashboard":
    # Import and run dashboard
    import pandas as pd
    from gmail_client import fetch_emails, send_reply
    from agent import run_agent
    from calendar_client import create_meet
    from datetime import datetime
    
    # Custom CSS
    st.markdown("""
    <style>
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
                    rate_limit_hit = False
                    
                    for idx, email in enumerate(emails):
                        # Check if email is empty
                        if not email.get("body", "").strip() and not email.get("subject", "").strip():
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
                            result = run_agent(email)
                            
                            # Check if rate limit was hit
                            if "rate_limit" in result.get("reason", "").lower():
                                rate_limit_hit = True
                        
                        processed.append({
                            **email,
                            **result
                        })
                        progress_bar.progress((idx + 1) / len(emails))
                    
                    st.session_state.processed_emails = processed
                    st.session_state.processing_done = True
                    
                    if rate_limit_hit:
                        st.error("⚠️ **Rate Limit Reached!**")
                        st.warning("""
                        Your Groq API has hit the daily token limit (100,000 tokens/day).
                        
                        **Options:**
                        1. Wait ~3 minutes and try again
                        2. Upgrade to Dev Tier at https://console.groq.com/settings/billing
                        3. Use a different API key
                        
                        Emails processed so far are shown below (some may be incomplete).
                        """)
                    else:
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
    
    # Apply filters
    df_filtered = df[df["priority"].isin(priority_filter)]
    
    # Categorize emails
    meeting_emails = df_filtered[df_filtered["action"] == "SCHEDULE_MEET"]
    replied_emails = df_filtered[df_filtered["action"] == "REPLY"]
    other_emails = df_filtered[df_filtered["action"] == "IGNORE"]
    
    # Summary Metrics
    st.header("📈 Summary Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Emails", len(df_filtered))
    with col2:
        st.metric("Meeting Scheduled", len(meeting_emails))
    with col3:
        st.metric("Needs Reply", len(replied_emails))
    with col4:
        st.metric("Other/Ignored", len(other_emails))
    
    st.divider()
    
    # ==================== MEETINGS SECTION ====================
    st.header("📅 Meeting Scheduled")
    if len(meeting_emails) > 0:
        # Show summary table
        meeting_summary = meeting_emails[["from", "subject", "priority"]].copy()
        meeting_summary.columns = ["From", "Subject", "Priority"]
        meeting_summary.insert(0, "#", range(1, len(meeting_summary) + 1))
        
        st.dataframe(meeting_summary, use_container_width=True, hide_index=True)
        
        # Bulk action button
        col_bulk1, col_bulk2 = st.columns([3, 1])
        with col_bulk2:
            if st.button("📆 Schedule All Meetings", type="primary", use_container_width=True):
                success_count = 0
                conflict_count = 0
                progress_bar = st.progress(0)
                status_text = st.empty()
                conflict_details = []
                
                for idx, (_, email) in enumerate(meeting_emails.iterrows()):
                    try:
                        status_text.text(f"Scheduling {idx + 1}/{len(meeting_emails)}...")
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
                        
                        result = create_meet(
                            subject=email["subject"],
                            description=email["body"],
                            attendee_email=email["from"],
                            start_time=start_time,
                            end_time=end_time,
                            check_conflicts=True,
                            auto_resolve=True  # Auto-find next slot for bulk
                        )
                        
                        if result["has_conflict"]:
                            conflict_count += 1
                            conflict_details.append(f"• {email['subject'][:40]} - Rescheduled due to conflict")
                        
                        reply_text = f"""Hi,

Thanks for reaching out. I've scheduled a meeting to discuss this further.

Google Meet link: {result["meet_link"]}

Looking forward to connecting.
"""
                        send_reply(email.to_dict(), reply_text)
                        success_count += 1
                    except Exception as e:
                        st.error(f"Failed: {email['subject'][:40]}")
                    
                    progress_bar.progress((idx + 1) / len(meeting_emails))
                
                status_text.empty()
                progress_bar.empty()
                st.success(f"✅ Scheduled {success_count}/{len(meeting_emails)} meetings!")
                
                if conflict_count > 0:
                    st.warning(f"⚠️ {conflict_count} meeting(s) had time conflicts and were rescheduled:")
                    for detail in conflict_details:
                        st.caption(detail)
        
        # Individual email details - clickable
        st.subheader("📋 Click to View Details & Take Action")
        for idx, (_, email) in enumerate(meeting_emails.iterrows()):
            with st.expander(f"#{idx+1}: {email['subject'][:70]}"):
                col_info, col_action = st.columns([2, 1])
                
                with col_info:
                    st.markdown(f"**From:** {email['from']}")
                    st.markdown(f"**Priority:** {email['priority']}")
                    st.markdown(f"**Summary:** {email['summary']}")
                    
                    # Show extracted date/time for debugging
                    with st.expander("🔍 AI Extracted Time Info (Debug)"):
                        st.json({
                            "date": email.get('date', 'Not extracted'),
                            "start_time": email.get('start_time', 'Not extracted'),
                            "end_time": email.get('end_time', 'Not extracted')
                        })
                    
                    with st.expander("📧 Full Email"):
                        st.text(email['body'][:500])
                
                with col_action:
                    # Manual time override option
                    with st.expander("⏰ Edit Meeting Time"):
                        st.caption("Override AI-extracted time or set custom time")
                        
                        col_date, col_time = st.columns(2)
                        with col_date:
                            custom_date = st.date_input(
                                "Date",
                                value=datetime.now().date() + timedelta(days=1),
                                key=f"custom_date_{idx}"
                            )
                        with col_time:
                            custom_time = st.time_input(
                                "Start Time",
                                value=datetime.strptime("14:00", "%H:%M").time(),
                                key=f"custom_time_{idx}"
                            )
                        
                        custom_duration = st.selectbox(
                            "Duration",
                            [15, 30, 45, 60, 90, 120],
                            index=1,
                            key=f"duration_{idx}"
                        )
                        
                        use_custom_time = st.checkbox("Use custom time", key=f"use_custom_{idx}")
                    
                    # Check if there's a pending conflict for this email
                    conflict_key = f"conflict_{idx}"
                    has_pending_conflict = conflict_key in st.session_state
                    
                    if has_pending_conflict:
                        # Show conflict resolution options
                        conflict_data = st.session_state[conflict_key]
                        
                        st.warning(f"⚠️ **Time Conflict Detected!**")
                        st.error(f"**Requested:** {conflict_data['requested_time']}")
                        st.error(f"**Conflicting meeting(s):** {', '.join(conflict_data['conflicting_events'])}")
                        
                        st.success(f"✅ **Next Available Slot Found:**")
                        st.info(f"📅 {conflict_data['next_date']}\n\n⏰ {conflict_data['next_time']}")
                        
                        col_opt1, col_opt2, col_opt3 = st.columns(3)
                        
                        with col_opt1:
                            if st.button("✅ Use This Slot", key=f"use_next_{idx}", type="primary"):
                                use_start = conflict_data['next_start']
                                use_end = conflict_data['next_end']
                                
                                with st.spinner("Creating meeting..."):
                                    result_new = create_meet(
                                        subject=email["subject"],
                                        description=email["body"],
                                        attendee_email=email["from"],
                                        start_time=use_start,
                                        end_time=use_end,
                                        check_conflicts=False,
                                        auto_resolve=False
                                    )
                                
                                if result_new.get("meet_link"):
                                    reply_text = f"""Hi,

Thanks for reaching out. I've scheduled a meeting to discuss this further.

Note: Your requested time had a conflict, so I scheduled it at the next available slot.

Google Meet link: {result_new["meet_link"]}

Looking forward to connecting.
"""
                                    send_reply(email.to_dict(), reply_text)
                                    st.success("✅ Scheduled at next available time!")
                                    st.info(f"📅 **Date:** {result_new['date_formatted']}\n\n⏰ **Time:** {result_new['start_time_ist']} - {result_new['end_time_ist']} IST")
                                    st.info(f"🔗 **Meet Link:** {result_new['meet_link']}")
                                    
                                    # Clear conflict state
                                    del st.session_state[conflict_key]
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to create meeting")
                        
                        with col_opt2:
                            if st.button("🔄 Find Another", key=f"find_another_{idx}"):
                                # Find next slot after current suggestion
                                from calendar_client import find_next_available_slot
                                another_start, another_end = find_next_available_slot(conflict_data['next_start'])
                                
                                # Update conflict data with new slot
                                import pytz
                                utc = pytz.utc
                                ist = pytz.timezone('Asia/Kolkata')
                                
                                another_start_dt = datetime.fromisoformat(another_start.replace('Z', ''))
                                another_start_dt = utc.localize(another_start_dt).astimezone(ist)
                                
                                another_end_dt = datetime.fromisoformat(another_end.replace('Z', ''))
                                another_end_dt = utc.localize(another_end_dt).astimezone(ist)
                                
                                st.session_state[conflict_key]['next_start'] = another_start
                                st.session_state[conflict_key]['next_end'] = another_end
                                st.session_state[conflict_key]['next_date'] = another_start_dt.strftime('%d %B %Y')
                                st.session_state[conflict_key]['next_time'] = f"{another_start_dt.strftime('%I:%M %p')} - {another_end_dt.strftime('%I:%M %p')} IST"
                                
                                st.rerun()
                        
                        with col_opt3:
                            if st.button("❌ Cancel", key=f"cancel_{idx}"):
                                del st.session_state[conflict_key]
                                st.rerun()
                    
                    else:
                        # Show normal schedule button
                        if st.button("📆 Schedule Meeting", key=f"meet_{idx}", use_container_width=True):
                            # Determine which time to use
                            if use_custom_time:
                                # Use custom time from UI
                                start_time = f"{custom_date}T{custom_time.strftime('%H:%M:%S')}"
                                end_dt = datetime.combine(custom_date, custom_time) + timedelta(minutes=custom_duration)
                                end_time = end_dt.strftime("%Y-%m-%dT%H:%M:%S")
                                st.info(f"📅 Using custom time: {custom_date.strftime('%d %B %Y')}")
                                st.info(f"⏰ {custom_time.strftime('%I:%M %p')} - {end_dt.strftime('%I:%M %p')} ({custom_duration} minutes)")
                            else:
                                # Use AI-extracted time
                                date = email.get("date")
                                start_time = email.get("start_time")
                                end_time = email.get("end_time")
                                
                                if date and start_time and end_time:
                                    pass
                                elif date and not (start_time or end_time):
                                    start_time = f"{date}T10:00:00"
                                    end_time = f"{date}T10:30:00"
                                else:
                                    start_time = None
                                    end_time = None
                            
                            with st.spinner("Checking calendar..."):
                                result = create_meet(
                                    subject=email["subject"],
                                    description=email["body"],
                                    attendee_email=email["from"],
                                    start_time=start_time,
                                    end_time=end_time,
                                    check_conflicts=True,
                                    auto_resolve=False
                                )
                            
                            if result["has_conflict"]:
                                # Store conflict info in session state
                                from calendar_client import find_next_available_slot
                                next_start, next_end = find_next_available_slot(result['scheduled_time'])
                                
                                import pytz
                                utc = pytz.utc
                                ist = pytz.timezone('Asia/Kolkata')
                                
                                next_start_dt = datetime.fromisoformat(next_start.replace('Z', ''))
                                next_start_dt = utc.localize(next_start_dt).astimezone(ist)
                                
                                next_end_dt = datetime.fromisoformat(next_end.replace('Z', ''))
                                next_end_dt = utc.localize(next_end_dt).astimezone(ist)
                                
                                st.session_state[conflict_key] = {
                                    'requested_time': f"{result['date_formatted']} at {result['start_time_ist']}",
                                    'conflicting_events': result['conflicting_events'],
                                    'next_start': next_start,
                                    'next_end': next_end,
                                    'next_date': next_start_dt.strftime('%d %B %Y'),
                                    'next_time': f"{next_start_dt.strftime('%I:%M %p')} - {next_end_dt.strftime('%I:%M %p')} IST"
                                }
                                
                                st.rerun()
                            else:
                                # No conflict, meeting created successfully
                                reply_text = f"""Hi,

Thanks for reaching out. I've scheduled a meeting to discuss this further.

Google Meet link: {result["meet_link"]}

Looking forward to connecting.
"""
                                send_reply(email.to_dict(), reply_text)
                                st.success("✅ Meeting scheduled!")
                                st.info(f"📅 **Date:** {result['date_formatted']}\n\n⏰ **Time:** {result['start_time_ist']} - {result['end_time_ist']} IST")
                                st.info(f"🔗 **Meet Link:** {result['meet_link']}")
                        # Determine which time to use
                        if use_custom_time:
                            # Use custom time from UI
                            start_time = f"{custom_date}T{custom_time.strftime('%H:%M:%S')}"
                            end_dt = datetime.combine(custom_date, custom_time) + timedelta(minutes=custom_duration)
                            end_time = end_dt.strftime("%Y-%m-%dT%H:%M:%S")
                            st.info(f"📅 Using custom time: {custom_date.strftime('%d %B %Y')}")
                            st.info(f"⏰ {custom_time.strftime('%I:%M %p')} - {end_dt.strftime('%I:%M %p')} ({custom_duration} minutes)")
                        else:
                            # Use AI-extracted time
                            date = email.get("date")
                            start_time = email.get("start_time")
                            end_time = email.get("end_time")
                            
                            if date and start_time and end_time:
                                pass
                            elif date and not (start_time or end_time):
                                start_time = f"{date}T10:00:00"
                                end_time = f"{date}T10:30:00"
                            else:
                                start_time = None
                                end_time = None
                        
                        with st.spinner("Checking calendar..."):
                            result = create_meet(
                                subject=email["subject"],
                                description=email["body"],
                                attendee_email=email["from"],
                                start_time=start_time,
                                end_time=end_time,
                                check_conflicts=True,
                                auto_resolve=False
                            )
                        
                        if result["has_conflict"]:
                            # Store conflict info in session state
                            from calendar_client import find_next_available_slot
                            next_start, next_end = find_next_available_slot(result['scheduled_time'])
                            
                            import pytz
                            utc = pytz.utc
                            ist = pytz.timezone('Asia/Kolkata')
                            
                            next_start_dt = datetime.fromisoformat(next_start.replace('Z', ''))
                            next_start_dt = utc.localize(next_start_dt).astimezone(ist)
                            
                            next_end_dt = datetime.fromisoformat(next_end.replace('Z', ''))
                            next_end_dt = utc.localize(next_end_dt).astimezone(ist)
                            
                            st.session_state[conflict_key] = {
                                'requested_time': f"{result['date_formatted']} at {result['start_time_ist']}",
                                'conflicting_events': result['conflicting_events'],
                                'next_start': next_start,
                                'next_end': next_end,
                                'next_date': next_start_dt.strftime('%d %B %Y'),
                                'next_time': f"{next_start_dt.strftime('%I:%M %p')} - {next_end_dt.strftime('%I:%M %p')} IST"
                            }
                            
                            st.rerun()
                        else:
                            # No conflict, meeting created successfully
                            reply_text = f"""Hi,

Thanks for reaching out. I've scheduled a meeting to discuss this further.

Google Meet link: {result["meet_link"]}

Looking forward to connecting.
"""
                            send_reply(email.to_dict(), reply_text)
                            st.success("✅ Meeting scheduled!")
                            st.info(f"📅 **Date:** {result['date_formatted']}\n\n⏰ **Time:** {result['start_time_ist']} - {result['end_time_ist']} IST")
                            st.info(f"🔗 **Meet Link:** {result['meet_link']}")
    else:
        st.info("No emails requiring meetings")
    
    st.divider()
    
    # ==================== REPLIES SECTION ====================
    st.header("✉️ Needs Reply")
    if len(replied_emails) > 0:
        # Show summary table
        reply_summary = replied_emails[["from", "subject", "priority"]].copy()
        reply_summary.columns = ["From", "Subject", "Priority"]
        reply_summary.insert(0, "#", range(1, len(reply_summary) + 1))
        
        st.dataframe(reply_summary, use_container_width=True, hide_index=True)
        
        # Bulk action button
        col_bulk1, col_bulk2 = st.columns([3, 1])
        with col_bulk2:
            if st.button("📤 Send All Replies", type="primary", use_container_width=True):
                success_count = 0
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for idx, (_, email) in enumerate(replied_emails.iterrows()):
                    try:
                        status_text.text(f"Sending {idx + 1}/{len(replied_emails)}...")
                        send_reply(email.to_dict(), email["reply"])
                        success_count += 1
                    except Exception as e:
                        st.error(f"Failed: {email['subject'][:40]}")
                    
                    progress_bar.progress((idx + 1) / len(replied_emails))
                
                status_text.empty()
                progress_bar.empty()
                st.success(f"✅ Sent {success_count}/{len(replied_emails)} replies!")
        
        # Individual email details - clickable
        st.subheader("📋 Click to View Details & Take Action")
        for idx, (_, email) in enumerate(replied_emails.iterrows()):
            with st.expander(f"#{idx+1}: {email['subject'][:70]}"):
                col_info, col_action = st.columns([2, 1])
                
                with col_info:
                    st.markdown(f"**From:** {email['from']}")
                    st.markdown(f"**Priority:** {email['priority']}")
                    st.markdown(f"**Summary:** {email['summary']}")
                    st.markdown("**Suggested Reply:**")
                    edited_reply = st.text_area(
                        "Edit before sending",
                        email["reply"],
                        height=150,
                        key=f"reply_text_{idx}"
                    )
                    with st.expander("📧 Full Email"):
                        st.text(email['body'][:500])
                
                with col_action:
                    if st.button("📤 Send Reply", key=f"reply_{idx}", use_container_width=True):
                        with st.spinner("Sending..."):
                            send_reply(email.to_dict(), edited_reply)
                            st.success("✅ Sent!")
    else:
        st.info("No emails requiring replies")
    
    st.divider()
    
    # ==================== OTHER EMAILS ====================
    st.header("📋 Other Emails (Ignored)")
    if len(other_emails) > 0:
        other_display = other_emails[["from", "subject", "priority", "reason"]].copy()
        other_display.columns = ["From", "Subject", "Priority", "Reason"]
        other_display.insert(0, "#", range(1, len(other_display) + 1))
        
        st.dataframe(other_display, use_container_width=True, hide_index=True)
    else:
        st.info("No other emails")
    
    # Footer
    st.divider()
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
