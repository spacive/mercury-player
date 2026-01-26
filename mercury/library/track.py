from mutagen import File
import os

class Track:
    def __init__(self, filepath):
        self.filepath = filepath
        self.title = os.path.basename(filepath)
        self.duration = 0
        self.load_metadata()

    def load_metadata(self):
        try:
            audio = File(self.filepath)
            if audio:
                self.duration = int(audio.info.length)
                if "title" in audio.tags:
                    self.title = audio.tags["title"][0]
        except Exception:
            pass

