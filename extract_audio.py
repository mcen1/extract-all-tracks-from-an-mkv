import subprocess
import json
import os
import sys

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
    # Drag & drop passes file path as argument
    if len(sys.argv) > 1:
        for f in sys.argv[1:]:
            extract(f)
    else:
        print("Drag and drop MKV file(s) onto this EXE.")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
