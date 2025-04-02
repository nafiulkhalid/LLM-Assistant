# code function working. 

import os
import sys
import time
import subprocess
import psutil
import pyautogui
import pygetwindow as gw
import re
import json
import audio
import pyperclip
from openai import OpenAI

##############################################################################
# SETUP
##############################################################################

import os
openai.api_key = os.getenv("OPENAI_API_KEY")


# Initialize OpenAI API
if not OpenAI.api_key:
    raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")

client = OpenAI()

# Path to your VS Code executable (change accordingly)
VSCODE_PATH_WINDOWS = r"C:\Users\ezaza\AppData\Local\Programs\Microsoft VS Code\Code.exe"
# VSCODE_PATH_MAC = "/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code"  # Update if different
# VSCODE_PATH_LINUX = "/usr/bin/code"  # Update if different

# Determine OS and set VSCode path accordingly
if os.name == 'nt':
    VSCODE_PATH = VSCODE_PATH_WINDOWS
elif sys.platform == "darwin":
    VSCODE_PATH = VSCODE_PATH_MAC
elif sys.platform.startswith("linux"):
    VSCODE_PATH = VSCODE_PATH_LINUX
else:
    raise OSError("Unsupported operating system for VS Code path configuration.")

# Global conversation memory for context retention
conversation_history = [
    {
        "role": "system",
        "content": (
            "You are an AI assistant that helps generate and debug Python code. "
            "You remember the conversation context."
        )
    }
]

##############################################################################
# MEMORY-BASED FUNCTIONS
##############################################################################

def add_message(role: str, content: str):
    """
    Appends a message to the conversation history.
    """
    conversation_history.append({"role": role, "content": content})

def chat_with_gpt(prompt: str) -> str:
    """
    Sends the latest user prompt plus full conversation history to GPT,
    and returns GPT's answer.
    """
    add_message("user", prompt)
    try:
        response = client.chat.completions.create(
            model="gpt-4",  # Updated to use GPT-4 for better performance
            messages=conversation_history,
            temperature=0.7,
            max_tokens=1500
        )
        assistant_message = response.choices[0].message.content.strip()
        add_message("assistant", assistant_message)

        return assistant_message
    except Exception as e:
        print(f"[ERROR] OpenAI API request failed: {e}")
        return ""

##############################################################################
# FILE & FOLDER HELPERS
##############################################################################
def create_folder_on_desktop(folder_name: str) -> str:
    """
    Creates a folder on the user's Desktop (if it doesn't exist) and returns its path.
    """
    try:
        if os.name == 'nt':
            desktop_path = os.path.join(os.environ['USERPROFILE'], 'Desktop')
        else:
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    except KeyError:
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")

    target_folder = os.path.join(desktop_path, folder_name)

    if not os.path.exists(target_folder):
        try:
            os.mkdir(target_folder)
            print(f"[INFO] Created folder: {target_folder}")
        except Exception as e:
            print(f"[ERROR] Could not create folder '{folder_name}': {e}")
            return ""
    else:
        print(f"[INFO] Folder '{folder_name}' already exists at: {target_folder}")

    return target_folder

def write_code_to_file(folder_path: str, file_name: str, code: str) -> str:
    """
    Writes the given code to a file in the specified folder.
    Extracts only the Python code from code blocks if present.
    """
    if not folder_path:
        print("[ERROR] Invalid folder path. Cannot write file.")
        return ""

    # Extract code between ```python and ```
    code_blocks = re.findall(r'```python\s*(.*?)\s*```', code, re.DOTALL | re.IGNORECASE)
    if code_blocks:
        final_code = code_blocks[0].strip()
    else:
        # If no code blocks found, assume entire response is code
        final_code = code.strip()

    # Optionally, remove any leading non-code lines (e.g., comments)
    lines = final_code.splitlines()
    cleaned_lines = []
    for line in lines:
        if line.strip().startswith("#") or line.strip() == "":
            cleaned_lines.append(line)
        else:
            cleaned_lines.append(line)
    final_code = "\n".join(cleaned_lines).strip()

    file_path = os.path.join(folder_path, file_name)
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(final_code)
        print(f"[INFO] Created/updated file: {file_path}")
    except Exception as e:
        print(f"[ERROR] Could not write to file '{file_name}': {e}")

    return file_path

##############################################################################
# APPLICATION HELPERS (VS CODE, Notepad, etc.)
##############################################################################

def check_application_running(app_name: str) -> bool:
    """
    Checks if an application with a given name is running.
    """
    try:
        for process in psutil.process_iter(['name']):
            if process.info['name'] and app_name.lower() in process.info['name'].lower():
                return True
    except Exception as e:
        print(f"[WARN] Failed to check if '{app_name}' is running: {e}")
    return False

def bring_window_to_front(app_name: str) -> bool:
    """
    Attempts to bring an application window to the forefront.
    """
    try:
        all_windows = gw.getAllTitles()
        matched_window = next(
            (title for title in all_windows if app_name.lower() in title.lower()),
            None
        )
        if matched_window:
            window = gw.getWindowsWithTitle(matched_window)[0]
            window.minimize()
            window.restore()
            window.activate()
            print(f"[INFO] Brought '{app_name}' to the front.")
            return True
        else:
            print(f"[INFO] No window found for '{app_name}'.")
    except Exception as e:
        print(f"[WARN] Could not bring '{app_name}' to front: {e}")
    return False

def open_application(app_name: str):
    """
    Opens an application dynamically based on the system OS.
    """
    print(f"[INFO] Opening {app_name}, please wait.")
    if os.name == "nt":  # Windows
        try:
            subprocess.Popen(f"start {app_name}", shell=True)
        except Exception as e:
            print(f"[ERROR] Failed to open {app_name}: {e}")
    elif sys.platform == "darwin":  # macOS
        try:
            subprocess.Popen(["open", "-a", app_name])
        except Exception as e:
            print(f"[ERROR] Failed to open {app_name}: {e}")
    elif sys.platform.startswith("linux"):  # Linux
        try:
            subprocess.Popen([app_name])
        except Exception as e:
            print(f"[ERROR] Failed to open {app_name}: {e}")
    else:
        print("Unsupported operating system.")
        return False
    time.sleep(3)  # Wait for the application to open
    return True

def open_in_vscode(file_path: str):
    """
    Opens the specified file in VS Code (non-blocking).
    """
    try:
        subprocess.Popen([VSCODE_PATH, file_path])
        print(f"[INFO] Opening '{file_path}' in VS Code.")
    except Exception as e:
        print(f"[ERROR] Could not open '{file_path}' in VS Code: {e}")

def open_or_focus_vscode(file_path: str):
    """
    If VS Code is running, bring it to front. Otherwise, open the file in VS Code.
    """
    if check_application_running("Code"):
        if not bring_window_to_front("Visual Studio Code"):
            print("[INFO] Attempting to bring VS Code to front failed. Opening new instance.")
            open_in_vscode(file_path)
    else:
        open_in_vscode(file_path)

##############################################################################
# NOTEPAD HELPERS
##############################################################################

def bring_to_forefront(app_name):
    """Bring an already running application to the forefront."""
    if os.name == 'nt':  # Windows
        try:
            all_windows = gw.getAllTitles()
            matched_window = next((title for title in all_windows if app_name.lower() in title.lower()), None)

            if matched_window:
                window = gw.getWindowsWithTitle(matched_window)[0]
                window.minimize()
                window.restore()
                window.activate()
                print(f"[INFO] {app_name} is already running. Bringing it to the front.")
                return True
            else:
                print(f"[INFO] Couldn't find {app_name}. Make sure it's running.")
                return False
        except Exception as e:
            print(f"[ERROR] Unable to bring {app_name} to the front. Error: {e}")
            return False
    else:
        print("This functionality is supported only on Windows.")
        return False

def click_notepad():
    """Click inside Notepad to ensure it's ready for input."""
    try:
        bring_to_forefront("Notepad")
        time.sleep(1)
        # Perform a click at the center of the Notepad window
        window = gw.getWindowsWithTitle("Notepad")[0]
        if window:
            x, y, w, h = window.left, window.top, window.width, window.height
            pyautogui.click(x + w // 2, y + h // 2)
            print("[INFO] Clicked inside Notepad to focus.")
        else:
            print("[ERROR] Failed to find Notepad window for clicking.")
    except Exception as e:
        print(f"[ERROR] Error clicking inside Notepad: {e}")

def copy_notepad_content():
    """Copy content from Notepad."""
    try:
        # Ensure Notepad is in focus
        bring_to_forefront("Notepad")
        click_notepad()
        time.sleep(1)

        # Select all and copy
        pyautogui.hotkey("ctrl", "a")
        time.sleep(0.5)
        pyautogui.hotkey("ctrl", "c")
        time.sleep(0.5)

        # Retrieve content from clipboard
        content = pyperclip.paste()
        print("[INFO] Content copied from Notepad.")
        return content
    except Exception as e:
        print(f"[ERROR] Failed to copy content from Notepad. Error: {e}")
        return None

def write_notepad_content(content: str):
    """Write content to Notepad."""
    try:
        open_application("notepad")
        time.sleep(2)
        pyautogui.typewrite(content, interval=0.05)
        print("[INFO] Content written to Notepad.")
    except Exception as e:
        print(f"[ERROR] Failed to write content to Notepad. Error: {e}")

##############################################################################
# RUN & DEBUG HELPERS
##############################################################################

def run_python_code_in_vscode_terminal(file_path: str):
    """
    Runs the Python file in VS Code's integrated terminal using pyautogui to automate keyboard shortcuts.
    """
    if not file_path or not os.path.exists(file_path):
        print(f"[ERROR] File '{file_path}' does not exist.")
        return

    try:
        # Wait for VS Code to open the file
        time.sleep(5)

        # Bring VS Code to the front
        if not bring_window_to_front("Visual Studio Code"):
            print("[WARN] Could not bring VS Code to front.")

        # Additional delay to ensure VS Code is in focus
        time.sleep(2)

        # Open integrated terminal
        # Windows/Linux: Ctrl + `
        # macOS: Cmd + `
        if os.name == 'nt' or sys.platform.startswith("linux"):
            pyautogui.hotkey('ctrl', '`')
        elif sys.platform == "darwin":
            pyautogui.hotkey('command', '`')
        else:
            pyautogui.hotkey('ctrl', '`')

        # Wait for terminal to open
        time.sleep(2)

        # Type the command to run the Python script
        run_command = f'python "{file_path}"'
        pyautogui.typewrite(run_command, interval=0.05)
        pyautogui.press('enter')
        print(f"[INFO] Executing '{run_command}' in VS Code's integrated terminal.")

    except Exception as e:
        print(f"[ERROR] Failed to run code in VS Code's terminal: {e}")

def run_python_script(file_path: str):
    """
    Runs the Python script using subprocess and captures output and errors.
    """
    if not file_path or not os.path.exists(file_path):
        print(f"[ERROR] File '{file_path}' does not exist.")
        return

    try:
        # Execute the Python script
        result = subprocess.run(
            ['python', file_path],
            capture_output=True,
            text=True,
            check=False  # Set to True to raise exceptions on errors
        )

        # Print stdout and stderr
        if result.stdout:
            print(f"[OUTPUT]\n{result.stdout}")
        if result.stderr:
            print(f"[ERROR OUTPUT]\n{result.stderr}")

        # Optionally, handle errors by sending them back to GPT for debugging
        if result.returncode != 0:
            error_message = result.stderr
            # Feed error_message back to GPT to fix the code
            # Implement your error handling logic here
            print("[INFO] There was an error executing the script. You can debug it manually or implement automated debugging.")

    except Exception as e:
        print(f"[ERROR] Failed to execute the script: {e}")

##############################################################################
# USER INPUT PARSING
##############################################################################

def parse_user_input(user_input: str) -> dict:
    """
    Parses the user input to extract folder name and file name.
    Returns a dictionary with 'folder_name' and 'file_name'.
    Defaults are provided if not specified.
    """
    folder_name = "GPT_Code_Solutions"
    file_name = "solution.py"

    # Attempt to extract folder name
    folder_match = re.search(r'folder\s+called\s+"([^"]+)"', user_input, re.IGNORECASE)
    if folder_match:
        folder_name = folder_match.group(1)
        print(f"[INFO] Detected folder name: {folder_name}")

    # Attempt to extract file name
    file_match = re.search(r'file\s+"([^"]+)"', user_input, re.IGNORECASE)
    if file_match:
        file_name = file_match.group(1)
        print(f"[INFO] Detected file name: {file_name}")

    return {"folder_name": folder_name, "file_name": file_name}

##############################################################################
# COMMAND INTERPRETATION AND EXECUTION
##############################################################################

def interpret_command(command: str) -> dict:
    """Use OpenAI API to interpret the command."""
    prompt = (
        f"You are an AI assistant. Interpret the following user command as an automation task.\n"
        f"Return a JSON object with 'action' and 'parameters' based on the command.\n"
        f"Examples:\n"
        f"- Input: 'Copy content from Notepad and save it as a file named notes.txt'\n"
        f"  Output: {{\"action\": \"copy_notepad_content\", \"parameters\": {{\"file_name\": \"notes.txt\"}}}}\n"
        f"- Input: 'Open Notepad and write Hello'\n"
        f"  Output: {{\"action\": \"write_notepad_content\", \"parameters\": {{\"content\": \"Hello\"}}}}\n"
        f"- Input: 'Open Visual Studio Code with solution.py'\n"
        f"  Output: {{\"action\": \"open_vscode\", \"parameters\": {{\"file_path\": \"path\to\solution.py\"}}}}\n"

        f"Input: {command}\nOutput:"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.5
        )
        interpreted = response.choices[0].message.content.strip()
        return json.loads(interpreted)
    except Exception as e:
        print(f"[ERROR] Error interpreting command: {e}")
        return {}

def execute_action(parsed_command: dict):
    """Execute the parsed automation task."""
    if not parsed_command:
        print("[ERROR] Invalid command. Unable to execute.")
        return

    action = parsed_command.get("action", "").lower()
    parameters = parsed_command.get("parameters", {})

    if action == "copy_notepad_content":
        file_name = parameters.get("file_name", "copied_content.txt")
        content = copy_notepad_content()
        if content:
            save_to_file(os.path.join(create_folder_on_desktop("GPT_Code_Solutions")), file_name, content)
    elif action == "write_notepad_content":
        content = parameters.get("content", "")
        if content:
            write_notepad_content(content)
    elif action == "open_vscode":
        file_path = parameters.get("file_path", "")
        if file_path:
            open_or_focus_vscode(file_path)
    elif action == "solve_problem":
        problem = parameters.get("problem", "")
        if problem:
            solve_problem_in_vscode(problem)
    else:
        print("[WARN] Action not recognized or unsupported.")



def save_to_file(folder_path: str, file_name: str, content: str):
    """Save the copied content into a new file on disk."""
    if not folder_path:
        print("[ERROR] Invalid folder path. Cannot save file.")
        return

    file_path = os.path.join(folder_path, file_name)
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)
        print(f"[INFO] Content saved to file: {file_path}")
    except Exception as e:
        print(f"[ERROR] Failed to save content to file '{file_name}': {e}")


##############################################################################
# MAIN SOLVER LOGIC
##############################################################################

def solve_problem_in_vscode(problem: str, max_attempts=5):
    """
    1. Parse the problem statement to extract folder and file names.
    2. Ask GPT to generate Python code that solves 'problem'.
    3. Write code to a local file on the Desktop.
    4. Open or focus VS Code with that file.
    5. Run the code in VS Code's integrated terminal.
    6. have a print statement of answer in the code. 
    7. If there's an error, feed the error back to GPT to fix the code.
       Repeat until success or max_attempts is reached.
    """
    # Step 1: Parse user input for folder and file names
    names = parse_user_input(problem)
    folder_name = names.get("folder_name", "GPT_Code_Solutions")
    file_name = names.get("file_name", "solution.py")

    # Step 2: Create a folder on Desktop
    folder_path = create_folder_on_desktop(folder_name)
    if not folder_path:
        print("[ERROR] Aborting due to folder creation failure.")
        return

    # Step 3: GPT generates code
    print("\n[INFO] Generating initial solution with GPT...\n")
    initial_prompt = (
        f"You are given this problem statement:\n\n"
        f"---\n{problem}\n---\n\n"
        "Please write a fully working Python solution. "
        "Ensure that the response contains only valid Python code without any explanations or additional text. "
        "Enclose the code within triple backticks and specify 'python' for proper formatting."
        "have a print statement of answer in the code."
    )
    code_solution = chat_with_gpt(initial_prompt)
    if not code_solution:
        print("[ERROR] Failed to generate code from GPT.")
        return

    # Step 4: Write code to file
    file_path = write_code_to_file(folder_path, file_name, code_solution)
    if not file_path:
        print("[ERROR] Failed to write code to file.")
        return

    # Step 5: Open in VS Code
    open_or_focus_vscode(file_path)

    # Step 6: Run the code in VS Code's integrated terminal
    run_python_code_in_vscode_terminal(file_path)

    # Step 7: Optional - Implement automated debugging by checking outputs/errors
    # Note: Automating error detection and re-generation requires advanced techniques
    # such as reading terminal outputs, which is non-trivial with pyautogui.
    # For now, the user can manually inspect and rerun if needed.

##############################################################################
# MAIN SCRIPT ENTRY
##############################################################################

def code_agent():
    print("============================================")
    print("   GPT-Code-Solver with Automated Debugging ")
    print("============================================")
    audio.speak("hey, so what do you wanna code ?")
    print("Type 'exit' or 'quit' to terminate.\n")
    print("Example Command:")
    print('"Open Notepad, copy the content as the problem statement, solve it in Visual Studio Code, and run the solution in the terminal."\n')

    while True:
        try:
            user_input = audio.listen().strip()
        except KeyboardInterrupt:
            audio.speak("\n[INFO] Exiting the assistant.")
            break

        if user_input.lower() in ["exit", "quit"]:
            audio.speak("[INFO] Exiting the assistant.")
            break

        if not user_input:
            audio.speak("[WARN] Empty input received. Please enter a valid command.")
            continue

        # Interpret the command using GPT
        parsed_command = interpret_command(user_input)
        execute_action(parsed_command)

        # If the command includes solving a problem, extract it from Notepad
        if "solve it in visual studio code" in user_input.lower():
            problem_statement = copy_notepad_content()
            if problem_statement:
                solve_problem_in_vscode(problem_statement)
