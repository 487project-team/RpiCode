#Dependencies
import sys
#Import cv2 like this for VScode Users
from cv2 import cv2
import threading
import tkinter as tk
import tkinter.ttk as ttk
from queue import Queue
from PIL import Image
from PIL import ImageTk

#Set up Application
class App(tk.Frame):
    def __init__(self, master, title):
        tk.Frame.__init__(self, master)
        self.is_running = False
        self.thread = None
        self.queue = Queue()
        self.photo = ImageTk.PhotoImage(Image.new("RGB", (640, 480), "teal"))
        master.wm_withdraw()
        master.wm_title(title)
        self.main_ui()
        self.grid(sticky=tk.NSEW)
        self.bind('<<MessageGenerated>>', self.on_next_frame)
        master.wm_protocol("WM_DELETE_WINDOW", self.on_destroy)
        master.grid_rowconfigure(0, weight = 1)
        master.grid_columnconfigure(0, weight = 1)
        master.wm_deiconify()
        #Control Variables
        self.forcelimit = "L"
        self.forcecommand = "LS"
        self.forceimport = "S56789"
        #Key binds control everything
        master.bind("<e>", self.handle_extend)
        master.bind("<r>", self.handle_retract)
        master.bind("<l>", self.handle_low)
        master.bind("<h>", self.handle_high)
        master.bind("<KeyRelease-r>", self.handle_stop)
        master.bind("<KeyRelease-e>", self.handle_stop)
        #window.bind("<0>", update_serial)
        self.buttonE.bind("<Button-1>", self.handle_extend)
        self.buttonE.bind("<ButtonRelease-1>", self.handle_stop)
        self.buttonR.bind("<Button-1>", self.handle_retract)
        self.buttonR.bind("<ButtonRelease-1>", self.handle_stop)
        self.buttonH.bind("<Button-1>", self.handle_high)
        self.buttonL.bind("<Button-1>", self.handle_low)
#App UI frame layout and button creation
#.grid(row=n,column=n) or .pack()
    def main_ui(self):
#########Camera UI        
        self.cam_frame = tk.Frame(self)
        self.camStart = tk.Button(self.cam_frame, text="CAM-ON", width=20,background="green", command=self.start)
        self.camStart.pack(side=tk.LEFT)        
        self.camStop = tk.Button(self.cam_frame, text="CAM-OFF", width=20, background="red", command=self.stop)
        self.camStop.pack(side=tk.LEFT)
        self.vid = ttk.Label(self, image=self.photo)
        self.vid.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.cam_frame.pack(side=tk.TOP, fill=tk.X, expand=True)
##########Force Control Button UI
        self.force_Frame = tk.Frame(self)
        self.buttonH = tk.Button(self.force_Frame,text="High Limits", width=20, height=1, bg="gray", fg="red")
        self.buttonH.pack(side=tk.LEFT)
        self.buttonL = tk.Button(self.force_Frame,text="Low Limits", width=20, height=1, bg="gray", fg="green")
        self.buttonL.pack(side=tk.LEFT)
        self.buttonR = tk.Button(self.force_Frame,text="Retract", width=20, height=1, bg="gray", fg="red")
        self.buttonR.pack(side=tk.RIGHT)
        self.buttonE = tk.Button(self.force_Frame,text="Extend", width=20, height=1, bg="gray", fg="green")
        self.buttonE.pack(side=tk.RIGHT)
        self.force_Frame.pack(side=tk.BOTTOM, fill=tk.X, expand=True)
#####threading included for application performance
    def on_destroy(self):
        self.stop()
        self.after(20)
        if self.thread is not None:
            self.thread.join(0.2)
        self.winfo_toplevel().destroy()

    def start(self):
        self.is_running = True
        self.thread = threading.Thread(target=self.videoLoop, args=())
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self.is_running = False
#####Onboard Camera video feed, for different camera change No=0,1,2,n....    
    def videoLoop(self, mirror=False):
        No=0
        cap = cv2.VideoCapture(No)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        while self.is_running:
            ret, cam = cap.read()
            if mirror is True:
                cam = cam[:,::-1]
            image = cv2.cvtColor(cam, cv2.COLOR_BGR2RGB)
            self.queue.put(image)
            self.event_generate('<<MessageGenerated>>')
#####Camera Performance Magic
    def on_next_frame(self, eventargs):
        if not self.queue.empty():
            image = self.queue.get()
            image = Image.fromarray(image)
            self.photo = ImageTk.PhotoImage(image)
            self.vid.configure(image=self.photo)
####Defining Motor Controller Actions
    def handle_low(self,event):
        self.forcelimit
        self.forcelimit = "L"
        self.buttonL.config(relief=tk.SUNKEN)
        self.buttonH.config(relief=tk.RAISED)
    def handle_high(self,event):
        self.forcelimit
        self.forcelimit = "H"
        self.buttonH.config(relief=tk.SUNKEN)
        self.buttonL.config(relief=tk.RAISED)
    def handle_extend(self,event):
        self.forcelimit
        self.forcecommand
        self.forcecontrol = "E"
        self.buttonE.config(self,relief=tk.SUNKEN)
        self.forcecommand =  self.forcelimit +  self.forcecontrol
    def handle_retract(self,event):
        self.forcelimit
        self.forcecommand
        self.forcecontrol = "R"
        self.buttonR.config(relief=tk.SUNKEN)
        self.forcecommand =  self.forcelimit +  self.forcecontrol
    def handle_stop(self,event):
        self.forcelimit
        self.forcecommand
        self.forcecontrol = "S"
        self.buttonE.config(relief=tk.RAISED)
        self.buttonR.config(relief=tk.RAISED)
        self.forcecommand =  self.forcelimit +  self.forcecontrol


def main(args):
    root = tk.Tk()
####Application Name Output, icon, sounds, and images should be place in 
####Resource folder found in app directory
    app = App(root, "Force Control Menu")
    root.iconbitmap("Resources/appIcon.ico")
    root['bg']="teal"
####root.geometry("750x750")
    root.mainloop()


if __name__ == '__main__':
    sys.exit(main(sys.argv))