#!/usr/bin/env python3

import subprocess
import json
import sys
import os
from openai import OpenAI
from dotenv import load_dotenv

def check_command(command):
    try:
        subprocess.run(['which', command], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError:
        return False

def notify(title, message, timeout=3000):
    subprocess.run(['notify-send', '-t', str(timeout), title, message])

def main():
    load_dotenv()
    
    required_commands = ['xclip', 'xdotool', 'notify-send']
    for cmd in required_commands:
        if not check_command(cmd):
            print(f"Error: Required command '{cmd}' is not installed.", file=sys.stderr)
            sys.exit(1)
    
    # Get selected text using PRIMARY selection (text selected with mouse)
    try:
        selected_text = subprocess.run(
            ['xclip', '-o', '-selection', 'primary'], 
            check=True, 
            stdout=subprocess.PIPE, 
            text=True
        ).stdout
    except subprocess.CalledProcessError:
        selected_text = ""
    
    if not selected_text.strip():
        notify("Dictation Cleanup", "No text selected! Please select text with your mouse first.")
        sys.exit(1)
    
    notify("Dictation Cleanup", "Processing your text...", 3000)
    
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        notify("Dictation Cleanup", "Error: OpenAI API key not found in .env file", 5000)
        sys.exit(1)
    
    client = OpenAI(api_key=api_key)
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that cleans up dictated text. Only fix grammar, spelling, and punctuation errors and create paragraphs for readability. MAKE NO OTHER CHANGES TO THE INPUT TEXT. Do not add any extra text, commentary, or introductory phrases. You should use the entire input text to help determine the correct spelling to use by understanding the context of the text. Simply output the cleaned text as it was dictated. Use Australian english for spelling. FOLLOW THESE INSTRUCTIONS EXACTLY."
                },
                {
                    "role": "user",
                    "content": selected_text
                }
            ],
            temperature=0
        )
        
        cleaned_text = response.choices[0].message.content
        
        if not cleaned_text.strip():
            notify("Dictation Cleanup", "Failed to get cleaned text from API response.", 5000)
            sys.exit(1)
        
        # Copy the cleaned text to clipboard
        subprocess.run(['xclip', '-selection', 'clipboard'], input=cleaned_text.encode(), check=True)
        
        # Paste the cleaned text (replacing the selection)
        subprocess.run(['xdotool', 'key', 'ctrl+v'], check=True)
        
        notify("Dictation Cleanup", "Text has been cleaned up!", 3000)
        
    except Exception as e:
        notify("Dictation Cleanup", f"Error: {str(e)}", 5000)
        sys.exit(1)

if __name__ == "__main__":
    main() 