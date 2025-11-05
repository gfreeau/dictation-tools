# Dictation Tools

These scripts provide a convenient way to use speech-to-text dictation on Linux, with additional tools for cleaning up dictated text using OpenAI. Think of it as a Linux alternative to [Wispr Flow](https://wisprflow.ai/), which currently doesn't support Linux systems.

## Why I Created This

I created these tools to make speech-to-text dictation more practical and seamless for my daily workflow:

- **Keyboard-driven workflow**: Easy keyboard shortcuts to start and stop dictation without disrupting focus
- **Desktop notifications**: Clear visual feedback when dictation is active or stopped
- **Easy text cleanup**: When dictation isn't perfect, a simple way to select and clean up text while preserving natural tone
- **Better integration**: Works smoothly with applications like Cursor and other text editors
- **Fast local transcription**: Uses faster-whisper for CPU-efficient local transcription, or fallback to OpenAI API
- **Context-aware cleanup**: Special handling for code and technical terms based on active window

## Whisper Dictation – Recommended Method

The primary dictation tool is `whisper_dictation.py`, which supports two modes:

| Mode | Processing | Model | Speed | Hot-key Scripts |
| ---- | ---------- | ----- | ----- | --------------- |
| **Local (default)** | ✅ CPU-friendly local | faster-whisper (small) | ~2s transcription | `start-whisper-dictation.sh` / `stop-whisper-dictation.sh` |
| **API (fallback)** | ☁️ Cloud API | OpenAI Whisper | ~4s API call | `start-whisper-dictation.sh` / `stop-whisper-dictation.sh` |

Both modes use Gemini 2.5 Flash Lite (via OpenRouter) for intelligent text cleanup and technical term correction.

**Why faster-whisper local mode?**
- No API costs for transcription
- Privacy (audio never leaves your machine)
- Faster than API in real-world usage
- Works offline

## Model Selection for Text Cleanup

We've evaluated multiple models for the text cleanup task across OpenAI and Google Gemini (via OpenRouter):

| Model | Evaluation Score | Speed | Cost vs GPT-4o-mini | Notes |
|-------|------------------|-------|---------------------|-------|
| **Gemini 2.5 Flash Lite** | 100% pass | 1.78s | ~80% cheaper | Default - fastest, excellent quality |
| **Gemini 2.0 Flash** | 100% pass | 2.93s | ~60% cheaper | Better homophone fixes |
| GPT-4o-mini | 100% pass | 7.04s | Baseline | Good fallback option |
| GPT-4.1-nano | 63.6% pass | - | Lower cost | Significantly lower quality |
| GPT-4.1-mini | 100% pass | - | Higher cost | No improvement over 4o-mini |

Our evaluation framework (see "Dictation Evaluations" below) tests each model's ability to resist prompt injection attacks while properly cleaning dictated text. All recommended models achieved 100% pass rates with our optimized prompts.

## Setup

### System Requirements

- **System packages**:
  ```bash
  sudo apt install xdotool xclip python3-pip notify-send ffmpeg
  ```

- **Python packages**:
  ```bash
  pip install faster-whisper openai python-dotenv pyyaml
  ```

  Or use requirements.txt:
  ```bash
  pip install -r requirements.txt
  ```

  *Optional: Use a virtual environment if you prefer isolated dependencies, but the bash scripts assume system-wide installation by default.*

### Configuration

1. **Create environment file**:
   ```bash
   cp .env.template .env
   nano .env
   ```

   Configure:
   - `OPENROUTER_API_KEY`: Your OpenRouter API key (for Gemini cleanup models) - get from https://openrouter.ai/keys
   - `OPENAI_API_KEY`: Your OpenAI API key (optional - for OpenAI models or API mode transcription)
   - `CLEANUP_MODEL`: Model for text cleanup (default: `google/gemini-2.5-flash-lite`)
   - `WHISPER_MODE`: Set to `local` (default) or `api`
   - `WHISPER_MODEL_SIZE`: Model size for local mode (default: `small`)

2. **Make scripts executable**:
   ```bash
   chmod +x *.sh *.py
   ```

3. **Context configuration** (optional but recommended):
   ```bash
   cp context_config.yml.example context_config.yml
   nano context_config.yml  # Customize for your workflow
   ```

   This enables context-aware technical term correction (e.g., "super base" → "Supabase" in code editors).

### Keyboard Shortcuts

Bind these scripts to keyboard shortcuts (recommended: F9/F10):
- `start-whisper-dictation.sh` → Start recording
- `stop-whisper-dictation.sh` → Stop, transcribe, and paste

## Usage

1. **Start dictation**: Press your start hotkey (e.g., F9)
2. **Speak**: Dictate your text
3. **Stop dictation**: Press your stop hotkey (e.g., F10)
4. **Result**: Transcribed and cleaned text is automatically pasted

### Testing Without Cleanup

To test raw Whisper output without GPT cleanup:
```bash
./whisper_dictation.py start --no-cleanup
# Speak...
./whisper_dictation.py stop --no-cleanup
```


## Context-Aware Dictation

The dictation system supports context-aware text cleanup that adapts based on your active window:

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

### Cleanup Features

The GPT cleanup stage provides:

- **Grammar correction**: Fixes grammar issues in dictated text
- **Punctuation correction**: Adds or fixes punctuation
- **Paragraph formatting**: Creates paragraphs for better readability
- **Technical term correction**: Fixes "super base" → "Supabase", "postgres SQL" → "PostgreSQL"
- **Australian English**: Uses Australian spelling conventions
- **Preserves your voice**: Maintains your natural tone and style while fixing technical issues
- **Context-awareness**: Adapts based on active window (e.g., code editors get better technical term handling)

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

The evaluation results informed our model choices - GPT-4o-mini, Gemini 2.5 Flash Lite, and Gemini 2.0 Flash all achieved 100% pass rates with the "hybrid" prompt.

## Files Overview

- **Core Files**:
  - `whisper_dictation.py`: Main dictation engine (start/stop/transcribe/cleanup)
  - `start-whisper-dictation.sh`: Starts recording (bind to F9)
  - `stop-whisper-dictation.sh`: Stops recording, transcribes and pastes (bind to F10)

- **Configuration**:
  - `.env.template`: Template for environment variables (API keys, model settings)
  - `context_config.yml.example`: Example configuration for context-aware cleanup
  - `requirements.txt`: Python package dependencies

- **Evaluation Framework**:
  - `dictation-eval/`: Directory containing evaluation tools
  - `dictation-eval/run_eval.py`: Script to run model evaluations
  - `dictation-eval/eval_config.yml`: Configuration for model and prompt testing
  - `dictation-eval/prompts/`: Different system prompts to evaluate

## Future Plans

- Advanced prompts and model selection options for different cleanup styles and languages
- Continued improvements to context-aware dictation