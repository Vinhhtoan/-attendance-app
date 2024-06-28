import tkinter

import cv2
import face_recognition
import csv
import os
import numpy as np
from datetime import datetime, timedelta
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
from tktimepicker import *
from numpy.core.defchararray import upper

imagePath = ""
dsPath = ""
subject = ""
images = []
classNames = []
startTime = datetime.now()


def Get_Images():
    if classNames != []: return
    myList = os.listdir(imagePath)
    print(myList)
    for cl in myList:
        print(cl)
        curimg = cv2.imread(f"{imagePath}/{cl}")
        images.append(curimg)
        classNames.append(os.path.splitext(cl)[0])
    print(len(images))
    print(classNames)


# reset
def reset():
    with open(dsPath, mode='w') as wr:
        for i in range(len(classNames)):
            wr.writelines(f"\n{classNames[i]},vang")
    wr.close()


# ma hoa
def Mahoa(images):
    Get_Images()
    encodeList = []
    for anh in images:
        anh = cv2.cvtColor(anh, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(anh)[0]
        encodeList.append(encode)
    return encodeList


def danhsach(name):
    now = datetime.now()
    if now > startTime + timedelta(minutes=10): return
    with open(dsPath, mode='r+') as f:
        myData = csv.reader(f, delimiter='\n')
        nameList = []
        isAbsence = []
        checkTime = []
        for line in myData:
            if len(line) == 0: continue
            entry = line[0].split(',')[0]
            nameList.append(entry.upper())
            if line[0].split(',')[1] == "co mat":
                isAbsence.append(0)
                checkTime.append(line[0].split(',')[2])
            else:
                isAbsence.append(1)
                checkTime.append(-1)

        f.close()

    if name in nameList:
        index = nameList.index(name)
        isAbsence[index] = 0
        with open(dsPath, mode='w') as wr:
            for i in range(len(nameList)):
                if i == index and checkTime[index] == -1:
                    wr.writelines(f"\n{nameList[i]},co mat,{datetime.now().strftime('%H:%M:%S')}")
                elif checkTime[i] != -1:
                    wr.writelines(f"\n{nameList[i]},co mat,{checkTime[i]}")
                else:
                    wr.writelines(f"\n{nameList[i]},vang")
        wr.close()


def NhanDien():
    if selection.get() == '': return
    global imagePath, dsPath, subject
    subject = selection.get()
    imagePath = selection.get() + "/StudentImage"
    dsPath = selection.get() + "/danhsach.csv"
    os.chdir("D:\pythonProject2")
    encodeListKnow = Mahoa(images)
    reset()
    print("Ma hoa thanh cong")
    print(len(encodeListKnow))
    cap1 = cv2.VideoCapture(0)
    while True:

        ret, frame = cap1.read()
        # hien tai mon hoc
        cv2.putText(frame,"Mon hoc:" + subject, (10, 30), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 139), 1)
        #
        frameS = cv2.resize(frame, (0, 0), None, fx=0.5, fy=0.5)
        frameS = cv2.cvtColor(frameS, cv2.COLOR_BGR2RGB)

        facecur = face_recognition.face_locations(frameS)  # lay tung khuon mat va vi tri khuon mat hien tai
        encodecur = face_recognition.face_encodings(frameS)
        for encodeFace, faceLoc in zip(encodecur, facecur):
            matches = face_recognition.compare_faces(encodeListKnow, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnow, encodeFace)
            matchIndex = np.argmin(faceDis)
            print(faceDis)
            if faceDis[matchIndex] < 0.50:
                name = classNames[matchIndex].upper()
                danhsach(name)
            else:
                name = "unknow"

            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 2, x2 * 2, y2 * 2, x1 * 2
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, name, (x2, y2), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 139), 1)
        cv2.imshow("Nhan dien khuon mat", frame)
        k = cv2.waitKey(1)
        if k % 256 == 27:
            break
    cap1.release()
    cv2.destroyAllWindows()


def ChupHinh():
    cap = cv2.VideoCapture(0)
    cv2.namedWindow("Screen shot")
    img_counter = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            print('Failed')
            break
        cv2.imshow("test", frame)

        k = cv2.waitKey(1)

        if k % 256 == 27:
            print("Escape hit, closing app")
            break
        elif k % 256 == 32:
            img_name = entry.get() + ".png"
            os.chdir(imagePath)
            cv2.imwrite(img_name, frame)
    cap.release()
    cv2.destroyAllWindows()


# time piacker
def updateTime(time):
    time_lbl.configure(text="Start Time: {}:{} {}".format(*time))


def get_time():
    top = tkinter.Toplevel()

    time_picker = AnalogPicker(top, type=constants.HOURS12)
    time_picker.pack(expand=True, fill="both")

    theme = AnalogThemes(time_picker)
    theme.setDracula()
    ok_btn = tkinter.Button(top, text="ok", command=lambda: updateTime(time_picker.time()))
    ok_btn.pack()


# Giao dien
win = Tk()
win.title('Face Check')
win.geometry('400x350')
# win['bg']='gray'
win.attributes('-topmost', True)

img_import = (Image.open(r'th.jpg'))
resize = img_import.resize((200, 200), Image.ANTIALIAS)
img = ImageTk.PhotoImage(resize)

lb1 = Label(win, text='', font=('Times New Roman', 12), image=img)
lb1.place(x=10, y=40)

lb = Label(win, text='Name: ', font=('Times New Roman', 12))
lb.place(x=40, y=310)

entry = Entry(win, width=14, font=('Times New Roman', 12))
entry.place(x=90, y=310)

lb = Label(win, text='Class: ', font=('Times New Roman', 12))
lb.place(x=210, y=40)

selection = ttk.Combobox(win, width=16);
selection['values'] = ('KHDL', 'XLTHS', 'XXTK')
selection.grid(column=1, row=7)
selection.place(x=260, y=40)

# time picker
time_lbl = tkinter.Label(win, text="Start time:")
time_lbl.place(x=220, y=150)
time_btn = tkinter.Button(win, text="Get Time", command=get_time)
time_btn.place(x=280, y=175)

bt1 = Button(win, text="Start", width=11, command=NhanDien)
bt1.place(x=70, y=250)

bt2 = Button(win, text="Input face", width=10, command=ChupHinh)
bt2.place(x=240, y=310)

win.mainloop()
