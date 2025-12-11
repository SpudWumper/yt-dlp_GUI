from yt_dlp import YoutubeDL
import tkinter as tk

#class for the main window
class ytdlpGUI:
    def __init__(self, w: int, h:int):
        self.window = tk.Tk()
        self.window.title("ytdlp gui")
        self.window.resizable(False,False)