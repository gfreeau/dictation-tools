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
| **Local (default)** | ✅ CPU-friendly local | faster-whisper (small) | ~2s transcription | `toggle-whisper-dictation.sh` (recommended) or `start`/`stop` scripts |
| **API (fallback)** | ☁️ Cloud API | OpenAI Whisper | ~4s API call | `toggle-whisper-dictation.sh` (recommended) or `start`/`stop` scripts |

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
  sudo apt install xdotool xclip python3-venv ffmpeg libnotify-bin
  ```

- **Python virtual environment setup**:
  ```bash
  # Create virtual environment
  python3 -m venv venv

  # Activate it
  source venv/bin/activate

  # Install Python dependencies
  pip install -r requirements.txt
  ```

  The launcher scripts (`start-whisper-dictation.sh`, `stop-whisper-dictation.sh`, `toggle-whisper-dictation.sh`) automatically use the venv, so you don't need to activate it manually when using keyboard shortcuts.

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

3. **Pre-download Whisper models** (recommended):
   ```bash
   source venv/bin/activate
   python3 -c "from faster_whisper import WhisperModel; model = WhisperModel('small', device='cpu', compute_type='int8')"
   ```

   This downloads the model ahead of time so your first dictation isn't delayed. Replace `'small'` with your chosen model size (`base`, `medium`, `large-v3`, etc.) to match your `WHISPER_MODEL_SIZE` setting in `.env`.

4. **Context configuration** (optional but recommended):
   ```bash
   cp context_config.yml.example context_config.yml
   nano context_config.yml  # Customize for your workflow
   ```

   This enables context-aware technical term correction (e.g., "super base" → "Supabase" in code editors).

### Keyboard Shortcuts

You can choose between two workflows:

**Option 1: Single-key toggle (recommended)**
- `toggle-whisper-dictation.sh` → Press once to start, press again to stop, transcribe, and paste
- Bind to a single key (e.g., F9)

**Option 2: Two-key workflow**
- `start-whisper-dictation.sh` → Start recording (e.g., F9)
- `stop-whisper-dictation.sh` → Stop, transcribe, and paste (e.g., F10)

## Usage

**Single-key toggle workflow:**
1. **Start dictation**: Press your toggle key (e.g., F9)
2. **Speak**: Dictate your text
3. **Stop dictation**: Press the same key again
4. **Result**: Transcribed and cleaned text is automatically pasted

**Two-key workflow:**
1. **Start dictation**: Press your start key (e.g., F9)
2. **Speak**: Dictate your text
3. **Stop dictation**: Press your stop key (e.g., F10)
4. **Result**: Transcribed and cleaned text is automatically pasted

### Testing Without Cleanup

To test raw Whisper output without LLM cleanup:
```bash
./whisper_dictation.py start --no-cleanup
# Speak...
./whisper_dictation.py stop --no-cleanup
```

Or with toggle mode:
```bash
./whisper_dictation.py toggle --no-cleanup  # start
# Speak...
./whisper_dictation.py toggle --no-cleanup  # stop
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

The file uses regex patterns to match window titles and supports two types of customization:

```yaml
context_rules:
  - window_pattern: ".*Visual Studio Code.*"
    description: "VS Code IDE coding context"
    paste_key: "ctrl+shift+v"  # Custom paste shortcut
    extra_context: >
      Right now we are in Cursor, an application used to write code...

  # Paste behavior only (no LLM context change)
  - window_pattern: "^Terminal$"
    description: "Terminal application"
    paste_key: "ctrl+shift+v"
```

**Configuration options:**
- `extra_context`: Additional text added to the LLM cleanup system prompt
- `paste_key`: Custom paste keyboard shortcut (default: `ctrl+v`)
  - Terminals and some IDEs use `ctrl+shift+v` because `Ctrl+C/V` are reserved for terminal control sequences

You can specify `extra_context`, `paste_key`, both, or neither in each rule.

### Use Cases

- **IDE-specific**: Special handling for code in different editors + custom paste shortcuts
- **Terminals**: Use `ctrl+shift+v` for paste without changing LLM context
- **Email clients**: Format for email communication
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
  - `whisper_dictation.py`: Main dictation engine (start/stop/toggle/transcribe/cleanup)
  - `toggle-whisper-dictation.sh`: Toggle recording on/off with single key (recommended)
  - `start-whisper-dictation.sh`: Starts recording (two-key workflow)
  - `stop-whisper-dictation.sh`: Stops recording, transcribes and pastes (two-key workflow)

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