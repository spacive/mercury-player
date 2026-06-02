# mercury-player - A lightweight music player

Mercury is a lightweight, yet functional music player that runs entirely within the terminal and hopefully doesn't take itself too seriously.
This is a personal project, so don't expect everything to run perfectly.

Built entirely in python, it is made to be light on both CPU and memory usage.

To do:
- add support for .opus files
- replace curses UI with Textual
- Windows support
- maybe remake the whole backend in vlc to improve support for windows
- AppImage file


## How to run:

simply run run.py


### Prerequisites

Mercury uses Gstreamer via PyGObject (gi) for audio playback.
These have to be installed through your system, not through pip.

### Linux

#### Debian / Ubuntu

sudo apt install python3-gi gir1.2-gstreamer-1.0 gstreamer1.0-plugins-base gstreamer1.0-plugins-good


#### Fedora (Untested)

sudo dnf install python3-gobject gstreamer1 gstreamer1-plugins-base gstreamer1-plugins-good

(Optional, but recommended):

sudo dnf install gstreamer1-plugins-bad-free gstreamer1-plugins-ugly-free


#### Arch (Untested)

sudo pacman -S python-gobject gstreamer gst-plugins-base gst-plugins-good


### MacOS (Homebrew) (Untested)

**MacOS is not officially supported, and most likely never will be. This is because I don't own a Mac.**
**However, the packages are available on Homebrew, so if you have an Apple device, try seeing if it works, because I have no idea.**

brew install pygobject3 gstreamer gst-plugins-base gst-plugins-good

**Make sure you are using Python on Homebrew**

### Windows (Unsupported)
**Windows is not supported for now.**
Porting Mercury from Unix systems to Windows requires a whole rewrite of the UI, such as in Textual. While Textual is a very good UI for the terminal and in Python, and works cross-platform, I have not learnt it yet, so the UI will use curses until that happens.
Windows support will come with the future Textual UI overhaul.
Sorry, 66.4% of the worldwide desktop operating system market share.

