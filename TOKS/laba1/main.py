import threading
import time
import tkinter
from tkinter import *
from tkinter import ttk
from tkinter.messagebox import showinfo
import serial

stringBuffer = []
sendFlag = 0
startFlag = 0
fl1=0
ser = None
pickFlag = 0

def getInput():
    global ser
    global startFlag
    global stringBuffer
    while 1:
        in_len = 0
        while in_len<1:
            try:
                in_st = ser.readline() #считали строку
                in_len = len(in_st)#сохранили длину
            except Exception:
                if ser is None:
                    debugListbox.insert(END, "Error while reading from port(getInput()).")
                    debugListbox.insert(END, "Enable ports and re-open the program")
                    break
        stringBuffer.append(in_st.decode())
        time.sleep(1)

tr_in = threading.Thread(target = getInput) #поток приема
tr_in.daemon = True

def Send():
    global ser
    out_st = inputEntry.get()
    if len(out_st)>0:
        try:
            ser.write(out_st.encode())
            #outputListbox.insert(END, ">" + out_st)
        except Exception:
            if ser is None:
                Error("Cant write!")
                debugListbox.insert(END, "Error in a Send() function.")
                debugListbox.insert(END, "Enable ports and re-open the program")
    inputEntry.delete(0, END)

def outFlag():
    global sendFlag #флаг запроса на передачу
    sendFlag =1

def PortDisplay():
    global sendFlag
    while len(stringBuffer)>0:
        st = stringBuffer.pop(0)
        outputListbox.insert(END, st)
    if sendFlag:
        Send()
        sendFlag = 0
    root.after(100,PortDisplay)#бесконечный цикл

def Connect1():
    global startFlag
    global ser
    global tr_in
    try:
        ser = serial.Serial('COM3', int(speed.get()), timeout=1)
    except Exception:
        if ser is None:
          Error("port is closed")
    #tr_in.start()
    startFlag = 1

def Connect2():
    global startFlag
    global ser
    global tr_in
    try:
        ser = serial.Serial('COM4', int(speed.get()), timeout=1)
    except Exception:
        if ser is None:
            Error("port is closed")
    #tr_in.start()
    startFlag = 1

def Choose():
    global pickFlag
    global fl1
    if fl1 == 0:
        if pickFlag == 0:
            Connect1()
            pickFlag = 1
        if pickFlag == 1:
            Connect2()
            pickFlag = 0
        fl1=1
        tr_in.start()

def Error(text):
    msg = text
    showinfo(title='Result', message=msg)

root = Tk() #создаем форму
root.title("laba1")
root.resizable(False, False)

input = LabelFrame()
input.pack()

output = LabelFrame()
output.pack()

debug = LabelFrame()
debug.pack(side="top")

scrollbar = Scrollbar(output)
scrollbar.pack(side=RIGHT, fill=Y)
outputListbox = Listbox(output, yscrollcommand=scrollbar.set, width=70, height=7)
outputListbox.pack(side=LEFT)

inputEntry = Entry(input, width = 72)
inputEntry.pack()

debugListbox = Listbox(debug, width=70, height=5)
debugListbox.pack()

# comPort = ttk.Combobox(debug, values=["Com3", "Com4"])
# comPort.pack(fill= X)

speed = ttk.Combobox(debug, values=[2400,4800,9600,19200,38400,57600,115200])
speed.pack(fill= X)

buttonChoose = ttk.Button(debug, text ="confirm", command = Choose)
buttonChoose.pack()

sendButton = Button(debug, text ="input", command = outFlag)
sendButton.pack(side=BOTTOM)

root.after(10,PortDisplay)
root.mainloop()