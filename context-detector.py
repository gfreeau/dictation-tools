#!/usr/bin/env python3

import subprocess
import os
import sys
import re
import traceback

def get_active_window_info():
    """Get information about the currently active window using xdotool"""
    try:
        # Get window ID of active window
        window_id = subprocess.check_output(
            ["xdotool", "getactivewindow"], 
            text=True,
            stderr=subprocess.PIPE
        ).strip()
        
        # Get window name (typically contains app name and often the file)
        window_name = subprocess.check_output(
            ["xdotool", "getwindowname", window_id], 
            text=True,
            stderr=subprocess.PIPE
        ).strip()
        
        print(f"Window Name: {window_name}")
        
        # Try to get application name from window title
        app_name = extract_app_name_from_title(window_name)
        
        return {
            "window_name": window_name,
            "app_name": app_name
        }
    except subprocess.CalledProcessError as e:
        error_msg = f"Failed to get window info: {str(e)}"
        print(error_msg)
        return {"error": error_msg}
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(error_msg)
        return {"error": error_msg}

def extract_app_name_from_title(window_name):
    """Try to extract application name from window title"""
    # Common application patterns in window titles
    app_patterns = {
        "Visual Studio Code": r'.*Visual Studio Code$',
        "Cursor": r'.*Cursor$',
        "Sublime Text": r'.*Sublime Text$',
        "Terminal": r'^Terminal$',
        "Firefox": r'.*Firefox$',
        "Chrome": r'.*Chrome$',
        "Slack": r'.*Slack.*$',
        "Discord": r'.*Discord.*$',
        "Gmail": r'.*Gmail.*$',
        "Outlook": r'.*Outlook.*$',
        "Word": r'.*Word.*$',
        "Excel": r'.*Excel.*$',
    }
    
    for app, pattern in app_patterns.items():
        if re.match(pattern, window_name):
            return app
    
    # If no match, try to get the last part after dash
    parts = window_name.split(' - ')
    if len(parts) > 1:
        return parts[-1]
    
    return "Unknown"

def extract_file_info_from_title(window_name):
    """Try to extract filename and directory from window title using common patterns"""
    # Common patterns in window titles with directory information
    patterns = [
        # VSCode: "filename.ext - directory - Visual Studio Code"
        r'^(.*?) - (.*) - Visual Studio Code$',
        # Cursor: "filename.ext - directory - Cursor"
        r'^(.*?) - (.*) - Cursor$',
        # Sublime Text: "filename.ext (directory) - Sublime Text"
        r'^(.*?) \((.*)\) - Sublime Text$',
        # Generic: "filename.ext - directory"
        r'^(.*?) - (.*)$',
    ]
    
    for pattern in patterns:
        match = re.match(pattern, window_name)
        if match:
            filename = match.group(1)
            directory = match.group(2)
            
            # Extract file extension if present
            extension = None
            if '.' in filename:
                extension = os.path.splitext(filename)[1].lstrip('.')
            
            return {
                "filename": filename,
                "extension": extension,
                "directory": directory
            }
    
    # If no directory information found, just extract filename
    simple_patterns = [
        # Vim/Neovim in terminal: "filename.ext [vim]"
        r'^(.*?) \[vim\]$',
        # Generic filename only
        r'^(.*)$',
    ]
    
    for pattern in simple_patterns:
        match = re.match(pattern, window_name)
        if match:
            filename = match.group(1)
            
            # Extract file extension if present
            extension = None
            if '.' in filename:
                extension = os.path.splitext(filename)[1].lstrip('.')
            
            return {
                "filename": filename,
                "extension": extension,
                "directory": None
            }
    
    return {
        "filename": None,
        "extension": None,
        "directory": None
    }

def show_notification(title, message):
    """Show a notification using notify-send"""
    try:
        subprocess.run(["notify-send", "-t", "10000", title, message], check=True)
        print(f"Notification sent: {title}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to show notification: {str(e)}")
    except Exception as e:
        print(f"Unexpected error showing notification: {str(e)}")

def get_context():
    """Get the current context information"""
    # Get active window information
    window_info = get_active_window_info()
    
    if "error" in window_info:
        return {"error": window_info["error"]}
    
    # Extract filename, extension and directory from window title
    file_info = extract_file_info_from_title(window_info["window_name"])
    
    # Combine all context information
    context = {
        "app_name": window_info["app_name"],
        "window_name": window_info["window_name"],
        "filename": file_info["filename"],
        "extension": file_info["extension"],
        "file_directory": file_info["directory"]
    }
    
    return context

def main():
    print("Starting context detection...")
    
    try:
        # Get context information
        context = get_context()
        
        if "error" in context:
            show_notification("Context Detection Error", context["error"])
            return 1
        
        # Prepare notification message
        message = f"""
Application: {context['app_name']}
Window Title: {context['window_name']}
Detected File: {context['filename'] or 'None detected'}
File Extension: {context['extension'] or 'Unknown'}
File Directory: {context['file_directory'] or 'Unknown'}
"""
        
        # Show notification with the gathered information
        show_notification("Context Detection Results", message)
        
        # Print context as JSON for potential programmatic use
        print("\nContext information:")
        for key, value in context.items():
            print(f"  {key}: {value}")
        
        return 0
    except Exception as e:
        error_msg = f"Unexpected error in main: {str(e)}"
        print(error_msg)
        show_notification("Context Detection Error", error_msg)
        return 1

if __name__ == "__main__":
    sys.exit(main()) 