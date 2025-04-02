# exit.py
from groq import Groq

# Initialize the Groq client with your API key
groq_client = Groq(api_key="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")

def is_exit_command(user_input):
    """
    Uses the Groq client to determine if the user's input indicates a desire to exit.

    The prompt instructs the model to classify the input as 'exit' if it indicates that 
    the user wants to exit, or 'continue' otherwise. Only a single word is expected in the response.
    
    Returns:
      True if the classification is 'exit'; False otherwise.
    """
    clean_input = user_input.strip()
    classification_prompt = f"""
Classify the following text as 'exit' if it indicates that the user wants to exit, 
or 'continue' if it does not. Only return one word.
Input: {clean_input}
Classification:"""
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a text classifier."},
                {"role": "user", "content": classification_prompt}
            ],
            max_tokens=1,
            temperature=0
        )
        classification = response.choices[0].message.content.strip().lower()
        return classification == "exit"
    except Exception as e:
        print("Error during exit classification:", e)
        # In case of an error, choose not to exit
        return False
