import json
import yt_dlp
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
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
            relief="raised",
            state=tk.DISABLED
        )
        self.downVid.pack(pady=10)

        
    # takes input URL and loads corresponding video and information
    # - first clear the frames if we have already loaded a video
    # - extracts the info of video
    # - grabs thumbnail URL and converts to tkinter displayable image
    # - display title above thumbnail
    # - grab and display downloadable formats
    # - input for file name and download location
    # - checkbox for embed thumbnail option
    def loadVid(self, event):
        for widget in self.vidInfoFrame.winfo_children():
            widget.destroy()
        for widget in self.formatOptFrame.winfo_children():
            widget.destroy()

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

        filenameLabel = tk.Label(master=self.formatOptFrame, text="Enter filename here")
        filenameLabel.pack()
        self.filenameIn = tk.Entry(master=self.formatOptFrame, width=49)
        self.filenameIn.pack(pady=5)
        self.fileLocation = tk.Label(master=self.formatOptFrame, text="Download location: ", wraplength=396)
        self.fileLocation.pack()
        self.browse = tk.Button(
            master=self.formatOptFrame,
            text="Choose download location",
            width=25,
            height=2,
            relief="raised"
        )
        self.browse.pack(pady=10)
        self.browse.bind("<Button-1>", self.browseDir)

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
        
        self.audioCB = ttk.Combobox(master=self.formatOptFrame, values=audio, width=49)
        self.audioCB.set('Choose an audio format')
        self.audioCB.pack(pady=10)
        self.videoCB = ttk.Combobox(master=self.formatOptFrame, values=video, width=49)
        self.videoCB.set('Choose a video format')
        self.videoCB.pack(pady=10)

        self.thumbnailYN = tk.IntVar()
        self.embedThumbnail = tk.Checkbutton(master=self.formatOptFrame, text="Embed thumbnail", variable=self.thumbnailYN, onvalue=1, offvalue=0)
        self.embedThumbnail.pack()

        self.downVid.config(state=tk.NORMAL)

    # function to handle file browsing, just a wrapper?
    def browseDir(self, event):
        dir = filedialog.askdirectory()
        self.fileLocation.config(text=dir)

    # downloads the video with selected options
    def downloadVideo(self, event):
        audioFormat = self.audioCB.get()
        videoFormat = self.videoCB.get()
        if audioFormat == 'Choose an audio format' or videoFormat == 'Choose a video format':
            messagebox.showerror("Missing format selection", "Make sure to choose and audio and video format")
        else:
            audioCode = audioFormat.split()[0]
            videoCode = videoFormat.split()[0]

            if self.thumbnailYN.get() == 1:
                ydl_opts = {
                    'outtmpl': self.fileLocation.cget('text') + "\\" + self.filenameIn.get(),
                    'format': audioCode+"+"+videoCode,
                    'writethumbnail': True,
                    'postprocessors': [
                        {'key': 'FFmpegMetadata', 'add_metadata': True,},
                        {'key': 'EmbedThumbnail'}
                        ]
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    error_code = ydl.download(self.linkIn.get())
                print("Video failed to download" if error_code
                      else "Downloaded successfully")
            else:
                ydl_opts = {
                    'outtmpl': self.fileLocation.cget('text') + "\\" + self.filenameIn.get(),
                    'format': audioCode+"+"+videoCode
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    error_code = ydl.download(self.linkIn.get())
                print("Video failed to download" if error_code
                      else "Downloaded successfully")

    # start up the gui
    def enterMain(self):
        self.findVid.bind("<Button-1>", self.loadVid)
        self.downVid.bind("<Button-1>", self.downloadVideo)

        self.window.mainloop()

if __name__ == "__main__":
    gui = ytdlpGUI(800, 600)
    gui.enterMain()
    