from googleapiclient.discovery import build
from auth import gmail_authenticate
from datetime import datetime, timedelta


def get_calendar_service():
    creds = gmail_authenticate()
    return build("calendar", "v3", credentials=creds)


from typing import Optional
import pytz
import re

def check_time_slot_available(start_time: str, end_time: str) -> bool:
    """
    Check if a time slot is available (no conflicts with existing events)
    """
    try:
        service = get_calendar_service()
        
        print(f"[DEBUG] Checking availability: {start_time} to {end_time}")
        
        events_result = service.events().list(
            calendarId='primary',
            timeMin=start_time,
            timeMax=end_time,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if len(events) > 0:
            print(f"[DEBUG] Slot BUSY - Found {len(events)} conflicting event(s)")
            for event in events:
                print(f"  - {event.get('summary', 'Untitled')}")
        else:
            print(f"[DEBUG] Slot AVAILABLE")
        
        return len(events) == 0  # True if no conflicts
    except Exception as e:
        print(f"[DEBUG] Error checking availability: {e}")
        return True  # If check fails, assume available


def find_next_available_slot(preferred_start: str, duration_minutes: int = 30) -> tuple:
    """
    Find the next available time slot starting from preferred_start
    Returns (start_time, end_time) as ISO strings
    """
    try:
        print(f"[DEBUG] Finding next available slot after: {preferred_start}")
        
        # Parse the preferred start time
        if preferred_start.endswith('Z'):
            preferred_start = preferred_start[:-1]
        
        start_dt = datetime.fromisoformat(preferred_start.replace('Z', ''))
        
        # Try slots in 30-minute increments for up to 24 hours
        # Start from i=1 to skip the conflicting slot itself
        for i in range(1, 49):  # 48 * 30 min = 24 hours, starting from next slot
            test_start = start_dt + timedelta(minutes=i * 30)
            test_end = test_start + timedelta(minutes=duration_minutes)
            
            test_start_str = test_start.strftime("%Y-%m-%dT%H:%M:%S") + "Z"
            test_end_str = test_end.strftime("%Y-%m-%dT%H:%M:%S") + "Z"
            
            print(f"[DEBUG] Checking slot {i}: {test_start_str}")
            
            if check_time_slot_available(test_start_str, test_end_str):
                print(f"[DEBUG] Found available slot: {test_start_str} - {test_end_str}")
                return test_start_str, test_end_str
        
        # If no slot found in 24 hours, return original + 24 hours
        print(f"[DEBUG] No slot found in 24 hours, using fallback")
        fallback_start = start_dt + timedelta(days=1)
        fallback_end = fallback_start + timedelta(minutes=duration_minutes)
        return fallback_start.strftime("%Y-%m-%dT%H:%M:%S") + "Z", fallback_end.strftime("%Y-%m-%dT%H:%M:%S") + "Z"
        
    except Exception as e:
        print(f"[DEBUG] Error in find_next_available_slot: {e}")
        # Fallback to default
        start = datetime.utcnow() + timedelta(days=1)
        end = start + timedelta(minutes=duration_minutes)
        return start.isoformat() + "Z", end.isoformat() + "Z"


def create_meet(subject: str, description: str, attendee_email: str, start_time: Optional[str] = None, end_time: Optional[str] = None, check_conflicts: bool = False, auto_resolve: bool = False) -> dict:
    """
    Creates a Google Calendar event with a Google Meet link.
    
    Returns dict with:
    - meet_link: The Google Meet URL
    - has_conflict: Boolean indicating if there was a time conflict
    - original_time: The originally requested time
    - scheduled_time: The actual scheduled time
    - conflicting_events: List of conflicting event titles (if any)
    - scheduled_time_ist: Formatted time in IST for display
    - date_ist: Date in IST
    - start_time_ist: Start time in IST
    - end_time_ist: End time in IST
    """
    service = get_calendar_service()

    def _default_times():
        start = datetime.utcnow() + timedelta(days=1)
        end = start + timedelta(minutes=30)
        return start.isoformat() + "Z", end.isoformat() + "Z"


    if not start_time or not end_time:
        start_time, end_time = _default_times()

    # Convert local time to UTC
    def local_to_utc(iso_str):
        """Convert IST time to UTC for Google Calendar storage"""
        if not iso_str:
            return iso_str
        
        # If already has Z, it's already UTC - don't convert!
        if iso_str.endswith('Z'):
            print(f"[DEBUG] Time already in UTC (has Z): {iso_str}, skipping conversion")
            return iso_str
            
        iso_str = re.sub(r'Z$', '', iso_str)
        try:
            from datetime import datetime
            import pytz
            
            # Parse the datetime string
            dt = datetime.strptime(iso_str, "%Y-%m-%dT%H:%M:%S")
            
            # Treat as IST (Indian Standard Time)
            ist = pytz.timezone('Asia/Kolkata')
            ist_dt = ist.localize(dt)
            
            # Convert to UTC
            utc_dt = ist_dt.astimezone(pytz.utc)
            result = utc_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            
            print(f"[DEBUG] Converting IST to UTC: {iso_str} (IST) → {result} (UTC)")
            return result
        except Exception as e:
            print(f"[DEBUG] Conversion failed: {e}, returning: {iso_str}Z")
            return iso_str + 'Z'
    
    def utc_to_ist_display(utc_str):
        """Convert UTC time to IST for display"""
        try:
            import pytz
            utc_str = utc_str.replace('Z', '')
            utc_dt = datetime.fromisoformat(utc_str)
            utc_dt = pytz.utc.localize(utc_dt)
            ist = pytz.timezone('Asia/Kolkata')
            ist_dt = utc_dt.astimezone(ist)
            return {
                'date': ist_dt.strftime('%Y-%m-%d'),
                'date_formatted': ist_dt.strftime('%d %B %Y'),  # 25 December 2025
                'time': ist_dt.strftime('%I:%M %p'),  # 04:00 PM
                'datetime_full': ist_dt.strftime('%d %B %Y at %I:%M %p IST')
            }
        except Exception:
            return {
                'date': 'N/A',
                'date_formatted': 'N/A',
                'time': 'N/A',
                'datetime_full': 'N/A'
            }

    original_start = start_time
    original_end = end_time
    
    print(f"[DEBUG] create_meet called with:")
    print(f"  Input start_time: {start_time}")
    print(f"  Input end_time: {end_time}")
    print(f"  check_conflicts: {check_conflicts}")
    print(f"  auto_resolve: {auto_resolve}")
    
    # Convert times (function will skip if already UTC)
    start_time = local_to_utc(start_time)
    end_time = local_to_utc(end_time)
    
    print(f"[DEBUG] After conversion:")
    print(f"  UTC start_time: {start_time}")
    print(f"  UTC end_time: {end_time}")
    
    has_conflict = False
    conflicting_events = []
    
    # Check for conflicts if requested
    if check_conflicts:
        try:
            events_result = service.events().list(
                calendarId='primary',
                timeMin=start_time,
                timeMax=end_time,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            if len(events) > 0:
                has_conflict = True
                conflicting_events = [event.get('summary', 'Untitled Event') for event in events]
                
                print(f"[DEBUG] Conflict detected! Found {len(events)} conflicting events")
                
                # If auto_resolve is True, find next available slot and create meeting
                if auto_resolve:
                    print(f"[DEBUG] Auto-resolving conflict...")
                    start_time, end_time = find_next_available_slot(start_time)
                else:
                    # Don't create meeting, just return conflict info
                    print(f"[DEBUG] Not auto-resolving. Returning conflict info without creating meeting.")
                    start_ist = utc_to_ist_display(start_time)
                    end_ist = utc_to_ist_display(end_time)
                    return {
                        "meet_link": None,
                        "has_conflict": True,
                        "original_time": original_start,
                        "scheduled_time": start_time,
                        "conflicting_events": conflicting_events,
                        "date_ist": start_ist['date'],
                        "date_formatted": start_ist['date_formatted'],
                        "start_time_ist": start_ist['time'],
                        "end_time_ist": end_ist['time'],
                        "datetime_full": start_ist['datetime_full']
                    }
        except Exception as e:
            print(f"[DEBUG] Error checking conflicts: {e}")
            pass

    # Create the meeting (only if no conflict or conflict was resolved)
    print(f"[DEBUG] Creating meeting at: {start_time} to {end_time}")
    
    event = {
        "summary": f"Discussion: {subject}",
        "description": description,
        "start": {
            "dateTime": start_time
        },
        "end": {
            "dateTime": end_time
        },
        "attendees": [
            {"email": attendee_email}
        ],
        "conferenceData": {
            "createRequest": {
                "requestId": f"meet-{start_time}",
                "conferenceSolutionKey": {
                    "type": "hangoutsMeet"
                }
            }
        }
    }

    created_event = service.events().insert(
        calendarId="primary",
        body=event,
        conferenceDataVersion=1
    ).execute()
    
    print(f"[DEBUG] Meeting created successfully!")
    
    # Get IST formatted times for display
    start_ist = utc_to_ist_display(start_time)
    end_ist = utc_to_ist_display(end_time)

    return {
        "meet_link": created_event["hangoutLink"],
        "has_conflict": has_conflict,
        "original_time": original_start,
        "scheduled_time": start_time,
        "conflicting_events": conflicting_events,
        "date_ist": start_ist['date'],
        "date_formatted": start_ist['date_formatted'],
        "start_time_ist": start_ist['time'],
        "end_time_ist": end_ist['time'],
        "datetime_full": start_ist['datetime_full']
    }
