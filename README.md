# Dictation Tools

These scripts provide a convenient way to use speech-to-text dictation on Linux, with additional tools for cleaning up dictated text using OpenAI. Think of it as a Linux alternative to [Wispr Flow](https://wisprflow.ai/), which currently doesn't support Linux systems.

## Why I Created This

I created these tools to make speech-to-text dictation more practical and seamless for my daily workflow:

- **Keyboard-driven workflow**: Easy keyboard shortcuts to start and stop dictation without disrupting focus
- **Desktop notifications**: Clear visual feedback when dictation is active or stopped
- **Easy text cleanup**: When dictation isn't perfect, a simple way to select and clean up text while preserving natural tone
- **Better integration**: Works smoothly with applications like Cursor and other text editors
- **Multiple engine options**: Use either local (Vosk) or cloud (Whisper) transcription based on your needs
- **Context-aware cleanup**: Special handling for code and technical terms based on active window

## Two Dictation Engines – Choose Your Preferred Method

This repository ships with **two completely separate dictation engines** that you can benchmark against each other:

| Engine | Processing | Model | Hot-key Scripts | Init Required? |
| ------ | ---------- | ----- | --------------- | -------------- |
| **nerd-dictation / Vosk** | ✅ 100% local | Vosk acoustic model | `start-dictation.sh` / `stop-dictation.sh` | Yes (`init-dictation.sh`) |
| **Whisper (OpenAI API)** | ☁️ Cloud API | OpenAI Whisper | `start-whisper-dictation.sh` / `stop-whisper-dictation.sh` | No |

Both flows share the same cleaning pipeline and use GPT-4o-mini for text refinement. This allows for direct comparison of transcription quality, latency, and usability.

## Model Selection: GPT-4o-mini vs Alternatives

We've evaluated multiple models for the text cleanup task, and GPT-4o-mini consistently performs best for the price:

| Model | Evaluation Score | Cost Comparison | Notes |
|-------|------------------|-----------------|-------|
| GPT-4o-mini | 100% pass | Baseline | Best performance/price ratio |
| GPT-4.1-nano | 63.6% pass | Lower cost | Significantly lower quality results |
| GPT-4.1-mini | Similar to 4o-mini | Higher cost | No significant quality improvement |

Our evaluation framework (see "Dictation Evaluations" below) tests each model's ability to resist prompt injection attacks while properly cleaning dictated text. GPT-4o-mini achieved perfect scores with our optimized prompts.

## Common Requirements (Both Methods)

- **System packages**:
  ```
  sudo apt install xdotool xclip python3-pip notify-send
  ```

- **Python packages**:
  ```
  pip install openai python-dotenv pyyaml
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

- **Context configuration** (optional but recommended):
  ```
  cp context_config.yml.example context_config.yml
  nano context_config.yml  # Customize to your needs
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
   export WHISPER_TEMP_DIR=$HOME/tmp/whisper     # Change temp recording directory
   export WHISPER_CLEANUP=false                  # Disable GPT cleanup (raw Whisper output)
   export OPENAI_MODEL=gpt-4.1-nano             # Change model (not recommended)
   export WHISPER_CONTEXT_CONFIG=~/my-config.yml # Custom context config path
   ```

3. Bind keyboard shortcuts:
   - `start-whisper-dictation.sh` → F7
   - `stop-whisper-dictation.sh` → F8

### Usage

1. **Start Whisper dictation**: Press F7 (or your configured key)
2. **Stop Whisper dictation**: Press F8 (or your configured key)

That's it! No initialization step is needed as recordings are sent directly to the OpenAI API.

## Context-Aware Dictation

Both dictation methods now support context-aware text cleanup that adapts based on your active window:

### How it Works

1. When cleaning up text, the system detects your active window title
2. It matches this title against patterns in `context_config.yml`
3. If a match is found, additional context is added to the system prompt
4. This helps the AI understand specific terminology and formatting needs

### Configuration

Create your configuration file:
```
cp context_config.yml.example context_config.yml
```

The file uses regex patterns to match window titles:
```yaml
context_rules:
  - window_pattern: ".*Cursor$"
    description: "Cursor IDE coding context"
    extra_context: >
      Right now we are in Cursor, an application used to write code...
```

### Use Cases

- **IDE-specific**: Special handling for code in different editors
- **Email clients**: Format for email communication
- **Terminal**: Preserve command syntax and special characters
- **Document editors**: Formal language or specific formatting

The pattern-based approach makes it easy to customize for your specific applications and needs.

## Text Cleanup (Common to Both Methods)

Both dictation methods can benefit from additional text cleanup:

1. Select text with your mouse
2. Press your configured shortcut (e.g., Ctrl+Alt+C)
3. The selected text will be replaced with cleaned-up text via GPT-4o-mini

### Cleanup Features

- **Grammar correction**: Fixes grammar issues in dictated text
- **Punctuation correction**: Adds or fixes punctuation
- **Paragraph formatting**: Creates paragraphs for better readability
- **Spelling correction**: Fixes spelling errors based on context
- **Australian English**: Uses Australian spelling conventions
- **Preserves your voice**: Maintains your natural tone and style while fixing technical issues
- **Context-awareness**: Adapts to the specific application you're using

## Dictation Evaluations

The repository includes an evaluation framework to test different models and system prompts:

### Evaluation Framework

Located in `dictation-eval/`, the framework tests model resistance to prompt injection attacks while properly cleaning up dictated text.

```bash
cd dictation-eval
python3 run_eval.py  # Run evaluations
```

### What's Tested

- **Prompt injection resistance**: Tests if models follow instructions in dictated text
- **System prompt leakage**: Checks if models reveal their internal instructions
- **Question answering**: Verifies models don't answer questions in dictated text
- **Technical term handling**: Ensures correct spelling of technical terms

The evaluation results informed our choice of GPT-4o-mini with the "hybrid" prompt, which achieved a 100% pass rate.

## Files Overview

- **Common Files**:
  - `.env.template`: Template for OpenAI API key configuration
  - `cleanup-dictation.py`: Cleans up selected text using GPT-4o-mini
  - `context_config.yml.example`: Example configuration for context-aware cleanup

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

- **Evaluation Framework**:
  - `dictation-eval/`: Directory containing evaluation tools
  - `dictation-eval/run_eval.py`: Script to run evaluations
  - `dictation-eval/eval_config.yml`: Configuration for model and prompt testing
  - `dictation-eval/prompts/`: Different system prompts to evaluate

## Future Plans

- Integration with [OpenRouter](https://openrouter.ai/) to offer more model options and flexibility
- Advanced prompts and model selection options for different cleanup styles and languages
- Continued improvements to context-aware dictation