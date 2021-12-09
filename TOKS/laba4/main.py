import math
import time
from tkinter import *
from tkinter import ttk
from tkinter.messagebox import showinfo

import serial
import threading
import random

threads = 0
stringBuf = []
string_send_buf = ""
send_flag = 0
start_flag = 0
fl1 = 0
ser = None
flag = 0
state = 2
outState = 2
prevState = 0
maxAttempts = 10
jamSignal = 0
clock = 0
collision = 0
not_connected = 0
pick_flag = 0


def Connect():
    global pick_flag
    global ser
    global thread
    try:
        ser = serial.Serial("COM3",timeout=0)
        pick_flag = 1
    except Exception:
        if pick_flag == 0:
            Error("Port is closed")
    if pick_flag == 1:
        try:
            ser = serial.Serial("COM4",timeout=0)
            pick_flag = 1
        except Exception:
            if pick_flag == 0:
                Error("Port is closed")
    thread.start()

def Error(text):
    msg = text
    showinfo(title='Error', message=msg)

def send():
    global ser
    mes = inputEntry.get()
    if len(mes) > 0:
        writeMessage(mes)
    inputEntry.config(validate="none")
    inputEntry.delete(0, END)
    inputEntry.config(validate="key")

def fillFrame(message):
    while len(message) != 23:
        message.append(0)

def makeFrame(message):
    global state
    if len(message) < 22:
        fillFrame(message)
        frame = message
        state = 0
        return frame
    if len(message) == 23:
        #message.append(0)
        frame = message
        state = 1
        return frame
    if len(message) > 23 or state == 2:
        frame = message[:23]
        del message[:23]
        state = 2
        return frame


def channelBusy():
    return 0 if random.randint(1, 5) == 1 else 1


def makeCol():
    return random.randint(0, 1)


def out_flag():
    global send_flag
    send_flag = 1

def acceptMessage():
    global ser
    global collision
    global clock
    global jamSignal
    global outState
    global prevState
    time1 = 0
    buf = []
    while True:
        len_ = 0
        while len_ < 1 and collision != 1:
            mes = ser.readline().decode()
            time.sleep(0.2)
            if mes == '1':
                prevState = outState
                outState = 1
            if mes == '0':
                prevState = outState
                outState = 0
            if clock == 1 and len(mes) == 0:
                time2 = time.time() - time1
                if time2 > 0.3:
                    collision = 1
                    clock = 0
                    time1 = 0
            len_ = len(mes)
        if (mes != '0' and mes != '1') or collision == 1:
            if mes!="":
                print("received: " + mes)
            if len(buf) == 0 and collision == 0 and mes != 'c':
                buf.append(mes)
                time1 = time.time()
                clock = 1
            elif mes == 'c':
                print("jam signal")
                buf.clear()
                time1 = 0
                clock = 0
            elif collision == 1:
                str_output = buf.pop()
                bit_list = [str(i) for i in list(str_output)]
                decodeMessage(bit_list)
                buf.clear()
                collision = 0
                time1 = 0
                clock = 0
            else:
                str_output = buf.pop()
                outState = 0
                bit_list = [str(i) for i in list(str_output)]
                decodeMessage(bit_list)
                buf.append(mes)
                time1 = time.time()
                clock = 1


def decodeMessage(mes):
    global prevState
    global outState
    bit_str = list(mes)
    tmp = ''.join(str(i) for i in bit_str)
    if outState == 1 and prevState == 0:
        tmp = tmp[:len(tmp) - 1]
        outState = 2
    elif outState == 2 and prevState == 0:
        tmp = ''
        tmp = tmp.join(str(i) for i in bit_str)
        outState = 2
    elif prevState == 0 and outState == 0:
        outState = 2
    stringBuf.append(tmp)
    return tmp

thread = threading.Thread(target=acceptMessage)
thread.daemon = True

def writeMessage(mes):
    global state
    global ser
    bit_str = [int(i) for i in list(mes)]
    state = 2
    attempts = 0
    debugListbox.insert(END,"User input: " + mes)
    print("user input: " + mes)
    while state == 2:
        state = 0
        bit_list = makeFrame(bit_str)
        while True:
            while channelBusy() != 0:
                print("channel is busy")
            print("channel is free")
            if state == 2:
                ser.write('0'.encode())
                time.sleep(0.1)
            if state == 1:
                ser.write('1'.encode())
                time.sleep(0.1)
            tmp = ''
            tmp = tmp.join(str(c) for c in list(bit_list))
            ser.write(tmp.encode())
            time.sleep(0.1)
            if makeCol() == 1:
                ser.write('c'.encode())
                time.sleep(0.1)
                attempts += 1
                if attempts < maxAttempts:
                    time.sleep(random.randint(0, 2 ** min(attempts, 10)) * 0.01)
                else:
                    break
            else:
                break
        debugListbox.insert(END, tmp + ':' + '*' * attempts)
        attempts = 0


def PortDisplay():
    global send_flag
    global not_connected
    while len(stringBuf) > 0:
        str_ = stringBuf.pop(0)
        if str_ != '':
            outputListbox.insert(0, str_)
    if send_flag:
        send()
        send_flag = 0
    root.after(100, PortDisplay)

def changeBaudrate():
    global ser
    ser.baudrate = int(speed.get())


def inputValidation(char):
    if char.isdigit():
        if char == "0" or char == "1":
            return True
        else:
            return False
    else:
        return False


root = Tk() #создаем форму
root.title("laba3")
root.resizable(False,False)

input = LabelFrame()
input.pack()

out = LabelFrame()
out.pack()

debug = LabelFrame()
debug.pack(side="top")

scrollbar = Scrollbar(out)
scrollbar.pack(side=RIGHT, fill=Y)
outputListbox = Listbox(out, yscrollcommand=scrollbar.set, width=70, height=7)
outputListbox.pack(side=LEFT)

validation = root.register(inputValidation)
inputEntry = Entry(input, width=72, validate="key", validatecommand=(validation, "%S"))
binary_input = root.register(inputValidation)
inputEntry.config(validate="key", validatecommand=(binary_input, '%S'))
inputEntry.pack()

debugListbox = Listbox(debug, width=70, height=5)
debugListbox.pack()

speed = ttk.Combobox(debug, values=[2400,4800,9600,19200,38400,57600,115200])
speed.current(2)
speed.pack(fill= X)

buttonChoose = ttk.Button(debug, text ="confirm", command =changeBaudrate)
buttonChoose.pack()

sendButton = Button(debug, text ="send", command = out_flag)
sendButton.pack(side=BOTTOM)

Connect()
root.after(10, PortDisplay)
root.mainloop()
