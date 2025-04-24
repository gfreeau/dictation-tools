#!/usr/bin/env python3
"""whisper_dictation.py

Standalone start/stop driver for OpenAI Whisper-based dictation.

Usage:
    python3 whisper_dictation.py start   # start recording microphone
    python3 whisper_dictation.py stop    # stop, transcribe & paste text

Design goals:
    • No dependency on existing nerd-dictation or cleanup-dictation scripts
    • CPU-only friendly (records to a temporary WAV then sends to OpenAI)
    • Optional GPT-3.5 cleanup with context-aware prompt if Cursor is detected

Environment / config:
    WHISPER_TEMP_DIR   – directory for temporary recordings (default: /tmp/whisper_records)
    WHISPER_CLEANUP    – "true" to enable GPT cleanup (default: true)
    OPENAI_API_KEY     – your OpenAI key (same as cleanup-dictation.py)

System dependencies: ffmpeg, xclip, xdotool, notify-send
Python dependencies: openai, python-dotenv
"""
from __future__ import annotations

import os
import sys
import subprocess
import datetime
import time
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
import re

try:
    from openai import OpenAI
except ImportError:  # graceful message
    OpenAI = None  # type: ignore

PID_FILE = Path.home() / ".whisper_recorder_pid"
TMP_DIR = Path(os.getenv("WHISPER_TEMP_DIR", "/tmp/whisper_records"))
CLEANUP_ENABLED = os.getenv("WHISPER_CLEANUP", "true").lower() in {"1", "true", "yes"}

REQUIRED_CMDS = ["ffmpeg", "xclip", "xdotool", "notify-send"]

SYSTEM_PROMPT_CLEANUP = (
    "You are a helpful assistant that cleans up dictated text. Only fix "
    "grammar, spelling, and punctuation errors and create paragraphs for "
    "readability. MAKE NO OTHER CHANGES TO THE INPUT TEXT. Do not add any "
    "extra text, commentary, or introductory phrases. Use Australian "
    "English spelling. FOLLOW THESE INSTRUCTIONS EXACTLY."
)

# Extra context when coding app detected
CODING_EXTRA_CONTEXT = (
    "We are in Cursor, an application used to write code. The user is "
    "likely talking about programming or technology. Correct technical "
    "terms and proper nouns such as 'Supabase', 'PostgreSQL', etc., to their "
    "appropriate spellings."
)


def check_dependencies() -> bool:
    missing = []
    for cmd in REQUIRED_CMDS:
        if subprocess.call(["which", cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) != 0:
            missing.append(cmd)
    if missing:
        print(f"Missing required system commands: {', '.join(missing)}", file=sys.stderr)
        return False
    if OpenAI is None:
        print("Missing python package 'openai'. Please install it.", file=sys.stderr)
        return False
    return True


def notify(title: str, message: str, timeout_ms: int = 3000) -> None:
    try:
        subprocess.run(["notify-send", "-t", str(timeout_ms), title, message], check=False)
    except Exception:
        pass  # ignore failures silently


def active_window_is_cursor() -> bool:
    """Detect if the active window belongs to the Cursor IDE by inspecting its title."""
    try:
        win_id = subprocess.check_output(["xdotool", "getactivewindow"], text=True).strip()
        window_name = subprocess.check_output(["xdotool", "getwindowname", win_id], text=True).strip()
        # Simple heuristics similar to context-detector.py
        if re.search(r"Cursor$", window_name):
            return True
        if " - Cursor" in window_name:
            return True
    except Exception:
        pass
    return False


def record_start() -> None:
    if PID_FILE.exists():
        print("Recording seems to be already running (PID file exists).", file=sys.stderr)
        return

    TMP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    wav_path = TMP_DIR / f"dictation_{timestamp}.wav"

    # Use ffmpeg for recording – mono, 16 kHz, wav
    cmd = [
        "ffmpeg",
        "-f", "alsa",
        "-i", "default",
        "-ac", "1",
        "-ar", "16000",
        "-v", "quiet",
        "-y",
        str(wav_path),
    ]

    proc = subprocess.Popen(cmd)
    PID_FILE.write_text(str(proc.pid))

    notify("Whisper Dictation", "Recording started…")
    print(f"Recording to {wav_path} (PID {proc.pid})")


def kill_recorder() -> Optional[Path]:
    if not PID_FILE.exists():
        print("No active recorder PID file found.", file=sys.stderr)
        return None

    try:
        pid = int(PID_FILE.read_text().strip())
    except ValueError:
        PID_FILE.unlink(missing_ok=True)
        print("Invalid PID file.", file=sys.stderr)
        return None

    try:
        os.kill(pid, 2)  # SIGINT for ffmpeg to gracefully stop
    except ProcessLookupError:
        print(f"Recorder process {pid} not found.", file=sys.stderr)
    finally:
        PID_FILE.unlink(missing_ok=True)

    # Wait briefly to ensure file flush
    time.sleep(1)

    # Find latest wav in TMP_DIR
    wav_files = sorted(TMP_DIR.glob("dictation_*.wav"), key=os.path.getmtime)
    return wav_files[-1] if wav_files else None


def transcribe_audio(wav_path: Path) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        notify("Whisper Dictation", "OPENAI_API_KEY not set", 5000)
        sys.exit(1)

    client = OpenAI(api_key=api_key)

    with wav_path.open("rb") as audio_file:
        print("Calling Whisper API…")
        resp = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="text",
        )
    text = resp.strip()
    print("Whisper result:", text)
    return text


def cleanup_text(raw_text: str) -> str:
    if not CLEANUP_ENABLED:
        return raw_text

    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)

    system_prompt = SYSTEM_PROMPT_CLEANUP
    if active_window_is_cursor():
        print("Cursor detected, adding extra context")
        system_prompt += "\n" + CODING_EXTRA_CONTEXT

    resp = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": raw_text},
        ],
        temperature=0,
    )
    cleaned = resp.choices[0].message.content.strip()
    print("Cleaned text:", cleaned)
    return cleaned


def copy_and_paste(text: str) -> None:
    subprocess.run(["xclip", "-selection", "clipboard"], input=text.encode(), check=False)
    subprocess.run(["xdotool", "key", "ctrl+v"], check=False)


def record_stop() -> None:
    wav_path = kill_recorder()
    if wav_path is None:
        return

    notify("Whisper Dictation", "Transcribing…", 2000)

    try:
        raw_text = transcribe_audio(wav_path)
        final_text = cleanup_text(raw_text)
        copy_and_paste(final_text)
        notify("Whisper Dictation", "Finished!", 3000)
    except Exception as exc:
        notify("Whisper Dictation", f"Error: {exc}", 5000)
        raise
    finally:
        # Optionally delete wav to save space
        try:
            wav_path.unlink()
        except Exception:
            pass


def main() -> None:
    load_dotenv()

    if len(sys.argv) != 2 or sys.argv[1] not in {"start", "stop"}:
        print("Usage: whisper_dictation.py start|stop")
        sys.exit(1)

    if not check_dependencies():
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "start":
        record_start()
    else:
        record_stop()


if __name__ == "__main__":
    main() 