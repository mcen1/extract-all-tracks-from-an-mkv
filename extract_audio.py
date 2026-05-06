import subprocess
import json
import os
import sys
import tkinter as tk
from tkinter import filedialog


def get_base_path():
    # When bundled by PyInstaller, files are extracted to _MEIPASS
    if hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

BASE_PATH = get_base_path()
FFMPEG = os.path.join(BASE_PATH, "ffmpeg.exe")
FFPROBE = os.path.join(BASE_PATH, "ffprobe.exe")

def run(cmd):
    return subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode()

def get_audio_streams(input_file):
    cmd = [
        FFPROBE,
        "-v", "error",
        "-select_streams", "a",
        "-show_entries", "stream=index,codec_name:stream_tags=language",
        "-of", "json",
        input_file
    ]
    data = json.loads(run(cmd))
    return data.get("streams", [])

def codec_to_ext(codec):
    return {
        "aac": "m4a",
        "ac3": "ac3",
        "eac3": "eac3",
        "dts": "dts",
        "mp3": "mp3",
        "flac": "flac",
        "opus": "opus",
        "vorbis": "ogg"
    }.get(codec, "bin")

def extract(input_file):
    base = os.path.splitext(os.path.basename(input_file))[0]
    out_dir = os.path.dirname(input_file)

    streams = get_audio_streams(input_file)

    if not streams:
        print("No audio streams found.")
        return

    for s in streams:
        idx = s["index"]
        codec = s.get("codec_name", "unknown")
        lang = s.get("tags", {}).get("language", "und")

        ext = codec_to_ext(codec)
        output = os.path.join(out_dir, f"{base}_track{idx}_{lang}.{ext}")

        print(f"Extracting stream {idx} ({codec}, {lang}) -> {output}")

        subprocess.run([
            FFMPEG,
            "-y",
            "-i", input_file,
            "-map", f"0:{idx}",
            "-c", "copy",
            output
        ])


def main():
    try:
        files = []

        # Case 1: drag & drop worked
        if len(sys.argv) > 1:
            files = [f.strip('"') for f in sys.argv[1:]]

        # Case 2: fallback to file picker
        if not files:
            print("No files passed via drag-and-drop.")
            print("Opening file picker...")

            root = tk.Tk()
            root.withdraw()

            selected = filedialog.askopenfilenames(
                title="Select MKV file(s)",
                filetypes=[("MKV files", "*.mkv"), ("All files", "*.*")]
            )

            files = list(selected)

        if not files:
            print("No files selected.")
            return

        for f in files:
            if not os.path.exists(f):
                print(f"File not found: {f}")
                continue

            print(f"\nProcessing: {f}")
            extract(f)

    except Exception as e:
        print(f"\nERROR: {e}")

    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
