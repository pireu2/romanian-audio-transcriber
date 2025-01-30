import os
import sys
import tkinter as tk
from transcriber import WhisperTranscriber


def get_base_path():
    if getattr(sys, "frozen", False):
        return sys._MEIPASS
    else:
        return os.path.dirname(os.path.abspath(__file__))


if __name__ == "__main__":
    root = tk.Tk()
    app = WhisperTranscriber(root, get_base_path())
    root.mainloop()
