import json
from openai import OpenAI
import therapy
import notepad
import audio
import whatsapp
import brightness
import open_file
import volume
import spotify
import translate
import time
import gemini
import gemini
import reading
# import reading
import my_code
import visualize
import zoom
import google_calendar
import close_active_apps  # Import the close_active_apps module
from exit import is_exit_command  # Import our centralized exit classifier

# Set the API key for OpenAI (this is hard-coded; consider using environment variables for security)
import os
openai.api_key = os.getenv("OPENAI_API_KEY")


def classify_input_to_json(user_input):
    """
    Classify the user input into a JSON structure: 
    {
      "category": <one of 12 categories>,
      "action": <open, close, create, increase, decrease, set, none>
    }
    """

    # Notice the double braces {{ }} in the example JSON line to escape them.
    prompt = f"""
You are a classification system. 
Given the user input, respond with a JSON object that has exactly two keys: "category" and "action".

Allowed categories: [
  "therapy",
  "notepad",
  "whatsapp",
  "meeting",
  "brightness",
  "translate",
  "volume",
  "visualize",
  "spotify",
  "close_active_apps",
  "calendar",
  "web-application",
  "code",
  "web_application",
  "retrive-file"
  "general"
  "gemini",
]

Allowed actions: [
  "open",
  "close",
  "create",
  "increase",
  "decrease",
  "set",
  "none"
]

Instructions:
1. Choose the 'category' based on the user's intent.
2. If the user clearly wants to open/launch something, set "action": "open".
3. If the user clearly wants to close something, set "action": "close".
4. If the user wants to create a meeting, event, file, etc., use "create".
5. If the user wants to increase or decrease something (like brightness or volume), use "increase" or "decrease".
6. If the user wants to set something to a specific value, use "set".
7. If none of the above actions apply, use "none".
8. Make sure the JSON is valid, with double quotes around keys and values, for example:
   {{ "category": "spotify", "action": "open" }}

User input:
{user_input}

Return only valid JSON in your answer. No extra text.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0
        )
        raw_content = response.choices[0].message.content.strip()

        # Attempt to parse the JSON. 
        # If parsing fails, fall back to category = "general", action = "none".
        try:
            parsed_json = json.loads(raw_content)
        except json.JSONDecodeError:
            parsed_json = {"category": "general", "action": "none"}

        # Make sure both keys exist; if missing, default them
        if "category" not in parsed_json:
            parsed_json["category"] = "general"
        if "action" not in parsed_json:
            parsed_json["action"] = "none"

        print(f"DEBUG: classify_input_to_json -> {parsed_json}")
        return parsed_json

    except Exception as e:
        print(f"ERROR in classify_input_to_json: {e}")
        return {"category": "general", "action": "none"}


import re

def parse_brightness_or_volume(user_input):
    """
    Parses user input for numeric values (e.g., "set brightness to 50%") 
    and determines increase or decrease actions.
    Returns (change_value, set_value).
    Example:
      "increase brightness by 10" -> (10, None)
      "decrease volume" -> (-10, None)
      "set brightness to 70" -> (None, 70)
    """
    user_input = user_input.lower()
    change_value = None
    set_value = None

    if "increase" in user_input or "up" in user_input:
        match = re.search(r'\d+', user_input)
        change_value = int(match.group()) if match else 10
    elif "decrease" in user_input or "down" in user_input:
        match = re.search(r'\d+', user_input)
        change_value = -int(match.group()) if match else -10
    elif "set" in user_input:
        match = re.search(r'\d+', user_input)
        set_value = int(match.group()) if match else 50

    print(f"DEBUG: parse_brightness_or_volume returning change={change_value}, set={set_value}")
    return change_value, set_value

def get_general_response(user_input):
    """
    For any input that does not specifically fit into the listed categories,
    we get a normal response from OpenAI.
    """
    prompt = f"Answer the following question:\n{user_input}\n"
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": (
                    "You are AERO, you are almost like a human friend. , "
                    "You speak in a calm and nice and keep your answers short and brief, "
                    "unless the topic really calls for a longer discussion."
                )},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7
        )
        answer = response.choices[0].message.content.strip()
    except Exception as e:
        answer = f"Error generating response: {e}"
    return answer

def main():
    audio.speak("Hey Nafi, how's it going?")
    while True:
        # 1. Capture user input (via microphone or however you are doing it)
        user_input = audio.listen().strip()
        if not user_input:
            continue

        # 2. Check exit condition
        if is_exit_command(user_input):
            audio.speak("Exiting the application. Goodbye!")
            break

        # 3. Classify into JSON (category + action)
        classification = classify_input_to_json(user_input)
        category = classification["category"]
        action = classification["action"]

        print(f"DEBUG: category={category}, action={action}")

        # 4. Route the request based on the category first
        if category == "therapy":
            therapy.activate_therapy_mode()

        elif category == "notepad":
            notepad.open_and_write_notepad()

        elif category == "whatsapp":
            whatsapp.activate_whatsapp_mode()

        elif category == "meeting":
            zoom.zoom_mode()

        elif category == "brightness":
            # If the action is "increase", "decrease", or "set", let's parse the user input
            if action in ["increase", "decrease", "set"]:
                change, set_val = parse_brightness_or_volume(user_input)
                brightness.adjust_brightness(change, set_val)
            else:
                # If there's no numeric action, do something default
                brightness.adjust_brightness(None, None)

        elif category == "volume":
            # Similar logic for volume
            mute_toggle = "mute" in user_input or "silent" in user_input
            if action in ["increase", "decrease", "set"]:
                change, set_val = parse_brightness_or_volume(user_input)
                volume.adjust_volume(change, set_val, mute_toggle)
            else:
                volume.adjust_volume(None, None, mute_toggle)

        elif category == "spotify":
            spotify.spotify_mode()

        elif category == "translate":
            translate.translate_mode()

        # elif category == "web_application":
        #     reading.xyz()

        elif category == "close_active_apps":
            close_active_apps.close_active_apps()

        elif category == "calendar":
            # If user might want to "create" an event
            if action == "create":
                audio.speak("Please provide the details of the event to add to your Google Calendar.")
                event_input = audio.listen().strip()
                google_calendar.create_calendar_event_from_input(event_input)
            else:
                # Some default handling
                audio.speak("Did you want to create or view a calendar event?")

        elif category == "code":
            my_code.code_agent()

        elif category == "web-application":
            reading.web_mode()

        elif category == "visualize":
            visualize.visualize_mod()

        elif category == "retrive-file":
            open_file.retrive_file()
            # time.sleep(150)

        elif category == "gemini":
            audio.speak("Hey! whats up ?")
            gemini.gemini_mode()


        else:
            # category == "general" or unhandled
            response = get_general_response(user_input)
            audio.speak(response)

if __name__ == "__main__":
    main()