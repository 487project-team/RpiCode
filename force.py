#!/usr/bin/env python3
#Dependencies
import sys, cv2, time, serial, threading, time
import tkinter as tk
from tkinter import *
#import tkinter.ttk as ttk
from queue import Queue
from PIL import Image
from PIL import ImageTk

ser = serial.Serial('/dev/ttyUSB1', 9600, timeout=None)
global limit; limit = "L"
global No; No = 0

#Class For Camera Control and Display
class App(tk.Frame):
    def __init__(self, master, title):
        tk.Frame.__init__(self, master)
        self.is_running0 = False
        self.is_running1 = False
        self.thread = None
        self.queue0 = Queue()
        self.queue1 = Queue()
        self.photo0 = ImageTk.PhotoImage(Image.new("RGB", (640, 480), "teal"))
        self.photo1 = ImageTk.PhotoImage(Image.new("RGB", (640, 480), "teal"))
        master.wm_withdraw()
        master.wm_title(title)
        self.image_gui()
        self.main_ui()
        self.bottom_ui()
        # self.grid(sticky=tk.NSEW) #Add for grid layout
        self.pack()
        self.bind('<<MessageGenerated>>', self.on_next_frame)
    
        master.bind("<e>", self.force_extend_key)
        master.bind("<r>", self.force_retract_key)
        master.bind("<KeyRelease-e>", self.force_stop_key)
        master.bind("<KeyRelease-r>", self.force_stop_key)
        master.bind("<f>", self.low_limit_key)
        master.bind("<a>", self.high_limit_key)
        master.bind("<s>", self.start_comms_key)
    
        master.wm_protocol("WM_DELETE_WINDOW", self.on_destroy)
        # master.grid_rowconfigure(0, weight = 1) #Add for grid layout
        # master.grid_columnconfigure(0, weight = 1) #Add for grid layout
        master.wm_deiconify()
        
    def image_gui(self):
        self.button_frame = tk.Frame(self)
        self.view0 = Label(self.button_frame, image=self.photo0)
        self.view0.pack(side=tk.LEFT, expand=True)
        self.view1 = Label(self.button_frame, image=self.photo1)
        self.view1.pack(side=tk.RIGHT, expand=True)
        self.button_frame.pack()#side=tk.TOP, fill=tk.BOTH, expand=False)
#App UI frame layout and button creation
    def main_ui(self):
        self.button_frame1 = tk.Frame(self)
        self.start0_button = tk.Button(self.button_frame1, text="P3-Cam-Start", width=10, bg="green", fg="white", command= lambda: self.start(0))
        self.start0_button.pack(anchor="nw", side=tk.LEFT)     
        self.stop0_button = tk.Button(self.button_frame1, text="P3-Cam-Stop", width=10, bg="red", fg="white", command= lambda: self.stop(0))
        self.stop0_button.pack(anchor="nw", side=tk.LEFT)
        self.start1_button = tk.Button(self.button_frame1, text="DI-Cam-Start", width=10, bg="green", fg="white", command= lambda: self.start(2))
        self.start1_button.pack(anchor="ne", side=tk.RIGHT)     
        self.stop1_button = tk.Button(self.button_frame1, text="DI-Cam-Stop", width=10, bg="red", fg="white", command= lambda: self.stop(2))
        self.stop1_button.pack(anchor="ne", side=tk.RIGHT) 
        self.button_frame1.pack()#side=tk.TOP, fill=tk.BOTH, expand=True)

    def bottom_ui(self):
        self.button_frame2 = tk.Frame(self)
        self.Lbutton = Button(self.button_frame2, text="Fiberglass", width=10, bg="alice blue", fg="green", relief=SUNKEN, command=self.low_limit)
        self.Lbutton.pack(side=RIGHT)
        self.Hbutton = Button(self.button_frame2, text="Aluminum", width=10, bg="gray", fg="red", command=self.high_limit)
        self.Hbutton.pack(side=RIGHT)
        self.Ebutton = Button(self.button_frame2, text="Extend", width=10, bg="gray", fg="green", command=self.force_extend)
        self.Ebutton.pack(side=LEFT)
        self.Rbutton = Button(self.button_frame2, text="Retract", width=10, bg="gray", fg="red", command=self.force_retract)
        self.Rbutton.pack(side=LEFT)
        self.Cbutton = Button(self.button_frame2, text="Start Arduino Serial Comms", width=30, bg="gray", fg="white", command=self.start_comms)
        self.Cbutton.pack(side=BOTTOM)
        self.forceStatus = Label(self.button_frame2, text="Linear Actuator Status",width=30, height=4)
        self.forceStatus.pack(side=BOTTOM)
        self.forceReading = Label(self.button_frame2, text="Applied Force __ (lbs)",width=30, height=4)
        self.forceReading.pack(side=BOTTOM)
        self.button_frame2.pack()#side=tk.TOP, fill=tk.BOTH, expand=True)
    
        # Hbutton.grid(column=0,row=1)
        # Lbutton.grid(column=0,row=2)
        # Rbutton.grid(column=1,row=2)
        # Ebutton.grid(column=1,row=1)
        # forceLabel.grid(column=0,row=3)
        # forceReading.grid(column=0,row=4)
    
#####threading included for application performance
    def on_destroy(self):
        self.stop(0)
        self.stop(2)
        self.after(20)
        if self.thread is not None:
            self.thread.join(0.2)
        self.winfo_toplevel().destroy()

    def start(self, Num):
        No = Num
        if No == 0:
            self.is_running0 = True
            self.thread0 = threading.Thread(target=self.videoLoop0, args=(),daemon=True).start()
        else:
            self.is_running1 = True
            self.thread1 = threading.Thread(target=self.videoLoop1, args=(),daemon=True).start()

    def stop(self, Num):
        No = Num
        if No == 0:
            self.is_running0 = False
            #time.sleep(1)
            #self.photo0 = ImageTk.PhotoImage(Image.new("RGB", (160, 120), "teal"))
            
        else:
            self.is_running1 = False
            #time.sleep(1)
            #self.photo1 = ImageTk.PhotoImage(Image.new("RGB", (160, 120), "teal"))

#####Onboard Camera video feed, for different camera change No=0,1,2,n....    
    def videoLoop0(self, mirror=False):
        cap0 = cv2.VideoCapture(No)
        cap0.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap0.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        time.sleep(2)
        while self.is_running0:
            ret0, cam0 = cap0.read()
            if mirror is True:
                cam0 = cam0[:,::-1]
            image0 = cv2.cvtColor(cam0, cv2.COLOR_BGR2RGB)
            self.queue0.put(image0)
            self.event_generate('<<MessageGenerated>>')
            
    def videoLoop1(self, mirror=False):
        cap1 = cv2.VideoCapture(No)
        cap1.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap1.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        time.sleep(2)
        while self.is_running1:
            ret1, cam1 = cap1.read()
            if mirror is True:
                cam1 = cam1[:,::-1]
            image1 = cv2.cvtColor(cam1, cv2.COLOR_BGR2RGB)
            self.queue1.put(image1)
            self.event_generate('<<MessageGenerated>>')
            
#####Camera Performance Magic
    def on_next_frame(self, eventargs):
        if not self.queue0.empty():
            image0 = self.queue0.get()
            image0 = Image.fromarray(image0)
            self.photo0 = ImageTk.PhotoImage(image0)
            self.view0.configure(image=self.photo0)
        if not self.queue1.empty():
            image1 = self.queue1.get()
            image1 = Image.fromarray(image1)
            self.photo1 = ImageTk.PhotoImage(image1)
            self.view1.configure(image=self.photo1)

    def low_limit(self):
        limit = "L"
        self.Lbutton.config(relief=SUNKEN, bg = "alice blue")
        self.Hbutton.config(relief=RAISED, bg = "gray")
        
    def high_limit(self):
        limit = "H"
        self.Hbutton.config(relief=SUNKEN, bg = "alice blue")
        self.Lbutton.config(relief=RAISED, bg = "gray")
        
    def start_comms_needle(self):
        while True:
            if ser.in_waiting:
                global forceimport
                forceimport = str(ser.readline().decode('utf_8')).replace("\r\n", "")
                self.forceStatus["text"] = "Linear Actuator "+ forceimport[0:7]
                self.forceReading["text"] = "Load Cell Reads " + forceimport[7:] + " lbs"
            time.sleep(0.1)

    def start_comms(self):
        threading.Thread(target=self.start_comms_needle, args=(), daemon=True).start()
    
    def force_retract_needle(self):
        forcecommand = limit + "R"
        ser.write(str(forcecommand).encode('utf_8'))
        
    def force_extend_needle(self):
        forcecommand = limit + "E"
        ser.write(str(forcecommand).encode('utf_8'))

    def force_extend(self):
        threading.Thread(target=self.force_extend_needle, args=(), daemon=True).start()
    
    def force_retract(self):
        threading.Thread(target=self.force_retract_needle, args=(), daemon=True).start()

    def force_extend_key(self, args):
        self.Ebutton.config(relief=SUNKEN)
        self.force_extend()
        
    def force_retract_key(self, args):
        self.Rbutton.config(relief=SUNKEN)
        self.force_retract()
        
    def low_limit_key(self, args):
        self.low_limit()
        
    def high_limit_key(self, args):
        self.high_limit()
        
    def start_comms_key(self, args):
        self.start_comms()
        
    def force_stop_key(self, args):
        self.Ebutton.config(relief=RAISED)
        self.Rbutton.config(relief=RAISED)

#def main(args):
root = tk.Tk()
App(root, "Force Control Menu")  
        
#Controls Menu Settings
top = Toplevel()
top.title("About this application...")
msg = Message(top, text="Place Holder Instructions")
msg.pack()
button = Button(top, text="Dismiss", command=top.destroy)
button.pack()
    
#   root.geometry("750x750")
root.mainloop()

if __name__ == '__main__':
    sys.exit(main(sys.argv))
