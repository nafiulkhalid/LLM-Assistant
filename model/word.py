import win32com.client

def write_solution_to_word(solution_text):
    """
    Writes the provided solution_text at the end of the active Word document.
    Assumes that MS Word is already running with an active document.
    """
    try:
        # Try to get the currently active instance of Word
        word_app = win32com.client.GetActiveObject("Word.Application")
    except Exception as e:
        print("Error: Could not get the active Word application instance.", e)
        return

    try:
        # Get the active document
        active_doc = word_app.ActiveDocument

        # Define a range at the end of the document
        rng = active_doc.Range()
        rng.Collapse(0)  # 0 indicates collapse to the end of the range

        # Insert the solution text (you can also add formatting if needed)
        rng.InsertAfter("\n" + solution_text + "\n")

        # Ensure the Word window is visible
        word_app.Visible = True

        print("Solution successfully written to the Word document.")
    except Exception as e:
        print("Error writing to the Word document:", e)

# Example usage:
if __name__ == "__main__":
    # Let's assume Gemini-Vision (or any other module) provides your solution text
    solution_text = "Here is the generated solution from Gemini-Vision."

    # Write the solution to the active Word file
    write_solution_to_word(solution_text)
