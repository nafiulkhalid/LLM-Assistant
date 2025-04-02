
https://github.com/user-attachments/assets/c78b30b3-e6f4-4c04-b6cb-e59f8f983aac

# AERO
## Automated Execution and Response Orchestrator
### Efficiency at your command. Intelligence at your fingertips. This is AERO.

>[!NOTE]
> Imagine having an assistant that doesn’t just answer questions but actually takes action—instantly. AERO is a smart, intuitive, and fully interactive AI assistant designed to simplify your digital life like never before. Once installed and set to run in the background, AERO springs to life the moment you say, “Hey AERO.”
---

# Design Document:   

### What is AERO?  

> Hands free Virtual Assistant  
> Siri + JARVIS (IronMan)  

### Technology?  

- **Python**  
- **LLM** - Groq (faster interpreter), Gemini (vision, homework, coding)  
- **Audio** – 11Labs (text to speech), DeepGram (speech to text) (mp3) (Transcribe)  
- **Selenium + OpenCV + Gemini Vision 1.5 Flash** (Web Navigation)  
- **Voice Model** – Samara  
- **API** – Gemini, OpenAI, Groq, 11Labs, Deepgram  
- **OAuth** – Zoom, Google Calendar  

### Use-cases?  

- **Disabled people** who have a hard time interacting with devices  
- **Busyness** – Automating routine tasks  
- **Faster Execution** – Reduce time spent on repetitive tasks  

### Structure  

- **base.py (OpenAI)**  
  - Classifies input into features  
  - General processing file  

- **Audio**  
  - Functions: `speak()`, `listen()`  

- **Application**  
  - Opens subprocesses using system calls  
  - Manages OS-level automation  

- **Credentials**  
  - OAuth integration for Zoom & Google Calendar  
  - Stores tokens in `token.json` (valid for 60 minutes)  

- **Gemini**  
  - **Visualize**: Converts images into models, code, and plots using Vision & Matplotlib  
  - **Live Translation**:  
    - Image → Model 1.5 → Text (any language)  
    - Model 1.5 → Translation (English) → Speak  

- **Therapy Mode**  
  - Uses Groq to generate AI-driven prompts  
  - Provides spoken conversational support  

- **Website**  
  - Built with **JavaScript** (CSS + Bootstrap) and **HTML**  

---

A TreeHacks2025 Project

---
* TreeHacks is the annual hackathon of Stanford University
