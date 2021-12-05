import math
import time
from tkinter import *
from tkinter import ttk
from tkinter.messagebox import showinfo

import serial
import threading
import random

threads = 0
string_buf = []
string_send_buf = ""
send_flag = 0
start_flag = 0
fl1 = 0
ser = None
flag = 0
state = 2
state_output = 2
state_prev = 0
attempts_max = 10
jam = 0
clock = 0
no_collision = 0
not_connected = 0


def Connect():
    global start_flag
    global ser
    global thread
    try:
        ser = serial.Serial("COM2", timeout=0)
    except Exception:
        if ser is None:
            try:
                ser = serial.Serial("COM3", timeout=0)
            except Exception:
                if ser is None:
                   Error("Error opening ports")
            else:
                start_flag = 1
    else:
        start_flag = 1
    finally:
        if start_flag == 1:
            thread.start()

def Error(text):
    msg = text
    showinfo(title='Error', message=msg)

def Input():
    global ser
    global no_collision
    global clock
    global state_output
    global state_prev
    global jam
    time1 = 0
    buf = []
    while True:
        len_ = 0
        while len_ < 1 and no_collision != 1:
            str_ = ser.readline().decode()
            time.sleep(0.2)
            if str_ == '1':
                state_prev = state_output
                state_output = 1
            if str_ == '0':
                state_prev = state_output
                state_output = 0
            if clock == 1 and len(str_) == 0:
                time2 = time.time() - time1
                if time2 > 0.3:
                    no_collision = 1
                    clock = 0
                    time1 = 0
            len_ = len(str_)
        if (str_ != '0' and str_ != '1') or no_collision == 1:
            print(str_)
            if len(buf) == 0 and no_collision == 0 and str_ != 'c':
                buf.append(str_)
                time1 = time.time()
                clock = 1
            elif str_ == 'c':
                print("jam signal")
                buf.clear()
                time1 = 0
                clock = 0
            elif no_collision == 1:
                str_output = buf.pop()
                bit_list = [str(i) for i in list(str_output)]
                decodeMessage(bit_list)
                buf.clear()
                no_collision = 0
                time1 = 0
                clock = 0
            else:
                str_output = buf.pop()
                state_output = 0
                bit_list = [str(i) for i in list(str_output)]
                decodeMessage(bit_list)
                buf.append(str_)
                time1 = time.time()
                clock = 1


def decodeMessage(message):
    global state_prev
    global state_output
    bit_str = list(message)
    bit_str_tmp = ''.join(str(i) for i in bit_str)
    if state_output == 1 and state_prev == 0:
        bit_str_tmp = bit_str_tmp[:len(bit_str_tmp) - 1]
        state_output = 2
    elif state_output == 2 and state_prev == 0:
        bit_str_tmp = ''
        bit_str_tmp = bit_str_tmp.join(str(i) for i in bit_str)
        state_output = 2
    elif state_prev == 0 and state_output == 0:
        state_output = 2
    string_buf.append(bit_str_tmp)
    return bit_str_tmp

thread = threading.Thread(target=Input)
thread.daemon = True

def send():
    global ser
    str_ = inputEntry.get()
    if len(str_) > 0:
        sending(str_)
    inputEntry.config(validate="none")
    inputEntry.delete(0, END)
    inputEntry.config(validate="key")

def sending(str_):
    global state
    global ser
    bit_str = [int(i) for i in list(str_)]
    state = 2
    attempts = 0
    debugListbox.insert(END,"User input: "+ str_)
    print("user input: " + str_)
    while state == 2:
        state == 0
        bit_list = makeFrame(bit_str)
        while True:
            while listen_to_channel() != 0:
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
            if collision_random() == 1:
                ser.write('c'.encode())
                time.sleep(0.1)
                attempts += 1
                if attempts < attempts_max:
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
    while len(string_buf) > 0:
        str_ = string_buf.pop(0)
        if str_ != '':
            outputListbox.insert(0, str_)
    if send_flag:
        send()
        send_flag = 0
    root.after(100, PortDisplay)


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
    if len(message) == 22:
        message.append(0)
        frame = message
        state = 1
        return frame
    if len(message) > 22 or state == 2:
        frame = message[len(message) - 23:]
        del message[len(message) - 23:]
        state = 2
        return frame


def listen_to_channel():
    return 0 if random.randint(1, 5) == 1 else 1


def collision_random():
    return random.randint(0, 1)


def out_flag():
    global send_flag
    send_flag = 1


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

