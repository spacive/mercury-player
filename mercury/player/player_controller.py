from mercury.player.audio_engine import AudioEngine

class PlayerController:
    def __init__(self, playlist):
        self.audio = AudioEngine()
        self.playlist = playlist
        self.audio.on_track_finished = self._on_track_finished

    def play_current(self):
        track = self.playlist.get_current_track()
        if track:
            self.audio.stop()                 # stop current track first
            self.audio.load(track.filepath)   # load new track
            self.audio.play()                 # start playback

    def next_track(self):
        self.playlist.next_track()  # update index
        self.play_current()          # immediately play

    def prev_track(self):
        self.playlist.prev_track()  # update index
        self.play_current()          # immediately play

    def _on_track_finished(self):
        next_track = self.playlist.next_track()
        if next_track:
            self.play_current()
