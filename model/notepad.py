import os
import subprocess
import tempfile
from groq import Groq
import audio

# Initialize the Groq client for notepad tasks
client = Groq(api_key="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")

def generate_notepad_content(topic):
    """
    Uses Groq to generate a well-structured and engaging piece of text on the given topic.
    
    Parameters:
      - topic: A string representing the topic.
      
    Returns:
      The generated content as a string.
    """
    prompt = f"""
You are a creative and knowledgeable writer. Generate a detailed, informative, and engaging article about:
{topic}

Write in a clear and concise manner, suitable for a notepad summary.
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=500
    )
    content = response.choices[0].message.content.strip()
    return content

def open_and_write_notepad():
    """
    Activates the notepad agent:
      - Announces via audio that notepad mode is active.
      - Listens for a voice command.
          * If the command contains "close notepad", it closes the Notepad window.
          * Otherwise, it treats the command as a writing prompt, generates text via Groq,
            writes the text to a temporary file, and opens it in Notepad.
    """
    # Announce that the notepad agent is active
    audio.speak("Hey, notepad agent is active. What would you like me to write?")
    
    # Listen for a voice command
    command = audio.listen().strip()
    if not command:
        audio.speak("I did not catch that. Please try again.")
        return

    # If the command includes a close instruction, close Notepad
    if "close notepad" in command.lower():
        audio.speak("Closing notepad.")
        os.system("taskkill /f /im notepad.exe")
        return

    # Otherwise, treat the command as a writing prompt
    audio.speak("Generating your note. Please wait.")
    content = generate_notepad_content(command)

    # Write the generated content to a temporary text file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8")
    temp_file.write(content)
    temp_file.close()

    audio.speak("Your note is ready. Opening Notepad.")
    # Open Notepad with the temporary file
    subprocess.Popen(["notepad.exe", temp_file.name])
