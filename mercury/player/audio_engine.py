import gi
gi.require_version("Gst", "1.0")
from gi.repository import Gst, GLib
from enum import Enum


class PlaybackState(Enum):
    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"


class AudioEngine:
    def __init__(self):
        Gst.init(None)

        self.player = Gst.ElementFactory.make("playbin", "player")
        if not self.player:
            raise RuntimeError("Failed to create GStreamer playbin")

        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self._on_message)

        self.state = PlaybackState.STOPPED
        self.on_track_finished = None

        
        self._position_callback = None
        self._position_source_id = None

    

    def load(self, filepath: str):
        uri = Gst.filename_to_uri(filepath)
        self.player.set_property("uri", uri)
        self.state = PlaybackState.STOPPED

    def play(self):
        self.player.set_state(Gst.State.PLAYING)
        self.state = PlaybackState.PLAYING

    def pause(self):
        self.player.set_state(Gst.State.PAUSED)
        self.state = PlaybackState.PAUSED

    def resume(self):
        if self.state == PlaybackState.PAUSED:
            self.play()

    def stop(self):
        self.player.set_state(Gst.State.NULL)
        self.state = PlaybackState.STOPPED

    def toggle_play_pause(self):
        if self.state == PlaybackState.PLAYING:
            self.pause()
        else:
            self.play()

    
    def set_volume(self, volume: float):
        volume = max(0.0, min(volume, 1.0))
        self.player.set_property("volume", volume)

    
    def get_position(self) -> float:
        success, position = self.player.query_position(Gst.Format.TIME)
        if not success:
            return 0.0
        return position / Gst.SECOND

    def get_duration(self) -> float:
        success, duration = self.player.query_duration(Gst.Format.TIME)
        if not success or duration <= 0:
            return 0.0
        return duration / Gst.SECOND

    def seek(self, seconds: float):
        if seconds < 0:
            seconds = 0

        self.player.seek_simple(
            Gst.Format.TIME,
            Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT,
            int(seconds * Gst.SECOND),
        )

    
    def is_playing(self) -> bool:
        return self.state == PlaybackState.PLAYING

    def is_paused(self) -> bool:
        return self.state == PlaybackState.PAUSED

    def is_stopped(self) -> bool:
        return self.state == PlaybackState.STOPPED

    
    def start_position_polling(self, callback, interval_ms=100):
        self._position_callback = callback

        if self._position_source_id:
            GLib.source_remove(self._position_source_id)

        def _poll():
            if self.state in (PlaybackState.PLAYING, PlaybackState.PAUSED):
                pos = self.get_position()
                self._position_callback(pos)
            return True 

        self._position_source_id = GLib.timeout_add(interval_ms, _poll)

    def stop_position_polling(self):
        if self._position_source_id:
            GLib.source_remove(self._position_source_id)
            self._position_source_id = None
        self._position_callback = None

    
    def _on_message(self, bus, message):
        msg_type = message.type

        if msg_type == Gst.MessageType.EOS:
            self.player.set_state(Gst.State.NULL)
            self.state = PlaybackState.STOPPED
            if self.on_track_finished:
                self.on_track_finished()

        elif msg_type == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            print("GStreamer Error:", err)
            if debug:
                print("Debug info:", debug)





class GaplessAudioEngine(AudioEngine):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.queue = []
            self.current_index = 0
            self.on_track_end = None  

        def load_playlist(self, tracks: list[str]):
            self.queue = tracks
            self.current_index = 0
            if tracks:
                self.load(tracks[0])

        def play_next(self):
            
            self.current_index += 1
            if self.current_index >= len(self.queue):
                return  
            self.load(self.queue[self.current_index])
            self.play()
            if self.on_track_end:
                self.on_track_end()
