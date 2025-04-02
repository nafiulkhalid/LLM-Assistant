import os
import json
import webbrowser
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import re
import audio  # Importing the audio module for speech-to-text and TTS

# Google Calendar API Scope
SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

# Number-to-digit mapping for normalizing spoken numbers
NUMBER_MAPPING = {
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
    "ten": "10",
    "eleven": "11",
    "twelve": "12"
}

def preprocess_text(natural_text):
    """
    Normalize spoken numbers and clean the transcribed text.
    Also normalizes time formats like '8PM' to '8:00 PM'.
    """
    # Replace spoken numbers with digits
    for word, digit in NUMBER_MAPPING.items():
        natural_text = re.sub(rf"\b{word}\b", digit, natural_text, flags=re.IGNORECASE)
    
    # Normalize time formats without a colon (e.g., "8PM" -> "8:00 PM")
    natural_text = re.sub(r"(\d{1,2})(AM|PM|am|pm)", r"\1:00 \2", natural_text)
    
    return natural_text

def authenticate_google_calendar():
    """
    Authenticate with the Google Calendar API and return the service object.
    """
    creds = None
    token_path = "token.json"

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        if not creds or not creds.valid or not creds.refresh_token:
            os.remove(token_path)
            creds = None

    if not creds:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")
        with open(token_path, "w") as token:
            token.write(creds.to_json())

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    return build("calendar", "v3", credentials=creds)

def extract_event_details(natural_text):
    """
    Extracts event details such as title, date, start time, and end time from natural language text.
    """
    try:
        natural_text = preprocess_text(natural_text)  # Normalize the text

        # Extract the event title (Fix: Now correctly extracts the event name)
        title_match = re.search(r"(?:schedule|hold|create|set up)?(?: a)?\s*([\w\s]+?)(?:\s*on|\s*for|\s*at|\s*from|$)", natural_text, re.IGNORECASE)
        title = title_match.group(1).strip().capitalize() if title_match else "Event"

        # Extract the date
        date_match = re.search(r"(?:on|for) (.+?) (from|at)", natural_text, re.IGNORECASE)
        raw_date = date_match.group(1).strip() if date_match else None

        if raw_date:
            # Handle full month names and abbreviated ones
            try:
                date = datetime.strptime(raw_date, "%B %d").replace(year=datetime.now().year).strftime("%Y-%m-%d")
            except ValueError:
                date = datetime.strptime(raw_date, "%b %d").replace(year=datetime.now().year).strftime("%Y-%m-%d")
        else:
            date = None

        # Extract start and end times
        time_match = re.search(r"from (\d{1,2}:\d{2} (AM|PM|am|pm)) to (\d{1,2}:\d{2} (AM|PM|am|pm))", natural_text, re.IGNORECASE)
        if time_match:
            start_time = time_match.group(1).strip()
            end_time = time_match.group(3).strip()
        else:
            start_time, end_time = None, None

        # Convert to 24-hour format
        start_time_24 = datetime.strptime(start_time, "%I:%M %p").strftime("%H:%M") if start_time else None
        end_time_24 = datetime.strptime(end_time, "%I:%M %p").strftime("%H:%M") if end_time else None

        if not title or not date or not start_time_24 or not end_time_24:
            raise ValueError("Incomplete event details extracted.")

        return {
            "title": title,
            "date": date,
            "start_time": start_time_24,
            "end_time": end_time_24,
        }

    except Exception as e:
        print(f"❌ Error extracting event details: {e}")
        return None

def create_calendar_event(event_details):
    """
    Create a new event in Google Calendar using the provided event details.
    """
    try:
        service = authenticate_google_calendar()
        event = {
            "summary": event_details["title"],  # Use the extracted title as the event name
            "description": f"Created via AI Assistant: {event_details['title']}",  # Description includes the title
            "start": {
                "dateTime": f"{event_details['date']}T{event_details['start_time']}:00",
                "timeZone": "America/Los_Angeles",
            },
            "end": {
                "dateTime": f"{event_details['date']}T{event_details['end_time']}:00",
                "timeZone": "America/Los_Angeles",
            },
            "reminders": {
                "useDefault": False,
                "overrides": [{"method": "popup", "minutes": 30}],
            },
        }

        created_event = service.events().insert(calendarId="primary", body=event).execute()
        print(f"✅ Event created successfully: {created_event.get('htmlLink')}")
        audio.speak(f"Your event '{event_details['title']}' has been created successfully.")
        webbrowser.open(created_event.get('htmlLink'))

    except HttpError as error:
        print(f"❌ An error occurred: {error}")
        audio.speak("An error occurred while creating the event. Please try again.")

def create_calendar_event_from_input(event_input):
    """
    Process user input to extract event details and create a Google Calendar event.
    """
    audio.speak("Processing your request.")
    event_details = extract_event_details(event_input)

    if not event_details:
        audio.speak("Failed to extract event details. Please try again.")
    else:
        create_calendar_event(event_details)