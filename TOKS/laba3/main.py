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
doubleError = 0
ZERO_STR = "0000000000000000000000"
flag = 0



def outFlag():
    global send_flag #флаг запроса на передачу
    send_flag =1

def PortDisplay():
    global send_flag
    global doubleError
    while len(string_buf) > 0:
        str_ = string_buf.pop(0)
        str_ = linkFrame(str_)
        if doubleError == 0:
            outputListbox.insert(0, str_)
        doubleError = 0
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

def Input():
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


tr_in = threading.Thread(target = Input) #поток приема
tr_in.daemon = True

def send():
    global ser
    global flag
    global string_send_buf
    userInput = inputEntry.get()
    isValid = True
    if len(userInput) > 0:
        fin_str = makeFrame(userInput)
        if flag == 1:
            fin_str+="0"
            flag = 0
        ser.write(fin_str.encode())
    inputEntry.config(validate="none")
    inputEntry.delete(0, END)
    inputEntry.config(validate="key")



def bitInsert(str_):
    i = 0
    n = 1
    while n < 6:
        str_.insert(i, 0)
        i = 2 ** n - 1
        n += 1
    return str_


def makeFrame(str_):
    global flag
    list_all = list([int(i) for i in str_])
    debugListbox.insert(END, "User input:" + str_)
    result = ""
    while len(list_all) > 0:
        x = 0
        if len(list_all) < 23:
            bit_list = list(list_all)
            del list_all[:]
            if bit_list[len(bit_list) - 1] == 0:
                x ^= 1
            while len(bit_list) < 23:
                bit_list.append(x ^ 0)
            flag = 1
        else:
            bit_list = list(list_all[:23])
            del list_all[:23]
        bit_list = bitInsert(bit_list)
        bit_list = makeCode(bit_list)
        bit_str = "".join(str(i) for i in bit_list)
        debugListbox.insert(END, "Hamming code:" + bit_str)
        bit_list = randomError(bit_list)
        result += "".join(str(i) for i in bit_list)
    return result

def linkFrame(str_):
    list_all = list([int(i) for i in str_])
    debugListbox.insert(END, "Received:" + str_)
    result = ""
    while len(list_all) > 0:
        bit_list = list(list_all[:29])
        del list_all[:29]
        bit_list = hammingCodeCheck(bit_list)
        if len(list_all) == 1:
            del list_all[:]
            x = bit_list.pop()
            while x == bit_list[len(bit_list) - 1]:
                bit_list.pop()
        result += "".join(str(i) for i in bit_list)
    return result

def makeCode(bit_list):
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


def hammingCodeCheck(bit_str):
    bit_list = [int(i) for i in bit_str]
    n = 0
    error_bit_pos = 0
    error_bit_list = list()
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
            error_bit_pos += 2 ** n
        error_bit_list.insert(0, bit_sum)
        n += 1
    i = 0
    parity_bit = 0
    while i < len(bit_list):
        parity_bit ^= bit_list[i]
        i += 1
    if (parity_bit == 0) and (error_bit_pos == 0):
        return makeDecode(bit_list, error_bit_pos, 1, error_bit_list)
    if (parity_bit == 1) and (error_bit_pos != 0):
        return makeDecode(bit_list, error_bit_pos, 0, error_bit_list)
    if (parity_bit == 0) and (error_bit_pos != 0):
        return makeDecode(bit_list, -1, 1, error_bit_list)
    if (parity_bit == 1) and (error_bit_pos == 0):
        return makeDecode(bit_list, len(bit_list), 0, error_bit_list)


def makeDecode(bit_list, error_bits_pos, ctrl, error_bit_list):
    global doubleError
    bit_str = [str(c) for c in bit_list]
    bit_pos_str = [str(c) for c in error_bit_list]
    if error_bits_pos == -1:
        debugListbox.insert(END, "Double error!")
        doubleError = 1
        for i in bit_pos_str:
            i = 0
    elif ctrl != 1:
        if error_bits_pos == len(bit_list):
            error_bit_list = [1, 0, 1, 0, 0]
            bit_pos_str = [str(c) for c in error_bit_list]
        bit_str[error_bits_pos - 1] = "{" + str(bit_str[error_bits_pos - 1]) + "}"
    n = 0
    while (2 ** n - 1) < len(bit_str):
        bit_str[2 ** n - 1] = "[" + str(bit_str[2 ** n - 1]) + "]"
        n += 1
    bit_str[len(bit_str) - 1] = "[" + str(bit_str[len(bit_str) - 1]) + "]"
    bit_str = "".join(bit_str)
    bit_pos_str = "".join(bit_pos_str)
    debugListbox.insert(END,bit_str + ":" + bit_pos_str)
    if ctrl != 1:
        bit_list[error_bits_pos - 1] ^= 1
    n = 0
    while (2 ** n - 1 - n) < len(bit_list):
        bit_list.pop(2 ** n - 1 - n)
        n += 1
    bit_list.pop()
    return bit_list


def randomError(bit_list):
    if randint(0, 1) == 1:
        if randint(0, 4) < 2:
            x = randint(9, len(bit_list) - 1)
            bit_list[x] ^= 1
            y = randint(0, 9)
            bit_list[y] ^= 1
            bit_str = [str(c) for c in bit_list]
            bit_str[x] = "{" + str(bit_str[x]) + "}"
            bit_str[y] = "{" + str(bit_str[y]) + "}"
            debugListbox.insert(END, "Error occurred:")
            debugListbox.insert(END, "".join(bit_str))
        else:
            x = randint(0, len(bit_list) - 1)
            bit_list[x] ^= 1
            bit_str = [str(c) for c in bit_list]
            bit_str[x] = "{" + str(bit_str[x]) + "}"
            debugListbox.insert(END, "Error occurred:")
            debugListbox.insert(END, "".join(bit_str))
    return bit_list


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

validation = root.register(inputValidation)
inputEntry = Entry(input, width=72, validate="key", validatecommand=(validation, "%S"))
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

