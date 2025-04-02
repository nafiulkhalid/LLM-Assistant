from openai import OpenAI
import speech_recognition as sr
import time
import pyautogui
import undetected_chromedriver as uc
#from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pyttsx3
import requests
import audio
from newspaper import Article
import re
import os
import subprocess
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
import sys

print('started...')


# Initialize speech recognizer
recognizer = sr.Recognizer()

# Initialize global driver variable
driver = None

# OpenAI API Key
import os
openai.api_key = os.getenv("OPENAI_API_KEY")





def open_google():
    """Opens Google in a browser"""
    global driver
    if driver is None:
        driver_path = ChromeDriverManager().install()
        service = Service(driver_path)

        # Launch undetected Chrome
        driver = uc.Chrome(service = service)
        driver.fullscreen_window()
        driver.get("https://www.google.com")
    else:
        print("Google is already open.")


def search_google(query):
    global driver
    if driver is not None:
        open_google()
        time.sleep(3)  # Wait for the browser to open

        
        try:
            search_box = driver.find_element(By.NAME, "q")  # Find search box
            search_box.clear()
            search_box.send_keys(query)
            search_box.send_keys(Keys.RETURN)
            time.sleep(2)  # Wait for results to load
        except NoSuchElementException:
            print("Search box not found! Refreshing the page and retrying...")
            driver.refresh()
            time.sleep(2)
    else:
        print("Google is not open. Opening now...")
        open_google()
        time.sleep(2)
        search_google(query)



def scroll_down():
    """Scrolls down the webpage"""
    global driver
    if driver is not None:
        driver.execute_script("window.scrollBy(0,500)")
    else:
        print("Google is not open.")


def click_link_by_text(link_text):
    """Finds and clicks a link based on spoken words."""
    global driver
    try:
        elements = driver.find_elements(By.TAG_NAME, "a") + driver.find_elements(By.TAG_NAME, "button")
        for element in elements:
            if link_text in element.text.lower():
                element.click()
                print(f"Clicked on: {element.text}")
                return
        print(f"No matching link found for: {link_text}")
    except NoSuchElementException:
        print(f"No element found for {link_text}")
    except ElementClickInterceptedException:
        print(f"Element click intercepted for {link_text}")
    except Exception as e:
        print(f"Error clicking the link: {e}")

# def click(command):
#     link_text = command.split("click", 1)[1].strip()
#     click_link_by_text(link_text)

def click(command):
    lower_command = command.lower()
    if "click" in lower_command:
        parts = lower_command.split("click", 1)
        if len(parts) > 1:
            link_text = parts[1].strip()
            click_link_by_text(link_text)
        else:
            audio.speak("I didn't catch what link to click. Please try again.")
    else:
        audio.speak("The command didn't include 'click'. Please try again.")


def scroll_up():
    """Scrolls up the page by 500 pixels."""
    driver.execute_script("window.scrollBy(0,-500)")


def close_google():
    """Closes the browser"""
    global driver
    if driver is not None:
        driver.quit()
        driver = None
    else:
        print("Google is not open.")


def extract_paragraphs(url):
    article = Article(url)
    article.download()  # Download the article
    article.parse()  # Parse the article
    return article.text.split('\n')  # Split into paragraphs


def save_summary_to_file(summary, url):
    """Saves the summary to a text file with a sanitized filename."""
    # Create a sanitized filename from the URL
    filename = re.sub(r'https?://', '', url)  # Remove 'http://' or 'https://'
    filename = re.sub(r'[\/:*?"<>|]', '_', filename)  # Replace invalid characters with '_'
    filename = filename[:50]  # Limit filename length to avoid OS issues
    # filepath = os.path.join(os.path.expanduser("~"), "Desktop", f"{filename}.txt")
    filepath = os.path.join(os.getcwd(), f"{filename}.txt")  # Save in the current working directory

    time.sleep(1)
    # Save the summary in the text file
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(summary)

    print(f"Summary saved as: {filepath}")
    
def summarize_text(text):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Use GPT-4 or another suitable model
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes text."},
            {"role": "user", "content": f"Summarize the following article in 3 sentences or less:\n\n{text}"}
        ],
        max_tokens=200  # Adjust based on summary length preference
    )
    
    return response.choices[0].message.content



reading_mode = False  # Global flag for reading mode

def process_command(command):
    global reading_mode
    reading_mode = True
    audio.speak("Reading mode activated. You can now use extra features like summarization.")
    

def stop_reading_mode(command):
    global reading_mode
    reading_mode = False
    audio.speak("Reading mode deactivated.")


    
    


def execute_gpt_action(gpt_response):
    """Executes the action suggested by GPT based on user input."""
    
    gpt_response = gpt_response.lower().strip()

    # Define possible actions based on GPT's response
    actions = {
        "scroll down": scroll_down,
        "scroll up": scroll_up,
        "go back": lambda: driver.back(),
        "search": lambda cmd: search_google(cmd),
        "summarize page": summarize_this_page,
        "take screenshot": take_screenshot,
        "enter reading mode": process_command,
        "stop reading mode": stop_reading_mode,
        "summarize table": summarize_table,
        "click": click,
        "open link": click_link_by_text,
        "exit program": exit_program,
    }

    # Check if GPT response matches a known action
    for action_text, function in actions.items():
        if action_text in gpt_response:
            if action_text == "search":
            # If the action is search, we need to extract the search term
                query = gpt_response.replace("search", "").strip()  # Remove 'search' from the command
                function(query)  # Pass the actual query to the function
            elif function.__code__.co_argcount == 0:  # If function takes no arguments
                function()
            else:
                function(action_text)
            return
            

    # If GPT suggests a Google search
    if "search google for" in gpt_response:
        query = gpt_response.replace("search google for", "").strip()
        search_google(query)
        return

    # If GPT suggests opening a website
    if "open" in gpt_response:
        site_name = gpt_response.replace("open", "").strip()
        click_link_by_text(site_name)
        return

    # If GPT response is unclear
    audio.speak("Sorry, I couldn't understand the action. Can you rephrase?")


def handle_command(command):
    """Process the user command, handle known commands, and use GPT for unknown ones."""
    
    # Define direct command mappings
    open_sites = {
        "google": open_google,
    }

    command_variants = {
        ("search", "look up", "find information on", "google this"): lambda cmd: search_google(extract_query(cmd)),
        ("scroll down", "go down", "move down"): scroll_down,
        ("scroll up", "go up", "move up"): scroll_up,
        ("go back", "back page", "previous page", "let's go to back page"): lambda: driver.back(),
        ("take screenshot", "capture screen", "save screenshot"): take_screenshot,
        ("summarize this page", "summarize", "give me summary of this", "explain this page"): summarize_this_page,
        ("enter reading mode", "activate reading mode", "open reading mode", "turn on reading mode"): lambda cmd: process_command(cmd),
        ("summarize this table", "visualize this table", "what is this table", "give information about this table"): summarize_table,
        ("stop reading mode", "deactivate reading mode", "turn off reading mode", "exit reading mode"): lambda cmd: stop_reading_mode(cmd),
        ("exit program", "close google"): close_google,
        ("click", "open this link"): click,
    }

    command_lower = command.lower().strip()

    # Handle "open ..." commands
    if command_lower.startswith("open"):
        site_name = command_lower.replace("open", "").strip()
        if site_name in open_sites:
            open_google()
            return
        else:
            click_link_by_text(site_name)
            return

    # Check for predefined command variations
    for keywords, action in command_variants.items():
        if any(command_lower.startswith(keyword) or command_lower == keyword for keyword in keywords):
            if callable(action):  # Ensures it's a function
                if action.__code__.co_argcount == 0:  # If function takes no arguments
                    action()
                else:
                    action(command)
            return

    # 🔹 Debugging Step: Print when GPT is used
    print(f"Unrecognized command: '{command}'. Sending to GPT...")

    # 🔹 Use GPT for Unrecognized Commands
    #gpt_response = ask_gpt(f"What action should be taken for: '{command}'?")

    gpt_response = ask_gpt(f"Select the best action: search, enter reading mode, stop reading mode, scroll down, scroll up, go back, take screenshot, summarize page, summarize table, exit program, click. User said: '{command}'.")


    print(f"GPT Response: {gpt_response}")  # Debugging line

    

    if gpt_response:
        execute_gpt_action(gpt_response)
    else:
        audio.speak("Sorry, I couldn't determine the action. Can you clarify?")


def extract_query(command):
    """
    Extracts the search query from the voice command.
    Example: "search for cats" -> "cats"
    """
    trigger_phrases = ["search for", "google this", "look up", "search"]
    
    for phrase in trigger_phrases:
        if phrase in command:
            return command.replace(phrase, "").strip()  # Remove the trigger phrase
    
    return command  # Fallback: use the entire command as the query
        

notepad_process = None  # Global variable to track the Notepad process


def summarize_this_page():
    global notepad_process  # To manage the Notepad process

    if reading_mode:
        url = driver.current_url
        article = Article(url)
        article.download()
        article.parse()
        
        summary = summarize_text(article.text)  # Generate summary using OpenAI
        print(f"Summary of this page:\n{summary}")

        # Read summary aloud
        audio.speak(summary)

        # Ask user if they want to save it
        time.sleep(2)
        audio.speak("Do you want to save the summary to Notepad? Say yes or no.")
        # # user_response = listen_command() or ""  # Ensure it's never None
        # user_response = user_response.lower()
        user_response = audio.listen().strip()

        if "yes" in user_response:
            try:
                filename = f"summary_{url.replace('https://', '').replace('/', '_')}.txt"
                with open(filename, "w", encoding="utf-8") as file:
                    file.write(summary)
                
                audio.speak("Summary saved successfully. Opening Notepad now.")
                notepad_process = subprocess.Popen(["notepad.exe", filename])  # Open Notepad
                
                # Wait for a command to close Notepad
                while True:
                    #speak("Say 'close Notepad' to exit Notepad.")
                    # user_response = listen_command() or ""  # Avoid None
                    # user_response = user_response.lower()
                    user_input = audio.listen().strip()

                    if "close notepad" in user_response:
                        notepad_process.terminate()
                        close_notepad()
                        break
            
            except Exception as e:
                audio.speak("An error occurred while saving the summary.")
                print(f"Error: {e}")

        else:
            audio.speak("Okay, not saving the summary.")

    else:
        audio.speak("Please enter into reading mode to get extra features.")

def close_notepad():
    global notepad_process
    if notepad_process:
        #notepad_process.terminate()  # Close Notepad
        audio.speak("Notepad closed.")

def close_notepad():
    global notepad_process
    if notepad_process:
        notepad_process.terminate()  # Close Notepad
        audio.speak("Notepad closed.")
        notepad_process = None
    else:
        audio.speak("Notepad is not open.")




def take_screenshot():
    print("Taking screenshot...")
    # subprocess.run(["python", "llm.py"])  # Runs llm.py when "take screenshot" is detected

    result = subprocess.run(["python", "llm.py"], capture_output=True, text=True)
    screenshot_path = result.stdout.strip()  # Get the printed path from llm.py
    print(f"Screenshot saved at: {screenshot_path}")

    # Run visualize.py with the screenshot path
    # subprocess.run(["python", "visualize.py", screenshot_path])
    time.sleep(5)
            
    vis_result = subprocess.run(["python", "visualize.py", screenshot_path], capture_output=True, text=True)
    output = vis_result.stdout.strip()  # Get printed output from visualize.py
    print("Output from visualize.py:", output)

def summarize_table():
    if reading_mode:
        result = subprocess.run(["python", "llm.py"], capture_output=True, text=True)
        screenshot_path = result.stdout.strip()  # Get the printed path from llm.py
        print(f"Screenshot saved at: {screenshot_path}")

        # Run visualize.py with the screenshot path
        # subprocess.run(["python", "visualize.py", screenshot_path])
        time.sleep(5)
            

        # Start the subprocess with Popen
        with open('visualize.log', 'r') as log_file:
            log_output = log_file.read().strip()
            print("Log output from visualize.py:", log_output)
                
            
    else:
        audio.speak("Please enter into reading mode to get extra features.")

def ask_gpt(prompt):
    response = client.chat.completions.create(
        model="gpt-4",  # Use your desired model
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def exit_program():
    print("Exiting...")
    sys.exit()
    
    


def web_mode():
    # Main loop to listen for commands
    audio.speak('Sure! , what would you like to search ?')

    while True:
        
        # command = listen_command()
        command = audio.listen().strip()
        if command:  # Ensure command is not None
            handle_command(command)
        else:
            print("Could not understand the command.")