# Dictation Tools

These scripts provide a convenient way to use speech-to-text dictation on Linux, with additional tools for cleaning up dictated text using OpenAI. Think of it as a Linux alternative to [Wispr Flow](https://wisprflow.ai/), which currently doesn't support Linux systems.

## Why I Created This

I created these tools to make speech-to-text dictation more practical and seamless for my daily workflow:

- **Keyboard-driven workflow**: Easy keyboard shortcuts to start and stop dictation without disrupting focus
- **Desktop notifications**: Clear visual feedback when dictation is active or stopped
- **Easy text cleanup**: When dictation isn't perfect, a simple way to select and clean up text while preserving natural tone
- **Better integration**: Works smoothly with applications like Cursor and other text editors
- **Multiple engine options**: Use either local (Vosk) or cloud (Whisper) transcription based on your needs
- **Context-aware cleanup**: Special handling for code and technical terms when in Cursor IDE

## Two Dictation Engines – Choose Your Preferred Method

This repository ships with **two completely separate dictation engines** that you can benchmark against each other:

| Engine | Processing | Model | Hot-key Scripts | Init Required? |
| ------ | ---------- | ----- | --------------- | -------------- |
| **nerd-dictation / Vosk** | ✅ 100% local | Vosk acoustic model | `start-dictation.sh` / `stop-dictation.sh` | Yes (`init-dictation.sh`) |
| **Whisper (OpenAI API)** | ☁️ Cloud API | OpenAI Whisper | `start-whisper-dictation.sh` / `stop-whisper-dictation.sh` | No |

Both flows share the same cleaning pipeline and use GPT-4.1 Nano for text refinement. This allows for direct comparison of transcription quality, latency, and usability.

## Common Requirements (Both Methods)

- **System packages**:
  ```
  sudo apt install xdotool xclip python3-pip notify-send
  ```

- **Python packages**:
  ```
  pip install openai python-dotenv
  ```

- **OpenAI API key**:
  Create a `.env` file with your OpenAI API key (used for cleanup and Whisper):
  ```
  cp .env.template .env
  nano .env
  ```
  Replace "your_api_key_here" with your actual OpenAI API key.

- **Make scripts executable**:
  ```
  chmod +x *.sh *.py
  ```

## Method 1: Local Dictation with nerd-dictation (Vosk)

### Additional Requirements

- **[nerd-dictation](https://github.com/ideasman42/nerd-dictation)**: 
  ```
  git clone https://github.com/ideasman42/nerd-dictation.git
  cd nerd-dictation
  pip3 install vosk
  ```
  **IMPORTANT**: Complete ALL the installation steps in the [nerd-dictation README](https://github.com/ideasman42/nerd-dictation#install).

- **Vosk speech model** - Download from [alphacephei.com/vosk/models](https://alphacephei.com/vosk/models)
  - Minimum: [vosk-model-en-us-0.22-lgraph](https://alphacephei.com/vosk/models/vosk-model-en-us-0.22-lgraph.zip) (128M)
  - Better accuracy: [vosk-model-en-us-0.42-gigaspeech](https://alphacephei.com/vosk/models/vosk-model-en-us-0.42-gigaspeech.zip) (2.3GB)

### Setup

1. Create a configuration file:
   ```
   cp dictation.conf.template dictation.conf
   ```

2. Edit the configuration file:
   ```
   nano dictation.conf
   ```
   Configure:
   - `NERD_DICTATION_PATH`: Path to the nerd-dictation executable
   - `VOSK_MODEL_DIR`: Path to your extracted Vosk model directory
   - `START_DICTATION_KEY` and `STOP_DICTATION_KEY`: for notifications

3. Bind keyboard shortcuts:
   - `start-dictation.sh` → F9
   - `stop-dictation.sh` → F10

### Usage

1. **Initialize dictation** (run once per session):
   ```
   ./init-dictation.sh
   ```
   This loads the speech model and suspends it, ready for fast dictation.

2. **Check if dictation is ready** (optional but recommended for large models):
   ```
   ./check-dictation-ready.sh
   ```
   This monitors the initialization process and notifies you when the model is fully loaded.

3. **Start dictation**: Press F9 (or your configured key)
4. **Stop dictation**: Press F10 (or your configured key)

## Method 2: Cloud Dictation with OpenAI Whisper

### Additional Requirements

- **ffmpeg**:
  ```
  sudo apt install ffmpeg
  ```

### Setup

1. Make the scripts executable:
   ```
   chmod +x start-whisper-dictation.sh stop-whisper-dictation.sh whisper_dictation.py
   ```

2. Optional configuration:
   ```bash
   export WHISPER_TEMP_DIR=$HOME/tmp/whisper    # Change temp recording directory
   export WHISPER_CLEANUP=false                 # Disable GPT cleanup (raw Whisper output)
   ```

3. Bind keyboard shortcuts:
   - `start-whisper-dictation.sh` → F7
   - `stop-whisper-dictation.sh` → F8

### Usage

1. **Start Whisper dictation**: Press F7 (or your configured key)
2. **Stop Whisper dictation**: Press F8 (or your configured key)

That's it! No initialization step is needed as recordings are sent directly to the OpenAI API.

## Special Features of the Whisper Flow

* **Cursor-aware spelling fixes** – Automatically detects if your active window belongs to the Cursor IDE and adds extra context to the cleanup prompt:
  > "We are in Cursor … likely talking about programming or technology. Correct technical terms such as Supabase, PostgreSQL …"
* **No model download needed** – Audio processing happens in the cloud, so startup is instant
* **Simplified workflow** – No initialization required

## Text Cleanup (Common to Both Methods)

Both dictation methods can benefit from additional text cleanup:

1. Select text with your mouse
2. Press your configured shortcut (e.g., Ctrl+Alt+C)
3. The selected text will be replaced with cleaned-up text via GPT-4.1 Nano

### Cleanup Features

- **Grammar correction**: Fixes grammar issues in dictated text
- **Punctuation correction**: Adds or fixes punctuation
- **Paragraph formatting**: Creates paragraphs for better readability
- **Spelling correction**: Fixes spelling errors based on context
- **Australian English**: Uses Australian spelling conventions
- **Preserves your voice**: Maintains your natural tone and style while fixing technical issues

## Files Overview

- **Common Files**:
  - `.env.template`: Template for OpenAI API key configuration
  - `cleanup-dictation.py`: Cleans up selected text using GPT-4.1 Nano

- **nerd-dictation / Vosk Method**:
  - `dictation.conf.template`: Template configuration for nerd-dictation paths and settings
  - `init-dictation.sh`: Initializes the Vosk speech recognition system
  - `check-dictation-ready.sh`: Monitors initialization process and notifies when ready
  - `start-dictation.sh`: Starts/resumes nerd-dictation
  - `stop-dictation.sh`: Stops/suspends nerd-dictation

- **Whisper Method**:
  - `whisper_dictation.py`: Main Python driver for Whisper dictation
  - `start-whisper-dictation.sh`: Starts recording for Whisper
  - `stop-whisper-dictation.sh`: Stops recording, transcribes with Whisper and pastes

## Future Plans

- Integration with [OpenRouter](https://openrouter.ai/) to offer more model options and flexibility
- Advanced prompts and model selection options for different cleanup styles and languages
- Evals and quality control of the prompts and model outputs