import json
import yt_dlp
import tkinter as tk

#class for the main window
class ytdlpGUI:
    def __init__(self, w: int, h:int):
        self.window = tk.Tk()
        self.window.title("ytdlp gui")
        self.window.resizable(False,False)

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

        bottom = tk.Frame(master=sizeFrame, width=w, height=h)
        bottom.pack(side=tk.BOTTOM)

    def loadVid(self, event):
        ydl_opts = {
            'listformats': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url=self.linkIn.get(), download=False)

            #print(json.dumps(ydl.sanitize_info(info)))
        

    def enterMain(self):
        self.findVid.bind("<Button-1>", self.loadVid)

        self.window.mainloop()

if __name__ == "__main__":
    gui = ytdlpGUI(800, 600)
    gui.enterMain()