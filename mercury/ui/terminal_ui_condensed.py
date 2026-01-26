import curses
import time
import random
from mercury.player.audio_engine import AudioEngine

def run_terminal_ui_condensed(engine: AudioEngine, tracks: list[str]):
    if not tracks:
        raise RuntimeError("No tracks provided")
    
    end_handled = False
    current_index = 0
    playing_index = 0

    loop_all = False
    loop_one = False
    shuffle = False
    shuffle_order = list(range(len(tracks)))

    engine.load(tracks[playing_index])
    engine.play()
    end_handled = False

    # Helpers
    def seek_relative(seconds: float):
        pos = engine.get_position()
        dur = engine.get_duration()
        new_pos = max(0, min(pos + seconds, dur - 0.1))
        engine.seek(new_pos)
        if engine.state.value == "PLAYING":
            engine.play()

    def get_next_track():
        if loop_one:
            return tracks[playing_index].split("/")[-1]
        elif shuffle:
            idx = shuffle_order.index(playing_index)
            if idx + 1 < len(shuffle_order):
                return tracks[shuffle_order[idx + 1]].split("/")[-1]
            elif loop_all:
                return tracks[shuffle_order[0]].split("/")[-1]
            else:
                return None
        else:
            if playing_index + 1 < len(tracks):
                return tracks[playing_index + 1].split("/")[-1]
            elif loop_all:
                return tracks[0].split("/")[-1]
            else:
                return None

    def format_time(seconds: float) -> str:
        seconds = max(0, int(seconds))
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02}:{secs:02}"

    def advance_track():
        nonlocal playing_index, current_index, shuffle_order, end_handled

        if loop_one:
            engine.stop()
            engine.load(tracks[playing_index])
            engine.play()
            end_handled = False
            return

        if shuffle:
            idx = shuffle_order.index(playing_index)
            if idx + 1 < len(shuffle_order):
                playing_index = shuffle_order[idx + 1]
            elif loop_all:
                playing_index = shuffle_order[0]
            else:
                return
        else:
            if playing_index + 1 < len(tracks):
                playing_index += 1
            elif loop_all:
                playing_index = 0
            else:
                return

        engine.stop()
        engine.load(tracks[playing_index])
        engine.play()
        end_handled = False
        current_index = playing_index

    def previous_track():
        nonlocal playing_index, current_index, end_handled

        if shuffle:
            idx = shuffle_order.index(playing_index)
            if idx > 0:
                playing_index = shuffle_order[idx - 1]
            elif loop_all:
                playing_index = shuffle_order[-1]
            else:
                return
        else:
            if playing_index > 0:
                playing_index -= 1
            elif loop_all:
                playing_index = len(tracks) - 1
            else:
                return

        engine.stop()
        engine.load(tracks[playing_index])
        engine.play()
        end_handled = False
        current_index = playing_index

    engine.on_track_end = advance_track

    # Curses UI
    def main(stdscr):
        nonlocal current_index, playing_index, shuffle_order, loop_all, loop_one, shuffle, end_handled

        curses.curs_set(0)
        stdscr.nodelay(True)
        stdscr.timeout(100)

        MIN_HEIGHT = 4
        MIN_WIDTH = 40

        while True:
            height, width = stdscr.getmaxyx()

            if height < MIN_HEIGHT or width < MIN_WIDTH:
                stdscr.clear()
                try:
                    stdscr.addstr(0, 0, "too small window i'm dying here")
                except curses.error:
                    pass
                stdscr.refresh()
                time.sleep(0.1)
                continue

            pos = engine.get_position()
            dur = engine.get_duration()
            if dur > 0 and pos >= dur - 0.15 and not end_handled:
                end_handled = True
                advance_track()
            vol = engine.player.get_property("volume")

            bar_len = max(10, width - 45)
            filled = int(bar_len * pos / dur) if dur > 0 else 0
            bar = "[" + "=" * filled + "-" * (bar_len - filled) + "]"

            now_playing = tracks[playing_index].split("/")[-1]
            next_track_name = get_next_track()
            next_line = f"Next Up: {next_track_name}" if next_track_name else "Next Up: [None]"
            stdscr.erase()
            try:
                stdscr.addstr(0, 0,
                    f"Now Playing: {now_playing} "
                    f"[L:{int(loop_all)} O:{int(loop_one)} S:{int(shuffle)}]"
                )
            except curses.error:
                pass

            try:
                stdscr.addstr(2, 0, next_line)
            except curses.error:
                pass

            try:
                stdscr.addstr(1, 0,
                    f"{bar} {format_time(pos)}/{format_time(dur)}  Vol:{round(vol*100)}%"
                )
            except curses.error:
                pass

            try:
                stdscr.addstr(3, 0,
                    "[↑↓/j/k] Move [N] Next  [B] Prev  [P] Play/Pause"  
                    "[L] LoopAll   [O] LoopOne [S] Shuffle  [Q] Quit"
                )
            except curses.error:
                pass

            try:
                stdscr.addstr(4, 0,
                "[+/-] Volume +/-10%  [F/R] Forward/Reverse +/-10s [←/→] Forward/Reverse +/-5s")
            except curses.error:
                pass

            stdscr.refresh()

            try:
                key = stdscr.getch()
            except curses.error:
                key = -1

            # Key handling
            
            if key in (ord("q"),):
                break
            elif key in (ord("p"), ord(" ")):
                engine.toggle_play_pause()
            elif key == ord("n"):
                advance_track()
            elif key == ord("b"):
                previous_track()
            elif key == ord("l"):
                loop_all = not loop_all
            elif key == ord("o"):
                loop_one = not loop_one
            elif key == ord("h"):
                shuffle = not shuffle
                if shuffle:
                    shuffle_order = list(range(len(tracks)))
                    random.shuffle(shuffle_order)
            elif key == curses.KEY_RIGHT:
                seek_relative(5)
            elif key == curses.KEY_LEFT:
                seek_relative(-5)
            elif key == ord("f"):
                seek_relative(10)
            elif key == ord("r"):
                seek_relative(-10)
            elif key in (ord("+"), ord("=")):
                vol = engine.player.get_property("volume")
                engine.set_volume(min(vol + 0.1, 1.0))
            elif key == ord("-"):
                vol = engine.player.get_property("volume")
                engine.set_volume(max(vol - 0.1, 0.0))

            time.sleep(0.05)

        engine.stop()

    curses.wrapper(main)
