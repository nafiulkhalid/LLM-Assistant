import time
import mss
import cv2
import numpy as np
import google.generativeai as genai
import audio
from PIL import Image
import io
import pygetwindow as gw
import pyautogui
import pyperclip

# ===================== Gemini Setup =====================
GENAI_API_KEY = "AIzaSyA9B7lMSkCdMt3Fk78M8DmUtkjFkqaa1-I"  # Replace with your actual API key
genai.configure(api_key=GENAI_API_KEY)

def capture_active_window():
    """
    Captures the currently active window.
    If no active window is found, it captures the full screen.
    """
    time.sleep(2)  # Allow time for the screen to update
    active_window = gw.getActiveWindow()
    
    if not active_window:
        print("\n⚠️ No active window detected! Capturing full screen instead.")
        with mss.mss() as sct:
            monitor = sct.monitors[1]  # Default to full-screen capture
            screenshot = sct.grab(monitor)
    else:
        print(f"\n🖥️ Capturing active window: {active_window.title}")
        bbox = {
            "left": active_window.left,
            "top": active_window.top,
            "width": active_window.width,
            "height": active_window.height
        }
        with mss.mss() as sct:
            screenshot = sct.grab(bbox)

    img = np.array(screenshot)
    img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)  # Convert to RGB
    pil_image = Image.fromarray(img)

    # Save for verification
    pil_image.save("debug_screenshot.png")
    print("\n📷 Screenshot saved as 'debug_screenshot.png'.")
    return pil_image

def extract_text(image_pil):
    """
    Extracts text from the image using Gemini.
    Assumes all text is already in English.
    """
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    # Convert image to bytes
    img_io = io.BytesIO()
    image_pil.save(img_io, format="JPEG")
    img_bytes = img_io.getvalue()

    extraction_response = model.generate_content(
        contents=[{
            "role": "user",
            "parts": [
                {"text": "Extract all text from this image exactly as it appears, character by character."},
                {"mime_type": "image/jpeg", "data": img_bytes}
            ]
        }]
    )
    extracted_text = extraction_response.text if extraction_response else ""
    return extracted_text

def generate_solution_from_text(input_text):
    """
    Uses Gemini to analyze the provided text (from the document)
    and generate a detailed solution or answer.
    The prompt instructs Gemini to provide a solution, not a summary.
    """
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    prompt = (
        "Based on the following document content, provide a detailed solution or answer that directly addresses the problem. "
        "Do not provide a summary or restatement of the content; only give the solution.\n\n"
        f"{input_text}"
    )
    
    response = model.generate_content(
        contents=[{
            "role": "user",
            "parts": [
                {"text": prompt}
            ]
        }]
    )
    solution_text = response.text if response else "No solution generated."
    # Remove any unwanted asterisk characters
    solution_text = solution_text.replace("*", "")
    return solution_text

def write_solution_to_word(solution_text):
    """
    Brings the Word window to the foreground, clicks into the document,
    and then pastes the solution text using clipboard and simulated keystrokes.
    """
    try:
        # Find the Word window by checking for a window title containing "Word"
        word_windows = [w for w in gw.getAllWindows() if "word" in w.title.lower()]
        if not word_windows:
            print("No Word window found. Please open your Word document and try again.")
            return

        # Use the first matching window (adjust if you have multiple Word documents open)
        word_window = word_windows[0]
        print(f"Bringing Word window to front: {word_window.title}")
        word_window.activate()  # Bring the Word window to the front
        time.sleep(0.5)  # Pause briefly to ensure the window is active

        # Calculate a point in the center of the Word window and click it to ensure focus
        center_x = word_window.left + word_window.width // 2
        center_y = word_window.top + word_window.height // 2
        pyautogui.click(center_x, center_y)
        time.sleep(0.5)

        # Copy the solution text to the clipboard
        paste_text = "\n" + solution_text + "\n"
        pyperclip.copy(paste_text)
        time.sleep(0.5)

        # Paste the text using Ctrl+V
        pyautogui.hotkey("ctrl", "v")
        print("Solution successfully written to the Word document via GUI automation.")
    except Exception as e:
        print("Error writing to the Word document:", e)

def process_word_document_with_gemini():
    """
    Checks if the active window is a Word document.
    If so, captures its image, uses Gemini to analyze its content,
    generates a solution, and writes that solution into the document.
    """
    active_window = gw.getActiveWindow()
    if not active_window or "word" not in active_window.title.lower():
        print("The active window is not recognized as a Word document. Please open a Word document and try again.")
        return

    image_pil = capture_active_window()
    extracted_text = extract_text(image_pil)
    if extracted_text:
        print("\n📝 Extracted text from the document:")
        print(extracted_text)
    else:
        extracted_text = "No text extracted from the document."
        print("\n⚠️ No text extracted from the image.")

    print("\n💡 Generating solution from Gemini...")
    solution_text = generate_solution_from_text(extracted_text)
    print("\n🛠️ Generated Solution:")
    # print(solution_text)

    write_solution_to_word(solution_text)

def gemini_mode():
    user_input = audio.listen().strip()
    audio.speak("Sure")
    process_word_document_with_gemini()

