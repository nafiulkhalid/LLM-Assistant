import time
import mss
import cv2
import numpy as np
import google.generativeai as genai
from PIL import Image
import io
import pygetwindow as gw
import pyttsx3
from google.api_core.exceptions import ResourceExhausted

# ---------------- Gemini Setup ----------------
GENAI_API_KEY = "SK0000000000"  # Replace with your actual API key
genai.configure(api_key=GENAI_API_KEY)

# ---------------- Text-to-Speech Setup ----------------
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Adjust speaking rate if desired

def speak_text(text):
    engine.say(text)
    engine.runAndWait()

# ---------------- Capture Function ----------------
def capture_active_window():
    time.sleep(2)  # Brief wait for screen update
    active_window = gw.getActiveWindow()
    with mss.mss() as sct:
        if active_window:
            bbox = {
                "left": active_window.left,
                "top": active_window.top,
                "width": active_window.width,
                "height": active_window.height
            }
            screenshot = sct.grab(bbox)
        else:
            screenshot = sct.grab(sct.monitors[1])
    img = np.array(screenshot)
    img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
    return Image.fromarray(img)

# ---------------- Extraction Function ----------------
def extract_text(image_pil):
    model = genai.GenerativeModel("gemini-1.5-flash")
    img_io = io.BytesIO()
    image_pil.save(img_io, format="JPEG")
    img_bytes = img_io.getvalue()
    
    response = model.generate_content(
        contents=[{
            "role": "user",
            "parts": [
                {"text": "Extract all text from this image exactly as it appears, character by character."},
                {"mime_type": "image/jpeg", "data": img_bytes}
            ]
        }]
    )
    return response.text.strip() if response else ""

# ---------------- Translation Function ----------------
def translate_text(japanese_text):
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = "Translate the following Japanese text into English: " + japanese_text
    try:
        response = model.generate_content(
            contents=[{
                "role": "user",
                "parts": [{"text": prompt}]
            }]
        )
        return response.text.strip() if response else ""
    except ResourceExhausted as e:
        # API quota exceeded; return empty string and skip this cycle.
        return ""
    except Exception as e:
        # Handle any other exceptions gracefully.
        return ""

# ---------------- Main Loop ----------------
def manga_dialogue_translator():
    while True:
        image_pil = capture_active_window()
        japanese_text = extract_text(image_pil)
        if japanese_text:
            english_text = translate_text(japanese_text)
            if english_text:
                speak_text(english_text)
        time.sleep(5)

if __name__ == "__main__":
    try:
        manga_dialogue_translator()
    except KeyboardInterrupt:
        print("\nExiting.")
