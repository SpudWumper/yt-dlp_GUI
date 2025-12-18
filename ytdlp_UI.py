import json
import os
import yt_dlp
from yt_dlp.utils import DownloadCancelled, download_range_func
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import urllib.request
from PIL import ImageTk, Image
import io
import re
import sys

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
        mid = tk.Frame(master=sizeFrame)#, width=w, height=h)
        mid.pack()

        self.vidInfoFrame = tk.Frame(master=mid)#, width=w//2, height=h)
        self.vidInfoFrame.pack(side=tk.LEFT)

        self.progFrame = tk.Frame(master=mid)
        self.progFrame.pack(side=tk.RIGHT)
        self.progressLogs = tk.Text(master=self.progFrame, wrap='word', width=49)
        #self.progressLogs.pack(side=tk.RIGHT)

        self.formatOptFrame = tk.Frame(master=mid)#, width=w//2, height=h)
        self.formatOptFrame.pack(side=tk.RIGHT)

        sys.stdout = TextRedirector(self.progressLogs)
        sys.stderr = TextRedirector(self.progressLogs)

        # -------------------------------------------------------------

        # bottom section of widgets
        self.bottom = tk.Frame(master=sizeFrame, width=w)
        self.bottom.pack(side=tk.BOTTOM)

        self.downVid = tk.Button(
            master=self.bottom,
            text="Download video",
            width=16,
            height=2,
            relief="raised"
        )
        # self.downVid.pack(pady=10)

    # function to handle file browsing, just a wrapper?
    def browseDir(self, event):
        dir = filedialog.askdirectory()
        self.fileLocation.config(text=dir)

    # takes input URL and loads corresponding video and information
    # - first clear the frames if we have already loaded a video
    # - extracts the info of video
    # - grabs thumbnail URL and converts to tkinter displayable image
    # - display title above thumbnail
    # - grab and display downloadable formats
    # - input for file name and download location
    # - checkbox for embed thumbnail option
    # - timestamp input to download section of video
    # - display log messages to show progress
    def loadVid(self, event):
        if not self.linkIn.get():
            messagebox.showerror("No URL entered", "Make sure to choose a valid URL")
        else:
            try:
                ydl_opts = {
                    
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url=self.linkIn.get(), download=False)

                    # l = open("log.txt", "w")
                    # l.write(json.dumps(ydl.sanitize_info(info), indent=2))

                    # print(json.dumps(ydl.sanitize_info(info), indent=2))
            except Exception:
                messagebox.showerror("Invalid URL", "Make sure to choose a valid URL")
                return -1

            for widget in self.vidInfoFrame.winfo_children():
                widget.destroy()
            for widget in self.formatOptFrame.winfo_children():
                widget.destroy()

            self.vidTitle = info.get('title')

            self.vidDuration = info.get('duration')
            
            imageURL = info.get('thumbnail')
            with urllib.request.urlopen(imageURL) as u:
                raw_data = u.read()
            
            image = Image.open(io.BytesIO(raw_data))
            image.thumbnail([396,396])
            self.photo = ImageTk.PhotoImage(image)

            titleLabel = tk.Label(master=self.vidInfoFrame, text=self.vidTitle, wraplength=396)
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
            audio = ['None']
            video = ['None']
            for f in formats:
                if f.get('resolution') == 'audio only':
                    audio.append(f.get('format') + ', ' + f.get('audio_ext') + ', ' + f.get('protocol'))
                elif f.get('format_note') == 'storyboard':
                    pass
                else:
                    video.append(f.get('format') + ', ' + f.get('video_ext') + ', ' + f.get('protocol'))
            
            self.audioCB = ttk.Combobox(master=self.formatOptFrame, values=audio, width=49)
            self.audioCB.set('Choose an audio format')
            self.audioCB.pack(pady=10)
            self.videoCB = ttk.Combobox(master=self.formatOptFrame, values=video, width=49)
            self.videoCB.set('Choose a video format')
            self.videoCB.pack(pady=10)

            self.timestampFrame = tk.Frame(master=self.formatOptFrame)
            self.timestampFrame.pack()
            self.timestampLabel = tk.Label(master=self.timestampFrame, text="Download section of video (DD:HH:MM:SS)")
            self.startIn = tk.Entry(master=self.timestampFrame, width=10)
            self.dashLabel = tk.Label(master=self.timestampFrame, text="-")
            self.endIn = tk.Entry(master=self.timestampFrame, width=10)
            self.timestampLabel.grid(column=0,row=0, columnspan=3)
            self.startIn.grid(column=0, row=1)
            self.dashLabel.grid(column=1, row=1)
            self.endIn.grid(column=2, row=1)

            self.thumbnailYN = tk.IntVar()
            self.embedThumbnail = tk.Checkbutton(master=self.formatOptFrame, text="Embed thumbnail", variable=self.thumbnailYN, onvalue=1, offvalue=0)
            self.embedThumbnail.pack(pady=5)

            self.progressLogs.pack()

            self.downVid.pack(pady=10)

    def hook(self, d):
        if d['status'] == 'downloading':
            #print(d['downloaded_bytes'])
            #print(d['total_bytes'])
            prog = d['downloaded_bytes']/d['total_bytes']
            prog = int(prog*100)

            if self.cancelBool:
                self.cancelBool = False
                raise DownloadCancelled("Download cancelled")

            #self.progressbar.step(prog)
            #self.window.update()

        if d['status'] == 'finished':
            self.finishCounter += 1
    
    def cancelDown(self, event):
        self.cancelBool = True


    # downloads the video with selected options
    # - display messages to indicate progress
    # - give user option to cancel download
    def downloadVideo(self, event):
        audioFormat = self.audioCB.get()
        videoFormat = self.videoCB.get()
        startTime = self.startIn.get()
        endTime = self.endIn.get()

        # thumbnail check
        getThumbnail = False
        if self.thumbnailYN.get() == 1:
            getThumbnail = True
        elif self.thumbnailYN.get() == 0:
            getThumbnail = False

        # timestamp validation
        validTimestamps = False
        getTimestamps = False

        timestampFormat = re.compile(r'^$|(?:([0-5][0-9]):)?(?:([0-5][0-9]):)?(?:([0-5][0-9]):)?[0-5][0-9]')

        if len(startTime) > 11 or len(endTime) > 11:
            messagebox.showerror("Invalid start or end timestamp", "Check format of timestamp(s) (1)")
            validTimestamps = False
        elif not timestampFormat.match(startTime) or not timestampFormat.match(endTime):
            messagebox.showerror("Invalid start or end timestamp", "Check format of timestamp(s) (2)")
            validTimestamps = False
        elif timestampFormat.match(startTime) or timestampFormat.match(endTime):
            bad = False
            timestamps = True

            startT = startTime.split(":")
            for c in startT:
                if len(c) > 2 or len(c) < 1:
                    bad = True
            endT = endTime.split(":")
            for c in endT:
                if len(c) > 2 or len(c) < 1:
                    bad = True
            
            if (len(startT) == 1 and startT[0] == '') and (len(endT) == 1 and endT[0] == ''):
                timestamps = False
                bad = False
            
            if bad:
                messagebox.showerror("Invalid start or end timestamp", "Check format of timestamp(s) (3)")
                validTimestamps = False
            else:
                if timestamps:
                    secondsStart = 0
                    for t in range(len(startT)-1, -1, -1):
                        if t == len(startT)-1:
                            secondsStart = secondsStart + int(startT[t])
                        if t == len(startT)-2:
                            secondsStart = secondsStart + int(startT[t])*60
                        if t == len(startT)-3:
                            secondsStart = secondsStart + int(startT[t])*3600
                        if t == len(startT)-4:
                            secondsStart = secondsStart + int(startT[t])*86400
                    secondsEnd = 0
                    for t in range(len(endT)-1, -1, -1):
                        if t == len(endT)-1:
                            secondsEnd = secondsEnd + int(endT[t])
                        if t == len(endT)-2:
                            secondsEnd = secondsEnd + int(endT[t])*60
                        if t == len(endT)-3:
                            secondsEnd = secondsEnd + int(endT[t])*3600
                        if t == len(endT)-4:
                            secondsEnd = secondsEnd + int(endT[t])*86400
                    
                    if secondsStart < 0:
                        messagebox.showerror("Invalid start timestamp", "Negative time")
                        validTimestamps = False
                    elif secondsStart > self.vidDuration:
                        messagebox.showerror("Invalid start timestamp", "Start time exceeds video duration")
                        validTimestamps = False
                    elif secondsStart > secondsEnd:
                        messagebox.showerror("Invalid start timestamp", "Start time comes after end time")
                        validTimestamps = False
                    elif secondsEnd > self.vidDuration:
                        messagebox.showerror("Invalid end timestamp", "End time exceeds video duration")
                        validTimestamps = False
                    elif secondsEnd < 0:
                        messagebox.showerror("Invalid end timestamp", "Negative time")
                        validTimestamps = False
                    else:
                        validTimestamps = True
                        getTimestamps = True
                else:
                    validTimestamps = True
                    getTimestamps = False


        # format validation
        validFormats = False
        if audioFormat == 'Choose an audio format' or videoFormat == 'Choose a video format':
            messagebox.showerror("Missing format selection", "Make sure to choose an audio and video format")
            validFormats = False
        elif audioFormat == 'None' and videoFormat == 'None':
            messagebox.showerror("Missing format selection", "Make sure to choose an audio and video format")
            validFormats = False
        else:
            audioCode = audioFormat.split()[0]
            videoCode = videoFormat.split()[0]

            audioProt = audioFormat.split(', ')[-1]
            videoProt = videoFormat.split(', ')[-1]

            finFormat = ""
            audvidOnly = 0
            if audioCode == "None":
                finFormat = videoCode
                vidFor = videoFormat.split(', ')[-2]
                audvidOnly = 0
                validFormats = True
            elif videoCode == "None":
                finFormat = audioCode
                audFor = audioFormat.split(', ')[-2]
                audvidOnly = 1
                validFormats = True
            else:
                if audioProt != videoProt:
                    messagebox.showerror("Mismatched protocols", "Make sure to choose an audio and video format with the same protocol")
                    validFormats = False
                else:
                    finFormat = audioCode+"+"+videoCode
                    audFor = audioFormat.split(', ')[-2]
                    vidFor = videoFormat.split(', ')[-2]
                    validFormats = True

        if validTimestamps and validFormats:
            if self.fileLocation.cget('text') == "Download location: ":
                fileLoc = os.getcwd()
            else: 
                fileLoc = self.fileLocation.cget('text')
            if not self.filenameIn.get():
                fileName = self.vidTitle
            else:
                fileName = self.filenameIn.get()

            #self.progressbar = ttk.Progressbar(master=self.bottom, orient=tk.HORIZONTAL, length=200)
            #self.progressbar.pack()

            self.finishCounter = 0

            self.cancel = tk.Button(
                master=self.bottom,
                text="Cancel",
                width=16,
                height=2,
                relief="raised"
            )
            self.cancel.pack(pady=5)
            self.cancel.bind("<Button-1>", self.cancelDown)
            self.cancelBool = False

            try:
                #get thumbnail, with timestamps
                if getThumbnail and getTimestamps:
                    ydl_opts = {
                        'outtmpl': fileLoc + "\\" + fileName + ".%(ext)s",
                        'format': finFormat,
                        'progress_hooks': [self.hook],
                        'download_ranges': download_range_func(None, [(secondsStart, secondsEnd)]),
                        'force_keyframes_at_cuts': True,
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
                # get thumbnail, no timestamps
                elif getThumbnail and not getTimestamps:
                    ydl_opts = {
                        'outtmpl': fileLoc + "\\" + fileName + ".%(ext)s",
                        'format': finFormat,
                        'progress_hooks': [self.hook],
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
                # no thumbnail, with timestamps
                elif not getThumbnail and getTimestamps:
                    ydl_opts = {
                        'outtmpl': fileLoc + "\\" + fileName + ".%(ext)s",
                        'format': finFormat,
                        'progress_hooks': [self.hook],
                        'download_ranges': download_range_func(None, [(secondsStart, secondsEnd)]),
                        'force_keyframes_at_cuts': True,
                    }
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        error_code = ydl.download(self.linkIn.get())
                    print("Video failed to download" if error_code
                        else "Downloaded successfully")
                # no thumbnail, no timestamps
                else:
                    ydl_opts = {
                        'outtmpl': fileLoc + "\\" + fileName + ".%(ext)s",
                        'format': finFormat,
                        'progress_hooks': [self.hook],
                    }
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        error_code = ydl.download(self.linkIn.get())
                    print("Video failed to download" if error_code
                        else "Downloaded successfully")
            except DownloadCancelled:
                if '+' in finFormat:
                    if self.finishCounter == 0:
                        os.remove(fileLoc + "/" + fileName + ".f" + finFormat.split('+')[0] + "." + audFor + ".part")
                    elif self.finishCounter == 1:
                        os.remove(fileLoc + "/" + fileName + ".f" + finFormat.split('+')[0] + "." + audFor)
                        os.remove(fileLoc + "/" + fileName + ".f" + finFormat.split('+')[1] + "." + vidFor + ".part")
                elif audvidOnly == 1:
                    os.remove(fileLoc + "/" + fileName + "." + audFor + ".part")
                elif audvidOnly == 0:
                    os.remove(fileLoc + "/" + fileName + "." + vidFor + ".part")
                if self.thumbnailYN.get() == 1:
                    os.remove(fileLoc + "/" + fileName + ".webp")

            self.cancel.pack_forget()

    # start up the gui
    def enterMain(self):
        self.findVid.bind("<Button-1>", self.loadVid)
        self.downVid.bind("<Button-1>", self.downloadVideo)

        self.window.mainloop()

# text redirector to redirect output from command line to tkinter window
# if curious - https://stackoverflow.com/questions/12351786/how-to-redirect-print-statements-to-tkinter-text-widget?rq=1
class TextRedirector:
    def __init__(self, widget):
        self.widget = widget
    
    def write(self, string):
        self.widget.configure(state='normal')
        self.widget.insert('end', string)
        self.widget.configure(state='disabled')
        self.widget.update() # THIS ALMOST FIXED IT
        self.widget.see('end')
    
    def flush(self):
        pass
    

if __name__ == "__main__":
    gui = ytdlpGUI(717, 600)
    gui.enterMain()
    