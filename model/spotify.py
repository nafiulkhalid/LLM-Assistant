import subprocess
import time
import re
import pyautogui
import pygetwindow as gw
import pyttsx3
import speech_recognition as sr
from pywinauto import Application
import os

# Initialize text-to-speech engine
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# Listen for voice commands using the microphone
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for Spotify command...")
        speak("Please say your Spotify command.")
        audio_data = recognizer.listen(source)
    try:
        command = recognizer.recognize_google(audio_data)
        print(f"You said: {command}")
        return command.lower()
    except sr.UnknownValueError:
        speak("Sorry, I did not understand that.")
        return None
    except sr.RequestError:
        speak("Network error. Please check your connection.")
        return None

# Helper: Get the Spotify window if open
def get_spotify_window():
    windows = [w for w in gw.getAllWindows() if "spotify" in w.title.lower()]
    return windows[0] if windows else None

# Spotify control functions

def open_spotify():
    """Launch Spotify on Windows."""
    speak("Opening Spotify, please wait.")
    subprocess.Popen("start spotify", shell=True)
    time.sleep(5)  # Wait for Spotify to open

def close_spotify():
    """Close Spotify using taskkill."""
    try:
        subprocess.run(["taskkill", "/IM", "spotify.exe", "/F"], shell=True)
        speak("Spotify has been closed.")
    except Exception as e:
        speak(f"Unable to close Spotify. {e}")

def search_and_play(song):
    """Search for a song in Spotify and play it."""
    speak(f"Searching for {song} in Spotify.")
    time.sleep(3)
    window = get_spotify_window()
    if not window:
        speak("Spotify window not found. Please open Spotify first.")
        return

    window.activate()
    try:
        # Connect to the Spotify window
        app = Application().connect(handle=window._hWnd)
        sp_window = app.window()
        # Open the search bar using Ctrl+K
        sp_window.type_keys("^k")
        time.sleep(1)
        # Clear any existing text (select all and backspace)
        sp_window.type_keys("^a{BACKSPACE}")
        # Type the song name
        sp_window.type_keys(song, with_spaces=True)
        sp_window.type_keys("{ENTER}")
        time.sleep(2)
        # Press enter to play the first result
        pyautogui.press("enter")
        speak("Playing the selected track.")
    except Exception as e:
        speak("Error interacting with Spotify.")
        print(f"Error: {e}")

def play_if_already_open():
    """Resume playback if Spotify is already open."""
    window = get_spotify_window()
    if window:
        window.activate()
        pyautogui.press("enter")
        speak("Resuming playback.")
    else:
        speak("Spotify is not open.")

def skip_next():
    """Skip to the next track."""
    pyautogui.hotkey("ctrl", "right")
    speak("Skipping to the next track.")

def go_previous():
    """Go back to the previous track."""
    pyautogui.hotkey("ctrl", "left")
    speak("Going back to the previous track.")

def pause_media():
    """Pause or resume the current track."""
    pyautogui.press("space")
    speak("Toggling pause.")

# Interpret the user's Spotify command using simple pattern matching
def interpret_spotify_command(command):
    if command is None:
        return None

    # If the user wants to open Spotify (optionally with a song)
    if "open" in command:
        if "spotify" in command:
            # Check if they also want to play a song
            if "play" in command:
                match = re.search(r"play\s+(.*)", command)
                if match:
                    song = match.group(1).strip()
                    return {"action": "open_play", "song": song}
            return {"action": "open"}
    # If the user wants to close Spotify
    if "close" in command and "spotify" in command:
        return {"action": "close"}
    # If the user issues a play command
    if "play" in command:
        match = re.search(r"play\s+(.*)", command)
        if match:
            song = match.group(1).strip()
            return {"action": "play", "song": song}
        else:
            return {"action": "play_resume"}
    # If the user wants to skip to the next track
    if "skip" in command or "next" in command:
        return {"action": "skip"}
    # If the user wants to go to the previous track
    if "previous" in command or "back" in command:
        return {"action": "previous"}
    # If the user wants to pause playback
    if "pause" in command:
        return {"action": "pause"}

    # Default: Unrecognized command
    return {"action": "unknown"}

# Execute the Spotify action based on the parsed command
def execute_spotify_action(command_dict):
    if command_dict is None:
        speak("I didn't catch a valid command.")
        return

    action = command_dict.get("action")
    if action == "open":
        open_spotify()
    elif action == "open_play":
        open_spotify()
        time.sleep(5)
        song = command_dict.get("song")
        if song:
            search_and_play(song)
    elif action == "close":
        close_spotify()
    elif action == "play":
        song = command_dict.get("song")
        if song:
            search_and_play(song)
        else:
            play_if_already_open()
    elif action == "play_resume":
        play_if_already_open()
    elif action == "skip":
        skip_next()
    elif action == "previous":
        go_previous()
    elif action == "pause":
        pause_media()
    else:
        speak("Spotify command not recognized. Please try again.")

# Main loop: Listen for Spotify commands and execute them
def spotify_mode():
    speak("Spotify assistant activated.")
    try:
        while True:
            command = listen()
            if command is None:
                continue
            if "exit" in command:
                speak("Exiting Spotify assistant.")
                break
            command_dict = interpret_spotify_command(command)
            execute_spotify_action(command_dict)
            speak("Do you need anything else with Spotify?")
    except KeyboardInterrupt:
        speak("Exiting Spotify assistant.")


