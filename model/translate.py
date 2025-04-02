import time
import mss
import cv2
import numpy as np
import google.generativeai as genai
from PIL import Image
import io
import audio
import pygetwindow as gw
import sys

# Configure Gemini API
GENAI_API_KEY = "AIzaSyA9B7lMSkCdMt3Fk78M8DmUtkjFkqaa1-I"  # Replace with your actual API key
genai.configure(api_key=GENAI_API_KEY)

def capture_active_window():
    """Automatically detects and captures the active window."""
    active_window = gw.getActiveWindow()
    
    if not active_window or active_window.isMinimized:
        print("🚪 Active window minimized or closed. Terminating program.")
        sys.exit()
    
    print(f"\n🖥️ Capturing active window: {active_window.title}")
    bbox = (active_window.left, active_window.top, active_window.right, active_window.bottom)
    with mss.mss() as sct:
        screenshot = sct.grab(bbox)  # Capture only the active window

    img = np.array(screenshot)
    img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)  # Convert to RGB format
    pil_image = Image.fromarray(img)

    # Save for verification
    pil_image.save("debug_screenshot.png")
    print("\n📷 Screenshot saved as 'debug_screenshot.png'. Open it to verify the correct screen was captured.")

    return pil_image

def extract_and_translate_text(image_pil):
    """Extracts text from the image and translates it using Gemini AI."""
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    img_io = io.BytesIO()
    image_pil.save(img_io, format="JPEG")
    img_bytes = img_io.getvalue()
    
    response = model.generate_content(
        contents=[
            {"role": "user", "parts": [
                {"text": "Extract the text from this image and translate it into English , do not give the  korean, only give the english translation.."},
                {"mime_type": "image/jpeg", "data": img_bytes}
            ]}
        ]
    )
    
    return response.text if response else "Translation unavailable."

def translate_mode():
    """Automatically capture and translate text every 5 seconds when a new screen is detected."""
    print("⏳ Please pull up the screen you want to capture. Starting in 5 seconds...")
    time.sleep(2)

    last_screen = None
    
    while True:
        print("📸 Automatically detecting and capturing the active window...")
        active_window = gw.getActiveWindow()
        
        if not active_window or active_window.isMinimized:
            print("🚪 Active window minimized or closed. Terminating program.")
            sys.exit()
        
        screen_img = capture_active_window()
        
        if last_screen is None or np.any(np.array(screen_img.resize((800, 600))) != np.array(last_screen.resize((800, 600)))):
            print("🔍 Detecting new screen, extracting text...")
            translated_text = extract_and_translate_text(screen_img)
            print("🔠 **Translated Text (Character-by-Character English Only):**")
            # print(translated_text)
            audio.speak(translated_text)
            last_screen = screen_img
        else:
            print("⏳ No screen change detected, waiting...")
        
        time.sleep(2)  # Wait before taking the next screenshot


