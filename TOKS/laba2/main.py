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
bufSend = ""
getBuf = ""



def outFlag():
    global sendFlag #флаг запроса на передачу
    sendFlag =1

def PortDisplay():
    global sendFlag
    global stringBuffer
    while len(stringBuffer) > 0:
        str = stringBuffer.pop(0)
        outputListbox.insert(END, str)
    if sendFlag:
        bitStuffing()
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

def debitStuffing():
    global ser
    global start_flag
    global stringBuffer
    global getBuf
    while 1: #ждем прием строки
        len_ = 0 #длина принятой строки
        while len_ < 1: #пока 0 попытка чтения из порта
            try:
                str_ = ""
                bitStuffing = ser.readline()
                bitStuffing = bitStuffing.decode()
                if len(getBuf) < 6:
                    tmp = getBuf
                    tmp_len = len(getBuf)
                else:
                    tmp = getBuf[len(getBuf) - 6:]
                    tmp_len = len(tmp)
                tmp += bitStuffing
                bitStuffing = tmp.replace("0001010", "000101")
                str_ = bitStuffing[tmp_len:]
                getBuf += str_
                len_ = len(str_)
            except Exception:
                if ser is None:
                    break
        stringBuffer.append(str_)
        time.sleep(1)

tr_in = threading.Thread(target = debitStuffing) #поток приема
tr_in.daemon = True

def bitStuffing():
    global ser
    global bufSend
    userInput = inputEntry.get()
    tmp = ""
    tmp_len = 6
    isValid = True
    for symbol in userInput:
        if symbol != '0' and symbol != '1':
            isValid = False
            debugListbox.insert(END, "Invalid input!")
            return
        if isValid:
            if len(userInput) > 0:
                if len(bufSend) < 6:
                    tmp = bufSend
                    tmp_len = len(bufSend)
                else:
                    tmp = bufSend[len(bufSend) - 6:]
                tmp += userInput
                bufSend += userInput
                debugListbox.insert(END, "Buffer:" + bufSend)
                if tmp.find("000101") == -1:
                    ser.write(userInput.encode())
                    debugListbox.insert(END, "Input:" + userInput)
                else:
                    bitStuffing = tmp.replace("000101", "0001010")
                    bitStuffing = bitStuffing[tmp_len:]
                    ser.write(bitStuffing.encode())
                    debugListbox.insert(END, "Input:" + userInput)
                    bitStuffing = tmp.replace("000101", "000101[0]")
                    bitStuffing = bitStuffing[tmp_len:]
                    debugListbox.insert(END, "After bit-stuffing:" + bitStuffing)
                break

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

inputEntry = Entry(input, width=72)
inputEntry.pack()

debugListbox = Listbox(debug, width=70, height=5)
debugListbox.insert(END,"FLAG: 00010111")
debugListbox.pack()

speed = ttk.Combobox(debug, values=[2400,4800,9600,19200,38400,57600,115200])
speed.pack(fill= X)

buttonChoose = ttk.Button(debug, text ="confirm", command = Choose)
buttonChoose.pack()

sendButton = Button(debug, text ="send", command = outFlag)
sendButton.pack(side=BOTTOM)

root.after(10,PortDisplay)
root.mainloop()
