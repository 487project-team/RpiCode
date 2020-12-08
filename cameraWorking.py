#Dependencies
import sys
import cv2
import threading
import tkinter as tk
from tkinter import *
import tkinter.ttk as ttk
from queue import Queue
from PIL import Image
from PIL import ImageTk

#Class For Camera Control and Display
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
#App UI frame layout and button creation
    def main_ui(self):
        self.button_frame = tk.Frame(self)
        self.stop_button = tk.Button(self.button_frame, text="Cam-Stop", width=20, background="red", command=self.stop)
        self.stop_button.pack(side=tk.RIGHT)
        self.start_button = tk.Button(self.button_frame, text="Cam-Start", width=20,background="green", command=self.start)
        self.start_button.pack(side=tk.RIGHT)        
        self.view = ttk.Label(self, image=self.photo)
        self.view.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.button_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True)
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
            self.view.configure(image=self.photo)


#Indicator Frame Set up
class IndicatorFrame (Frame):
    def __init__(self, the_window):
        super().__init__()
        self["height"]=150
        self["width"]=150
        self["relief"]=RAISED
        self["highlightbackground"]="black"
        self["highlightthickness"]=3
        self["bg"]="grey"



def main(args):
    root = Tk()
#    root.iconbitmap("Resources/appIcon.ico")
#
    app = App(root, "Force Control Menu")
#
    frame_a = IndicatorFrame(root)
    label_L=Label(frame_a, text="High Limits",width=10,fg="grey", relief=RAISED,padx=30).pack(side=RIGHT)
    label_H=Label(frame_a, text="Low Limits",width=10,fg="grey", relief=RAISED,padx=30).pack(side=RIGHT)
    label_R=Label(frame_a, text="Retract",width=10,fg="grey", relief=RAISED,padx=30).pack(side=LEFT)
    label_E=Label(frame_a, text="Extend",width=10,fg="grey", relief=RAISED,padx=30).pack(side=LEFT)
    frame_a.grid(row=1,column=0)
    
#Controls Menu Settings
    top = Toplevel()
    #top.iconbitmap("Resources/appIcon.ico")
    top.title("About this application...")
    msg = Message(top, text="Place Holder Instructions")
    msg.pack()

    button = Button(top, text="Dismiss", command=top.destroy)
    button.pack()

 #   root.geometry("750x750")
    root.mainloop()

if __name__ == '__main__':
    sys.exit(main(sys.argv))
