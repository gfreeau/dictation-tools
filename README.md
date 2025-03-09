# Dictation Tools

These scripts provide a convenient way to use [nerd-dictation](https://github.com/ideasman42/nerd-dictation) for natural speech-to-text on Linux, with additional tools for cleaning up dictated text using OpenAI. Think of it as a Linux alternative to [Wispr Flow](https://wisprflow.ai/), which currently doesn't support Linux systems.

## Why I Created This

I created these tools to make speech-to-text dictation more practical and seamless for my daily workflow:

- **Keyboard-driven workflow**: I needed easy keyboard shortcuts to start and stop dictation without disrupting my focus
- **Desktop notifications**: Clear visual feedback when dictation is active or stopped
- **Easy text cleanup**: When dictation isn't perfect, I wanted a simple way to select and clean up text using more powerful LLMs but also preserve my natural tone
- **Better integration**: Works smoothly with applications like Cursor and other text editors
- **Optimized performance**: Initialize the heavy speech model once at startup, then enjoy faster dictation throughout your session
- **Privacy-focused**: All speech processing happens locally on your computer - no audio sent to the cloud

## Requirements

Before setting up, ensure you have the following installed:

- **System packages**:
  ```
  sudo apt install xdotool xclip python3-pip notify-send
  ```

- **Python packages** (or use the provided requirements.txt):
  ```
  pip install openai python-dotenv
  ```

- **[nerd-dictation](https://github.com/ideasman42/nerd-dictation)** - First, follow the complete installation instructions from the nerd-dictation repository:
  ```
  git clone https://github.com/ideasman42/nerd-dictation.git
  cd nerd-dictation
  pip3 install vosk  # Required by nerd-dictation
  ```
  **IMPORTANT**: Complete ALL the installation steps in the [nerd-dictation README](https://github.com/ideasman42/nerd-dictation#install) before proceeding with this setup.

- **Vosk speech model** - Download from [alphacephei.com/vosk/models](https://alphacephei.com/vosk/models)
  - Minimum recommended: [vosk-model-en-us-0.22-lgraph](https://alphacephei.com/vosk/models/vosk-model-en-us-0.22-lgraph.zip) (128M)
  - For better accuracy: [vosk-model-en-us-0.42-gigaspeech](https://alphacephei.com/vosk/models/vosk-model-en-us-0.42-gigaspeech.zip) (2.3GB)

## Setup

1. **Verify nerd-dictation works first**: Before proceeding, make sure you can run nerd-dictation successfully on its own following their [installation instructions](https://github.com/ideasman42/nerd-dictation#install).

2. Make all scripts executable:
   ```
   chmod +x *.sh *.py
   ```

3. Create a configuration file by copying the template:
   ```
   cp dictation.conf.template dictation.conf
   ```

4. Edit the configuration file to match your setup:
   ```
   nano dictation.conf
   ```
   
   Configure the following:
   - `NERD_DICTATION_PATH`: Path to the nerd-dictation executable
   - `VOSK_MODEL_DIR`: Path to your extracted Vosk model directory
   - `START_DICTATION_KEY` and `STOP_DICTATION_KEY`: if you want your keyboard shortcuts showing up in notifications

5. If you haven't already downloaded a Vosk model during nerd-dictation setup, download and extract one now:
   ```
   wget https://alphacephei.com/vosk/models/vosk-model-en-us-0.42-gigaspeech.zip
   unzip vosk-model-en-us-0.42-gigaspeech.zip
   ```
   Then update the `VOSK_MODEL_DIR` in your dictation.conf to point to this directory.

6. For the cleanup-dictation.py script (which uses OpenAI's API), create a .env file with your OpenAI API key:
   ```
   cp .env.template .env
   nano .env
   ```
   Replace "your_api_key_here" with your actual OpenAI API key.

7. **REQUIRED**: Set up keyboard shortcuts in your desktop environment
   This step is **mandatory** - the tools are designed to be used via keyboard shortcuts:
   - Assign `start-dictation.sh` to a key like F9
   - Assign `stop-dictation.sh` to a key like F10
   - Assign `cleanup-dictation.py` to a key like Ctrl+Alt+C

## Usage

### Basic Workflow

1. **Initialize dictation** (run once at the beginning of your session):
   ```
   ./init-dictation.sh
   ```
   This loads the speech model and immediately suspends, ready for fast dictation. This is just an initialisation command you could set to run on boot. It needs to be run before dictation will work.

2. **Start dictating** (press your configured keyboard shortcut - do NOT run the script directly):
   Press your configured shortcut (e.g., F9) to start dictation.
   Speak naturally into your microphone.

3. **End dictation** (press your configured keyboard shortcut - do NOT run the script directly):
   Press your configured shortcut (e.g., F10) to end dictation.
   This processes the text and inserts it at your cursor position.

4. **Clean up dictated text** (optional):
   1. Select text with your mouse
   2. Press your configured shortcut (e.g., Ctrl+Alt+C) - do NOT run the script directly
   3. The selected text will be replaced with cleaned-up text via OpenAI

## Features

### Dictation Features
- **Configurable paths**: Easy setup through dictation.conf
- **High-quality speech model**: Using Vosk models for superior accuracy
- **Full sentence capitalization**: First word of sentences is capitalized
- **Numbers as digits**: Numbers are converted to digits (e.g., "twenty three" becomes "23")
- **Number separators**: Large numbers use comma separators (e.g., "one thousand" becomes "1,000")
- **Punctuation**: Automatic punctuation based on pauses
- **Fast operation**: Using suspend/resume for quick dictation without reloading the model

### Cleanup Features (via OpenAI GPT-3.5 Turbo)
- **Grammar correction**: Fixes grammar issues in dictated text
- **Punctuation correction**: Adds or fixes punctuation
- **Paragraph formatting**: Creates paragraphs for better readability
- **Spelling correction**: Fixes spelling errors based on context
- **Australian English**: Uses Australian spelling conventions
- **Preserves your voice**: Maintains your natural tone and style while fixing technical issues

## Files

- `dictation.conf.template`: Template configuration file for paths and shortcuts. Copy and create `dictation.conf`
- `init-dictation.sh`: Initializes the dictation system (run directly)
- `start-dictation.sh`: Starts/resumes dictation (use ONLY via keyboard shortcut)
- `stop-dictation.sh`: Stops/suspends dictation (use ONLY via keyboard shortcut)
- `cleanup-dictation.py`: Cleans up selected text using OpenAI (use ONLY via keyboard shortcut)
- `.env.template`: Template for OpenAI API key configuration. Copy and create `.env`

## Future Plans

- The cleanup functionality currently uses GPT-3.5 Turbo, which provides excellent results without requiring more expensive models
- Future versions may include integration with [OpenRouter](https://openrouter.ai/) to offer more model options and flexibility
- Building more advanced prompts and model selection options for different cleanup styles and languages
- Building evals and ensure quality control of the prompts and model outputs