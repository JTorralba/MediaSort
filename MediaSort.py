#!/usr/bin/env python

from tkinter import *
from EXIFTool import *

import time
import os
import sys
import threading
import traceback
import queue
import shutil
import tkinter.filedialog

class StopWatch(Frame):

    def __init__(self, parent=None, **kw):

        Frame.__init__(self, parent, kw)
        self.Queue = queue.Queue()
        self.Running = 0

        self.Timer = StringVar()
        self.Timer_Start = time.time()
        self.Timer_Elapsed = 0.0

        self.Widgets()
        self.Update()

        self.Location = WhereAmI()
        self.Queue_Add('LOC: ' + self.Location)

    def Widgets(self):
        TimerLabel = Label(self, textvariable=self.Timer)
        self.Set(self.Timer_Elapsed)
        TimerLabel.pack(fill=X, expand=NO, pady=2, padx=2)

        SBH = Scrollbar(self, orient=HORIZONTAL)
        SBH.pack(side=BOTTOM, fill=X)

        SBV = Scrollbar(self, orient=VERTICAL)
        SBV.pack(side=RIGHT, fill=Y)

        global Console
        # Windows scrollbar bug/crash.
        if (os.name == 'nt'):
            Console = Text(self, wrap=NONE)
        else:
            Console = Text(self, wrap=NONE, xscrollcommand=SBH.set, yscrollcommand=SBV.set)
        Console.pack(expand=TRUE, fill=BOTH)
        Console.bind('<Configure>', lambda e: Console.configure(width=e.width-10))
        SBH.config(command=Console.xview)
        SBV.config(command=Console.yview)

    def Set(self, Elapse):
        Minutes = int(Elapse/60)
        Seconds = int(Elapse - Minutes*60.0)
        HSeconds = int((Elapse - Minutes*60.0 - Seconds)*100)
        self.Timer.set('%02d:%02d:%02d' % (Minutes, Seconds, HSeconds))

    def StartStop(self):
        if not self.Running:
            self.Timer_Start = time.time() - self.Timer_Elapsed
            self.Update()
            self.Running = 1
        else:
            self.after_cancel(self._timer)
            self.Timer_Elapsed = time.time() - self.Timer_Start
            self.Set(self.Timer_Elapsed)
            self.Running = 0

    def Reset(self):
        with self.Queue.mutex:
            self.Queue.queue.clear()
        Console.delete(1.0, END)
        self.Timer_Start = time.time()
        self.Timer_Elapsed = 0.0
        self.Set(self.Timer_Elapsed)

    def Queue_Add(self, Line):
        self.Queue.put(Line)

    def Write(self, Line):
        try:
            Line = Line.replace('/', Slash)
            RowCol = Console.index('end-1c')
            LineNumber = RowCol[:-2]
            Console.insert(END, Line.encode('utf-8'))
            Console.insert(END, '\n')
            Console.see(END)
            Console.tag_add(LineNumber, RowCol, str(float(RowCol) + 0.4))
            if (Line[:3] == 'LOC'):
                Console.tag_config(LineNumber, background='gold', foreground='black')
            else:
                if Line[:3] == 'MED':
                    Console.tag_config(LineNumber, background='darkseagreen', foreground='black')
                else:
                    if Line[:3] == 'FYI':
                        Console.tag_config(LineNumber, background='gold', foreground='black')
                    else:
                        if (Line[:3] == 'EXC'):
                            Console.tag_config(LineNumber, background='indianred', foreground='black')
                        else:
                            if (Line[:3] == 'STS'):
                                Console.tag_config(LineNumber, background='violet', foreground='black')
                            else:
                                Console.tag_config(LineNumber, background='white', foreground='black')
            Console.pack()
            Console.update_idletasks()
        except:
            print(traceback.format_exc())
            pass

    def Update(self):
        if self.Running:
            self.Timer_Elapsed = time.time() - self.Timer_Start
            self.Set(self.Timer_Elapsed)
        try:
            Line = self.Queue.get_nowait()
            self.Write(Line)
        except:
            pass

        self._timer = self.after(100, self.Update)

    def MED_Button_Root_LED(self):
        if MED_Button.cget('state') == DISABLED:
            BG = MED_Button.cget('bg')
            FG = MED_Button.cget('fg')
            MED_Button.configure(bg = FG)
            MED_Button.configure(fg = BG)
            self.after(500, self.MED_Button_Root_LED)
        else:
            MED_Button.configure(bg = MED_Button_BG)
            MED_Button.configure(fg = MED_Button_FG)

    def GetLocation(self):
        Options = {}
        Options['initialdir'] = self.Location
        #Options['filetypes'] = [('JPG Files','.jpg'),('JPG Files','.JPG'),('PNG Files','.png'),('PNG Files','.PNG'),('AVI Files','.avi'),('AVI Files','.AVI'),('MOV Files','.mov'),('MOV Files','.MOV'),('MP4 Files','.mp4'),('MP4 Files','.MP4'),('MTS Files','.mts'),('MTS Files','.MTS'),('WAV Files','.wav'),('WAV Files','.WAV')]
        Options['title'] = 'Open Media File'
        File = tkinter.filedialog.askopenfilename(**Options)
        if File:
            self.Location = os.path.split(File)[0]
            self.Queue_Add('LOC: ' + self.Location)

def Clear():
    global CMD
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def S_Action(SW):
    SW.StartStop()

def R_Action(SW):
    SW.Reset()

def Worker(SW, Thread):
    Button_X = Thread + '_Button'
    Button_X_BG = Thread + '_Button_BG'
    Button_X_FG = Thread + '_Button_FG'

    globals()[Button_X_BG] = globals()[Button_X].cget('bg')
    globals()[Button_X_FG] = globals()[Button_X].cget('fg')
    globals()[Button_X].configure(state=DISABLED)

    CMD = 'SW.' + Button_X + '_Root_LED()'
    exec(CMD)

    X = threading.Thread(target = globals()[Thread], args=(SW,))
    X.start()

def Sleep():
    time.sleep(0)

def WhereAmI():
    return os.path.dirname(os.path.realpath(__import__('__main__').__file__))

def MED(SW):
    SW.StartStop()

    Current_Location = SW.Location

    if Current_Location != 'CANCEL':

        for Path, Folders, Files in os.walk(Current_Location, topdown=False):

            for File in sorted(Files, reverse=True):

                if os.path.isfile(os.path.join(Path, File)):
                    From = Path + Slash + File

                    BASE = File_Base(File)
                    EXT = File_Extension(File)

                    if Tree.get() == 1:
                        New_Location = Current_Location + Slash + '..' + Slash + EXT + Slash + Make(From) + Slash + Model(From) + Slash + Dimension(From) + Slash
                    else:
                        New_Location = Current_Location + Slash + '..' + Slash + EXT + Slash
 
                    DateTimeOriginal = Type(From)
                    if DateTimeOriginal != '':
                        Date_YYYY = DateTimeOriginal[0:4]
                        Date_MM = DateTimeOriginal[5:7]
                        Date_DD = DateTimeOriginal[8:10]
                        Time_HH = DateTimeOriginal[11:13]
                        Time_MM = DateTimeOriginal[14:16]
                        Time_SS = DateTimeOriginal[17:19]
                        BASE = Date_YYYY + '-' + Date_MM + '-' + Date_DD + '_' + Time_HH + Time_MM + Time_SS

                    if not os.path.exists(New_Location):
                        try:
                            os.makedirs(New_Location, 777)
                        except:
                            print('MED(SW): ' + traceback.format_exc())

                    To = New_Location + BASE + '.' + EXT.lower()

                    I = 0;
                    while os.path.isfile(To):
                        I += 1
                        To = New_Location + BASE + '_' + str(I).zfill(6) + '.' + EXT.lower()

                    try:
                        shutil.move(From, To)
                        SW.Queue_Add('MED: ' + File + ' --> ' + To)
                    except:
                        SW.Queue_Add('STS: ' + File + ' (Could not move file.)')
                        print('MED(SW): ' + traceback.format_exc())
                        pass

                Sleep()

            try:
                if len(os.listdir(Path)) == 0:
                    os.rmdir(Path)
            except:
                pass

    MED_Button.configure(state=NORMAL)
    SW.StartStop()

def LOC_Action(SW):
    SW.GetLocation()

def T_Action():
    print(Tree.get())

def main():
    root = Tk()
    root.title('MediaSort')
    root.geometry('640x480')
    root.resizable(0,0)

    global Slash
    if os.name == 'nt':
        Slash = '\\'
    else:
        Slash = '/'
  
    global Tree
    Tree = IntVar()
    Tree.set(0)

    SW = StopWatch(root)
    SW.pack(side=TOP, expand=TRUE, fill=BOTH)

    PadX = 10

    LOC_Button = Button(root, text='LOC', padx=PadX*2, command=lambda:LOC_Action(SW))
    LOC_Button.pack(side=LEFT)

    global MED_Button
    MED_Button = Button(root, text='MED', padx=PadX*2, command=lambda:Worker(SW,'MED'))
    MED_Button.pack(side=LEFT)

    Tree_CheckButton = Checkbutton(root, text='Tree', variable=Tree, onvalue=1, offvalue=0, padx=PadX)
    Tree_CheckButton.pack(side=LEFT)

    Q_Button = Button(root, text='Q', padx=PadX, command=root.destroy)
    Q_Button.pack(side=RIGHT)

    R_Button = Button(root, text='R', padx=PadX, command=lambda:R_Action(SW))
    R_Button.pack(side=RIGHT)

    S_Button = Button(root, text='S', padx=PadX, command=lambda:S_Action(SW))
    S_Button.pack(side=RIGHT)

    root.mainloop()

if __name__ == '__main__':
    Clear()
    main()
