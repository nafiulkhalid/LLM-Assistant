# import requests
# import json
# import os
# import subprocess
# import pyautogui
# import time
# from datetime import datetime, timezone, timedelta
# from groq import Groq
# import audio

# # Initialize the Groq client
# client = Groq(api_key="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")


# # 🔹 Zoom OAuth Credentials
# CLIENT_ID = "1OQGfLsRQkCrIV7orHoG6A"
# CLIENT_SECRET = "2pEbo40eSbqimM3BiihOJfmuvAJg9OBm"
# ACCOUNT_ID = "hBx3CgT6TAqmVdc0pNCEvQ"

# # 🔹 Zoom API endpoints
# # TOKEN_URL = f"https://zoom.us/oauth/token?grant_type=account_credentials&account_id={ACCOUNT_ID}"
# ZOOM_MEETING_URL = "https://api.zoom.us/v2/users/me/meetings"

# # 🔹 Token storage file
# # TOKEN_FILE = "zoom_token.json"

# # NOTE:
# # Make sure you have set up your Groq client.
# # For example, if using a hypothetical Groq SDK:
# # from groq_sdk import Client
# # client = Client(api_key="YOUR_GROQ_API_KEY")
# #
# # For this example, we assume that a global `client` object is already available.

# def fetch_new_token():
#     """Fetch a new OAuth token from Zoom and save it to a file."""
#     response = requests.post(TOKEN_URL, auth=(CLIENT_ID, CLIENT_SECRET))
#     if response.status_code == 200:
#         token_data = response.json()
#         expiry_time = datetime.utcnow().replace(tzinfo=timezone.utc) + timedelta(seconds=token_data["expires_in"])
#         token_data["expiry_time"] = expiry_time.isoformat()
#         with open(TOKEN_FILE, "w") as file:
#             json.dump(token_data, file)
#         return token_data
#     else:
#         print("❌ Error fetching new token:", response.text)
#         exit(1)

# def get_access_token():
#     """Retrieve a valid access token, fetching a new one if needed."""
#     if os.path.exists(TOKEN_FILE):
#         try:
#             with open(TOKEN_FILE, "r") as file:
#                 token_data = json.load(file)
#             expiry_time_str = token_data.get("expiry_time", None)
#             if expiry_time_str:
#                 expiry_time = datetime.fromisoformat(expiry_time_str)
#                 if datetime.utcnow().replace(tzinfo=timezone.utc) < expiry_time:
#                     return token_data["access_token"]
#             else:
#                 print("⚠️ Token file exists but expiry_time is missing. Fetching new token.")
#         except (json.JSONDecodeError, KeyError):
#             print("⚠️ Corrupted or invalid token file. Fetching new token.")
#     return fetch_new_token()["access_token"]

# def parse_meeting_command_groq(user_input):
#     """
#     Uses the Groq API to extract meeting details from natural language input.
    
#     Expected JSON output (strictly JSON, no extra text) should have the following keys:
#       - "topic": the meeting title.
#       - "date": the meeting date in YYYY-MM-DD format.
#       - "time": the meeting start time in HH:MM AM/PM format.
#       - "duration": the meeting duration in minutes (an integer).

#     Example:
#       Input: "Schedule a meeting titled 'Team Sync' on 2025-02-10 at 03:00 PM for 30 minutes"
#       Output: {"topic": "Team Sync", "date": "2025-02-10", "time": "03:00 PM", "duration": 30}
#     """
#     prompt = f"""
# You are an AI assistant that only returns structured JSON data.
# Extract the meeting details from the user input. The JSON must have the following keys:
#   - "topic": the meeting title.
#   - "date": the meeting date in YYYY-MM-DD format.
#   - "time": the meeting start time in HH:MM AM/PM format.
#   - "duration": the meeting duration in minutes as an integer.
# Ensure the output is strictly JSON with no additional commentary.

# Example:
# Input: "Schedule a meeting titled 'Team Sync' on 2025-02-10 at 03:00 PM for 30 minutes"
# Output: {{"topic": "Team Sync", "date": "2025-02-10", "time": "03:00 PM", "duration": 30}}

# User Input: {user_input}
# Output:
#     """
#     try:
#         response = client.chat.completions.create(
#             model="llama-3.3-70b-versatile",
#             messages=[{"role": "user", "content": prompt}],
#             temperature=0.0,  # Deterministic output
#             max_tokens=50
#         )

#         if not response or not response.choices:
#             print("❌ ERROR: Empty response from Groq.")
#             return None

#         output = response.choices[0].message.content.strip()
#         print(f"DEBUG: Groq Response: {output}")

#         if not output.startswith("{"):
#             print("❌ ERROR: Groq did not return valid JSON.")
#             return None

#         result = json.loads(output)
#         topic = result.get("topic", "Untitled Meeting")
#         date_str = result.get("date")
#         time_str = result.get("time")
#         duration = result.get("duration")

#         if not date_str or not time_str or duration is None:
#             print("❌ ERROR: Missing meeting details in Groq output.")
#             return None

#         return {
#             "topic": topic,
#             "date": date_str,
#             "time": time_str,
#             "duration": duration
#         }

#     except json.JSONDecodeError as e:
#         print(f"❌ JSON Parsing Error: {e}")
#         return None
#     except Exception as e:
#         print(f"❌ ERROR parsing command with Groq: {e}")
#         return None

# def schedule_zoom_meeting():
#     """Schedule a Zoom meeting using meeting details parsed via Groq."""
#     access_token = get_access_token()  # Ensure a valid token is used
#     headers = {
#         "Authorization": f"Bearer {access_token}",
#         "Content-Type": "application/json"
#     }

#     # ✅ Get natural language input for meeting details
#     audio.speak(
#         "Please describe the meeting  "
#     )
#     time.sleep(1)

#     user_input = audio.listen().strip()

#     meeting_details = parse_meeting_command_groq(user_input)
#     if not meeting_details:
#         print("❌ Failed to parse meeting details. Please try again.")
#         return None

#     topic = meeting_details["topic"]
#     date_str = meeting_details["date"]
#     time_input = meeting_details["time"]
#     duration = meeting_details["duration"]
#     original_time_format = f"{time_input} PST"  # For display purposes

#     # Convert the provided time to 24-hour format for the Zoom API
#     try:
#         formatted_time = datetime.strptime(time_input, "%I:%M %p").strftime("%H:%M")
#     except ValueError:
#         print("❌ Time format error. Please ensure the time is in HH:MM AM/PM format.")
#         return None

#     start_time = f"{date_str}T{formatted_time}:00"

#     meeting_payload = {
#         "topic": topic,
#         "type": 2,  # Scheduled meeting
#         "start_time": start_time,
#         "duration": int(duration),
#         "timezone": "America/Los_Angeles",  # PST
#         "agenda": "User scheduled meeting",
#         "settings": {
#             "host_video": True,
#             "participant_video": True,
#             "join_before_host": False,
#             "mute_upon_entry": True,
#             "waiting_room": True
#         }
#     }

#     response = requests.post(ZOOM_MEETING_URL, headers=headers, data=json.dumps(meeting_payload))
#     if response.status_code == 201:
#         meeting_info = response.json()
#         zoom_details = {
#             "topic": meeting_info['topic'],
#             "start_time": original_time_format,  # Use the original display format
#             "meeting_id": meeting_info['id'],
#             "join_url": meeting_info['join_url']
#         }
#         print("\n✅ Meeting created successfully!")
#         print(f"📌 Meeting Name: {zoom_details['topic']}")
#         print(f"🕒 Start Time: {zoom_details['start_time']}")
#         print(f"🔢 Meeting ID: {zoom_details['meeting_id']}")
#         print(f"🔗 Join URL: {zoom_details['join_url']}")
#         return zoom_details
#     else:
#         print("\n❌ Failed to create meeting:", response.status_code)
#         print(response.json())
#         return None

# def open_whatsapp():
#     """Open WhatsApp Desktop."""
#     try:
#         subprocess.Popen(["cmd", "/c", "start whatsapp:"])
#         time.sleep(5)  # Allow time for WhatsApp to open
#         return True
#     except Exception as e:
#         print(f"❌ Error opening WhatsApp: {e}")
#         return False

# def search_and_open_contact(contact):
#     """Search for a contact and open their chat in WhatsApp Desktop."""
#     print(f"🔍 Searching for contact: {contact}")
#     time.sleep(2)
#     pyautogui.hotkey('ctrl', 'f')
#     time.sleep(1)
#     pyautogui.typewrite(contact)
#     time.sleep(1)
#     pyautogui.press('enter')
#     time.sleep(2)
#     pyautogui.click(200, 200)

# def send_message(message):
#     """Send a message to the selected contact."""
#     print(f"✉️ Sending message:\n{message}")
#     for part in message.split("\n"):
#         pyautogui.typewrite(part)
#         pyautogui.press('enter')
#         time.sleep(1)
#     print("✅ Message sent successfully.")

# def send_whatsapp_message(contact, meeting_details):
#     """Automate sending a WhatsApp message with Zoom meeting details."""
#     if open_whatsapp():
#         search_and_open_contact(contact)
#         message_text = f"""
# 📅 *Meeting Name:* {meeting_details['topic']}
# 🕒 *Start Time:* {meeting_details['start_time']}
# 🔢 *Meeting ID:* {meeting_details['meeting_id']}
# 🔗 *Join URL:* {meeting_details['join_url']}
#         """.strip()
#         send_message(message_text)
#     else:
#         print("❌ Failed to open WhatsApp.")

# def zoom_mode():
#     """Main function to schedule a meeting and optionally send it via WhatsApp."""
#     zoom_meeting_details = schedule_zoom_meeting()
#     if zoom_meeting_details:
#         audio.speak("do you wanna send it to someone ?")
#         send_confirmation = audio.listen().strip().lower()
#         if "yes" in send_confirmation:
#             audio.speak("Provide the  WhatsApp contact name to send the Zoom details: ")
#             contact_name = audio.listen().strip()
#             send_whatsapp_message(contact_name, zoom_meeting_details)
#             time.sleep(10)
#         else:
#             audio.speak("Okay, not sending the meeting details via WhatsApp.")

