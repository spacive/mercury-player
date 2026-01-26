import os
import random
from mercury.library.track import Track

class Playlist:
    def __init__(self):
        self.tracks = []
        self.current_index = 0
        self.shuffle = False
        self.repeat_one = False

    def load_folder(self, folder_path):
        """Scan folder for audio files and create tracks."""
        supported_exts = (".mp3", ".flac", ".ogg", ".wav", ".m4a", ".opus")
        self.tracks = [
            Track(os.path.join(folder_path, f))
            for f in os.listdir(folder_path)
            if f.lower().endswith(supported_exts)
        ]
        self.current_index = 0

    def get_current_track(self):
        if not self.tracks:
            return None
        return self.tracks[self.current_index]

    def next_track(self):
        if not self.tracks:
            return None

        if self.repeat_one:
            return self.get_current_track()

        if self.shuffle:
            self.current_index = random.randint(0, len(self.tracks) - 1)
        else:
            self.current_index += 1
            if self.current_index >= len(self.tracks):
                self.current_index = 0  # loop to start

        return self.get_current_track()

    def prev_track(self):
        if not self.tracks:
            return None

        if self.repeat_one:
            return self.get_current_track()

        if self.shuffle:
            self.current_index = random.randint(0, len(self.tracks) - 1)
        else:
            self.current_index -= 1
            if self.current_index < 0:
                self.current_index = len(self.tracks) - 1  # loop to end

        return self.get_current_track()

    def toggle_repeat_one(self):
        self.repeat_one = not self.repeat_one

    def toggle_shuffle(self):
        self.shuffle = not self.shuffle

