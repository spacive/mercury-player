import curses
import time
import random
from mercury.player.audio_engine import AudioEngine


def run_terminal_ui(engine: AudioEngine, tracks: list[str]):
    if not tracks:
        raise RuntimeError("No tracks provided")
    end_handled = False

    current_index = 0
    playing_index = 0
    scroll_offset = 0
    list_height = 1  

    loop_all = False
    loop_one = False
    shuffle = False
    shuffle_order = list(range(len(tracks)))

    # Initial playback
    engine.load(tracks[playing_index])
    engine.play()
    end_handled = False
    # Helpers
    def clamp_indices():
        nonlocal current_index, playing_index
        current_index = max(0, min(current_index, len(tracks) - 1))
        playing_index = max(0, min(playing_index, len(tracks) - 1))

    def adjust_scroll():
        nonlocal scroll_offset, list_height
        clamp_indices()

        max_scroll = max(0, len(tracks) - list_height)
        scroll_offset = max(0, min(scroll_offset, max_scroll))

        if current_index < scroll_offset:
            scroll_offset = current_index
        elif current_index >= scroll_offset + list_height:
            scroll_offset = current_index - list_height + 1
    
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
        
        seconds = max(0, int(seconds))  # ensure non-negative integer
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

        clamp_indices()
        engine.stop()
        engine.load(tracks[playing_index])
        engine.play()
        end_handled = False

        current_index = playing_index
        adjust_scroll()

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

        clamp_indices()
        engine.stop()
        engine.load(tracks[playing_index])
        engine.play()
        end_handled = False

        current_index = playing_index
        adjust_scroll()

    engine.on_track_end = advance_track

    # Curses UI
    def main(stdscr):
        nonlocal current_index, playing_index, scroll_offset
        nonlocal loop_all, loop_one, shuffle, shuffle_order
        nonlocal list_height
        nonlocal end_handled

        curses.curs_set(0)
        stdscr.nodelay(True)
        stdscr.timeout(100)

        while True:
            height, width = stdscr.getmaxyx()
            list_height = max(1, height - 7)

            adjust_scroll()

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
            stdscr.addstr(
                0, 0,
                f"Now Playing: {now_playing} "
                f"[L:{int(loop_all)} O:{int(loop_one)} S:{int(shuffle)}]"
            )
            stdscr.addstr(2, 0, next_line)

            stdscr.addstr(1, 0,f"{bar} {format_time(pos)}/{format_time(dur)}  Vol:{round(vol*100)}%")

            stdscr.addstr(3, 0, "Tracks:")

            for i in range(list_height):
                idx = scroll_offset + i
                y = 5 + i 
                stdscr.move(y, 0)
                stdscr.clrtoeol()  

                if idx >= len(tracks):
                    continue

                name = tracks[idx].split("/")[-1]
                if idx == current_index:
                    stdscr.addstr(y, 2, f"> {name}", curses.A_REVERSE)
                elif idx == playing_index:
                    stdscr.addstr(y, 2, f"* {name}")
                else:
                    stdscr.addstr(y, 2, f"  {name}")

            stdscr.addstr(height - 2, 0, "[↑↓/j/k] Move  [Enter] Play Selected  [n] Next  b Prev  [P] Play/Pause"  
                "[L] LoopAll  [O] LoopOne [S] Shuffle  [Q] Quit")
            stdscr.addstr(height - 1, 0,
                "[+/-] Volume +/-10%  [F/R] Forward/Reverse +/-10s [←/→] Forward/Reverse +/-5s")

            stdscr.refresh()

            try:
                key = stdscr.getch()
            except curses.error:
                key = -1

            if key in (ord("q"),):
                break
            elif key in (ord("p"), ord(" ")):
                engine.toggle_play_pause()
            elif key in (curses.KEY_DOWN, ord("j")):
                current_index += 1
                adjust_scroll()
            elif key in (curses.KEY_UP, ord("k")):
                current_index -= 1
                adjust_scroll()
            elif key in (10, 13):
                playing_index = current_index
                engine.stop()
                engine.load(tracks[playing_index])
                engine.play()
                end_handled = False
            elif key == ord("n"):
                advance_track()
            elif key == ord("b"):
                previous_track()
            elif key == ord("l"):
                loop_all = not loop_all
            elif key == ord("o"):
                loop_one = not loop_one
            elif key == ord("s"):
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

            elif key in (ord("+"), ord("=")):  # Volume up
                vol = engine.player.get_property("volume")
                engine.set_volume(min(vol + 0.1, 1.0))

            elif key == ord("-"):  # Volume down
                vol = engine.player.get_property("volume")
                engine.set_volume(max(vol - 0.1, 0.0))


            time.sleep(0.05)

        engine.stop()

    curses.wrapper(main)
