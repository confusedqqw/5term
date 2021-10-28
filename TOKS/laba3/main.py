import threading
import time
import tkinter
from random import randint
from tkinter import *
from tkinter import ttk
from tkinter.messagebox import showinfo
import serial

string_buf = []
send_flag = 0
start_flag = 0
fl1=0
ser = None
pickFlag = 0
string_send_buf = ""
double_error_occurred_flag = 0




def outFlag():
    global send_flag #флаг запроса на передачу
    send_flag =1

def PortDisplay():
    global send_flag
    global double_error_occurred_flag
    while len(string_buf) > 0:
        str_ = string_buf.pop(0)
        str_ = linking_frames(str_)
        if double_error_occurred_flag == 0:
            outputListbox.insert(0, str_)
        double_error_occurred_flag = 0
    if send_flag:
        send()
        send_flag = 0
    root.after(100,PortDisplay)#бесконечный цикл

def Connect1():
    global start_flag
    global ser
    global tr_in
    try:
        ser = serial.Serial('COM2', int(speed.get()), timeout=1)
    except Exception:
        if ser is None:
          Error("port is closed")
    start_flag = 1

def Connect2():
    global start_flag
    global ser
    global tr_in
    try:
        ser = serial.Serial('COM3', int(speed.get()), timeout=1)
    except Exception:
        if ser is None:
            Error("port is closed")
    start_flag = 1

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

def get_input():
    global ser
    global start_flag
    global string_buf
    global string_send_buf
    while 1:
        len_ = 0
        while len_ < 1:
            str_ = ser.readline().decode()
            len_ = len(str_)
        string_buf.append(str_)
        time.sleep(1)


tr_in = threading.Thread(target = get_input) #поток приема
tr_in.daemon = True

def send():
    global ser
    global string_send_buf
    userInput = inputEntry.get()
    isValid = True
    for symbol in userInput:
        if symbol != '0' and symbol != '1':
            isValid = False
            debugListbox.insert(END, "Invalid input!")
            return
        if isValid:
            if len(userInput) > 0:
                fin_str = splitting_into_frames(userInput)
                ser.write(fin_str.encode())
            break

def bit_insert(msg):
    i = 0
    n = 1
    while n < 6:
        msg.insert(i, 0)
        i = 2 ** n - 1
        n += 1
    return msg


def splitting_into_frames(str_):
    bit_list_all = list([int(i) for i in str_])
    debugListbox.insert(END, "typed:" + str_)
    fin_str = ""
    while len(bit_list_all) > 0:
        x = 0
        if len(bit_list_all) < 22:
            bit_list = list(bit_list_all)
            del bit_list_all[:]
            if bit_list[0] == 0:
                x ^= 1
            while len(bit_list) < 22:
                bit_list.insert(0, x ^ 0)
        else:
            bit_list = list(bit_list_all[:22])
            del bit_list_all[:22]
            if bit_list[0] == 0:
                x ^= 1
        bit_list.insert(0, x)
        bit_list = bit_insert(bit_list)
        bit_list = hamming_code(bit_list)
        bit_str = "".join(str(i) for i in bit_list)
        debugListbox.insert(END, "hamming:" + bit_str)
        bit_list = random_corruption(bit_list)
        fin_str += "".join(str(i) for i in bit_list)
    return fin_str


def hamming_code(bit_list):
    n = 0
    while 2 ** n < len(bit_list):
        start = 2 ** n
        i = start - 1
        bit_sum = 0
        skip = 0
        skip_counter = 0
        while i < len(bit_list):
            if skip != 1:
                bit_sum ^= bit_list[i]
            i += 1
            skip_counter += 1
            if skip_counter == start:
                skip_counter = 0
                skip ^= 1
        n += 1
        bit_list[start - 1] = bit_sum
    i = 0
    bit_sum = 0
    while i < len(bit_list):
        bit_sum ^= bit_list[i]
        i += 1
    bit_list.append(bit_sum)
    return bit_list


def linking_frames(str_):
    bit_list_all = list([int(i) for i in str_])
    debugListbox.insert(END, "received:" + str_)
    fin_str = ""
    x = 0
    while len(bit_list_all) > 0:
        bit_list = list(bit_list_all[:29])
        del bit_list_all[:29]
        bit_list = hamming_check(bit_list)
        x = bit_list.pop(0)
        while x == bit_list[0]:
            bit_list.pop(0)
        fin_str += "".join(str(i) for i in bit_list)
    return fin_str


def hamming_check(bit_str):
    bit_list = [int(i) for i in bit_str]
    n = 0
    corrupt_bit_pos = 0
    corrupt_bit_list = list()
    while 2 ** n < len(bit_list) - 1:
        start = 2 ** n
        i = start - 1
        bit_sum = 0
        skip = 0
        skip_counter = 0
        while i < len(bit_list) - 1:
            if skip != 1:
                bit_sum ^= bit_list[i]
            i += 1
            skip_counter += 1
            if skip_counter == start:
                skip_counter = 0
                skip ^= 1
        if bit_sum == 1:
            corrupt_bit_pos += 2 ** n
        corrupt_bit_list.insert(0, bit_sum)
        n += 1
    i = 0
    parity_bit = 0
    while i < len(bit_list):
        parity_bit ^= bit_list[i]
        i += 1
    if (parity_bit == 0) and (corrupt_bit_pos == 0):
        return hamming_decode(bit_list, corrupt_bit_pos, 1, corrupt_bit_list)
    if (parity_bit == 1) and (corrupt_bit_pos != 0):
        return hamming_decode(bit_list, corrupt_bit_pos, 0, corrupt_bit_list)
    if (parity_bit == 0) and (corrupt_bit_pos != 0):
        return hamming_decode(bit_list, -1, 1, corrupt_bit_list)
    if (parity_bit == 1) and (corrupt_bit_pos == 0):
        return hamming_decode(bit_list, len(bit_list), 0, corrupt_bit_list)


def hamming_decode(bit_list, corrupt_bit_pos, ctrl, corrupt_bit_list):
    global double_error_occurred_flag
    bit_str = [str(c) for c in bit_list]
    bit_pos_str = [str(c) for c in corrupt_bit_list]
    if corrupt_bit_pos == -1:
        debugListbox.insert(END, "double error occurred")
        double_error_occurred_flag = 1
        for i in bit_pos_str:
            i = 0
    elif ctrl != 1:
        if corrupt_bit_pos == len(bit_list):
            corrupt_bit_list = [1, 0, 1, 0, 0]
            bit_pos_str = [str(c) for c in corrupt_bit_list]
        bit_str[corrupt_bit_pos - 1] = "{" + str(bit_str[corrupt_bit_pos - 1]) + "}"
    n = 0
    while (2 ** n - 1) < len(bit_str):
        bit_str[2 ** n - 1] = "[" + str(bit_str[2 ** n - 1]) + "]"
        n += 1
    bit_str[len(bit_str) - 1] = "[" + str(bit_str[len(bit_str) - 1]) + "]"
    bit_str = "".join(bit_str)
    bit_pos_str = "".join(bit_pos_str)
    debugListbox.insert(END, "check: " + bit_str + ":" + bit_pos_str)
    if ctrl != 1:
        bit_list[corrupt_bit_pos - 1] ^= 1
    n = 0
    while (2 ** n - 1 - n) < len(bit_list):
        bit_list.pop(2 ** n - 1 - n)
        n += 1
    bit_list.pop()
    return bit_list


def random_corruption(bit_list):
    if randint(0, 1) == 1:
        if randint(0, 4) < 2:
            x = randint(9, len(bit_list) - 1)
            bit_list[x] ^= 1
            y = randint(0, 9)
            bit_list[y] ^= 1
            bit_str = [str(c) for c in bit_list]
            bit_str[x] = "{" + str(bit_str[x]) + "}"
            bit_str[y] = "{" + str(bit_str[y]) + "}"
            debugListbox.insert(END, "Error(s) generated:")
            debugListbox.insert(END, "".join(bit_str))
        else:
            x = randint(0, len(bit_list) - 1)
            bit_list[x] ^= 1
            bit_str = [str(c) for c in bit_list]
            bit_str[x] = "{" + str(bit_str[x]) + "}"
            debugListbox.insert(END, "Error(s) generated:")
            debugListbox.insert(END, "".join(bit_str))
    return bit_list



root = Tk() #создаем форму
root.title("laba3")
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

inputEntry = Entry(input, width=72)
inputEntry.pack()

debugListbox = Listbox(debug, width=70, height=5)
debugListbox.insert(END)
debugListbox.pack()

speed = ttk.Combobox(debug, values=[2400,4800,9600,19200,38400,57600,115200])
speed.pack(fill= X)

buttonChoose = ttk.Button(debug, text ="confirm", command = Choose)
buttonChoose.pack()

sendButton = Button(debug, text ="send", command = outFlag)
sendButton.pack(side=BOTTOM)

root.after(10,PortDisplay)
root.mainloop()