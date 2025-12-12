import json
import yt_dlp
import tkinter as tk
from tkinter import ttk
import urllib.request
from PIL import ImageTk, Image
import io

#class for the main window
class ytdlpGUI:
    def __init__(self, w: int, h:int):

        # root window
        self.window = tk.Tk()
        self.window.title("ytdlp gui")
        self.window.resizable(False,False)

        # top section of widgets
        sizeFrame = tk.Frame(width = w, height = h)
        sizeFrame.pack()
        top = tk.Frame(master=sizeFrame, width=w)
        top.pack(fill=tk.X)

        self.linkInLabel = tk.Label(master=top, text="Enter video URL here")
        self.linkInLabel.pack(pady=5)
        self.linkIn = tk.Entry(master=top,width=98)
        self.linkIn.pack()
        self.findVid = tk.Button(
            master=top,
            text="Load video",
            width=10,
            height=2,
            relief="raised"
        )
        self.findVid.pack(pady=10)

        # -------------------------------------------------------------

        # mid section of widgets
        mid = tk.Frame(master=sizeFrame, width=w, height=h)
        mid.pack()

        self.vidInfoFrame = tk.Frame(master=mid, width=w//2, height=h)
        self.vidInfoFrame.pack(side=tk.LEFT)

        self.formatOptFrame = tk.Frame(master=mid, width=w//2, height=h)
        self.formatOptFrame.pack(side=tk.RIGHT)

        # -------------------------------------------------------------

        # bottom section of widgets
        bottom = tk.Frame(master=sizeFrame, width=w)
        bottom.pack(side=tk.BOTTOM)

        self.downVid = tk.Button(
            master=bottom,
            text="Download video",
            width=16,
            height=2,
            relief="raised"
        )
        self.downVid.pack(pady=10)

        
    # takes input URL and loads corresponding video and information
    # - extracts info of video
    # - grabs thumbnail URL and converts to tkinter displayable image
    # - display title above thumbnail
    # - grab and display downloadable formats
    def loadVid(self, event):
        ydl_opts = {
            
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url=self.linkIn.get(), download=False)

            # l = open("log.txt", "w")
            # l.write(json.dumps(ydl.sanitize_info(info), indent=2))

            # print(json.dumps(ydl.sanitize_info(info), indent=2))

        imageURL = info.get('thumbnail')
        print(imageURL)
        with urllib.request.urlopen(imageURL) as u:
            raw_data = u.read()
        
        image = Image.open(io.BytesIO(raw_data))
        image.thumbnail([396,396])
        self.photo = ImageTk.PhotoImage(image)

        titleLabel = tk.Label(master=self.vidInfoFrame, text=info.get('title'), wraplength=396)
        titleLabel.config(font=("TkDefaultFont", 16))
        titleLabel.pack()

        imgLabel = tk.Label(master=self.vidInfoFrame, image=self.photo)
        imgLabel.pack()

        formats = info.get('formats')
        audio = []
        video = []
        for f in formats:
            if f.get('resolution') == 'audio only':
                audio.append(f.get('format') + ', ' + f.get('audio_ext'))
            elif f.get('format_note') == 'storyboard':
                pass
            else:
                video.append(f.get('format') + ', ' + f.get('video_ext'))
        audio.append('None')
        video.append('None')
        
        audioCB = ttk.Combobox(master=self.formatOptFrame, values=audio, width=49)
        audioCB.set('Choose an audio format')
        audioCB.pack(pady=10)
        videoCB = ttk.Combobox(master=self.formatOptFrame, values=video, width=49)
        videoCB.set('Choose an video format')
        videoCB.pack(pady=10)

        

    def enterMain(self):
        self.findVid.bind("<Button-1>", self.loadVid)

        self.window.mainloop()

if __name__ == "__main__":
    gui = ytdlpGUI(800, 600)
    gui.enterMain()
    