import sys
import os
from glob import glob
from mercury.player.audio_engine import AudioEngine
from mercury.ui.terminal_ui import run_terminal_ui as run_terminal_ui_full
from mercury.ui.terminal_ui_condensed import run_terminal_ui_condensed

AUDIO_EXTENSIONS = [".mp3", ".flac", ".wav", ".ogg", ".m4a"]

def collect_tracks(args, recursive=True):
    tracks = []

    for path in args:
        if os.path.isdir(path):
            if recursive:
                for root, dirs, files in os.walk(path):
                    for f in files:
                        if os.path.splitext(f)[1].lower() in AUDIO_EXTENSIONS:
                            tracks.append(os.path.join(root, f))
            else:
                for f in os.listdir(path):
                    full = os.path.join(path, f)
                    if os.path.isfile(full) and os.path.splitext(f)[1].lower() in AUDIO_EXTENSIONS:
                        tracks.append(full)
        elif os.path.isfile(path):
            if os.path.splitext(path)[1].lower() in AUDIO_EXTENSIONS:
                tracks.append(path)
        else:
            print(f"Warning: {path} is not a valid file or directory")

    return tracks


def main():
    if len(sys.argv) < 2:
        print("Usage: python run.py [--condensed] <track1|folder1> <track2|folder2> ...")
        sys.exit(1)

    # Determine if condensed mode is enabled
    condensed = "--condensed" in sys.argv or "-c" in sys.argv

    # Filter out the --condensed flag from track args
    track_args = [arg for arg in sys.argv[1:] if arg not in ("--condensed", "-c")]
    tracks = collect_tracks(track_args)

    if not tracks:
        print("No valid audio tracks found.")
        sys.exit(1)

    engine = AudioEngine()

    if condensed:
        run_terminal_ui_condensed(engine, tracks)
    else:
        run_terminal_ui_full(engine, tracks)


if __name__ == "__main__":
    main()
