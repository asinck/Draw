#!/usr/bin/env python
#Adam Sinck

#This program should use the webcam to draw on the screen

#this is a list of import commands. If the user doesn't have Tkinter
#or other libraries installed, it will fail gracefully instead of
#crashing.
imports = [
    "from Tkinter import *",
    "import Tkinter as tk",
    "from PIL import Image, ImageTk",
    "import cv2 as cv",
    "import numpy as np"
    # "import tkMessageBox",
    # "from ScrolledText import ScrolledText",
    # "import tkFileDialog as tkf",
    # "import string"
]

#failedPackages will keep a record of the names of the packages that
#failed to import, so that the program can go through the entire list
#of packages that it wants to import. This will allow the program to
#give the user a complete list of packages that they need to install,
#instead of only telling the user one at a time.
failedPackages = ''
for i in imports:
    try:
        exec(i)
    except ImportError as error:
        failedPackages += str(error) + '\n'
#if there were any errors in the imports, tell the user what packages
#didn't import, and exit.
if len(failedPackages) > 0:
    print "Some packages could not be imported:"
    print failedPackages
    exit()



gui_width, gui_height = 500, 500
webcamY, webcamX = 1, 1
x, y, prevx, prevy = 0, 0, 0, 0

webcam = cv.VideoCapture(0)

colors = {
    "r" :  ([  0, 100, 120], [ 10, 255, 255]),
    "g" :  ([ 60, 100,  20], [ 90, 255, 255]),
    "b" :  ([110, 100, 100], [130, 255, 255]),
    "a" :  ([ 90, 100,  50], [110, 255, 255]),
    "p" :  ([130, 100,  50], [150, 255, 175]),
    "i" :  ([140, 100, 100], [160, 255, 255]),
    "y" :  ([ 10, 100,  50], [ 40, 255, 255]),
    "o" :  ([  5, 100,  00], [ 20, 255, 214])
}

colorFilter = colors['r']
lower = np.array(colorFilter[0])
upper = np.array(colorFilter[1])


# Read three images first:
t_minus = cv.cvtColor(webcam.read()[1], cv.COLOR_RGB2GRAY)
t = cv.cvtColor(webcam.read()[1], cv.COLOR_RGB2GRAY)
t_plus = cv.cvtColor(webcam.read()[1], cv.COLOR_RGB2GRAY)

#this will look at the difference between frames
def diffImg(t0, t1, t2):
    d1 = cv.absdiff(t2, t1)
    d2 = cv.absdiff(t1, t0)
    return cv.bitwise_or(d1, d2)

def changeColor(color):
    global colorFilter, upper, lower
    colorFilter = colors[color]
    lower = np.array(colorFilter[0])
    upper = np.array(colorFilter[1])
    print color

def clear():
    global canvas
    canvas.pack_forget()
    canvas = Canvas(outputFrame, width=gui_width, height=gui_height, bg = "#999")
    canvas.pack()

def scale((x, y)):
    #ratio
    #inputX / webcamX = outputY / scaleX
    #inputY / webcamY = outputY / scaleY

    #solving, 
    #outputY =  scaleX * (inputX / webcamX)
    #outputY = scaleY * (inputY / webcamY)

    #note: this might have an issue if the origin (x, y) is in a
    #different corner
    # x increases left to right
    # y increases top to bottom
    # for the webcam, (0, 0) is in the top left corner

    outputX = int(gui_width * ((x*1.0)/(webcamX*1.0)))
    outputY = int(gui_height * ((y*1.0)/(webcamY*1.0)))
    return (outputX, outputY)

#see http://stackoverflow.com/questions/16366857/show-webcam-sequence-tkinter
def show_frame(frame):
    # _, frame = capture.read()
    # frame = cv.flip(frame, 1)
    cvimage = cv.cvtColor(frame, cv.COLOR_BGR2RGBA)
    img = Image.fromarray(cvimage)
    imgtk = ImageTk.PhotoImage(image=img)
    display.imgtk = imgtk
    display.configure(image=imgtk)
    # display.after(10, show_frame)

def draw():
    global x, y, prevx, prevy
    prevx, prevy = x, y
    global t_minus, t, t_plus
    global upper, lower
    # Read next image
    t_minus = t
    t = t_plus
    color = webcam.read()[1]
    
    HSV = cv.cvtColor(color, cv.COLOR_BGR2HSV)
    t_plus = cv.cvtColor(color, cv.COLOR_RGB2GRAY)

    #take a frame
    frame = diffImg(t_minus, t, t_plus)
    frame = cv.GaussianBlur(frame, (3,3), 0)

    #mask = cv.inRange(color, lower, upper)
    mask = cv.inRange(HSV, lower, upper)
    maskedFrame = cv.bitwise_and(color, color, mask = mask)
    colorMotionMask = cv.bitwise_and(frame, frame, mask = mask)
    still = int(cv.mean(colorMotionMask)[0]*100) < 4
    (minVal, maxVal, minLoc, maxLoc) = cv.minMaxLoc(colorMotionMask)
    
    #this is the area of most motion. it's green.
    cv.circle(maskedFrame, maxLoc, 4, (0, 255, 0), 5)
    x, y = scale((maxLoc[0], maxLoc[1]))
    x = gui_width - x
    canvas.create_line(prevx, prevy, x, y, width=3)

    #this is the area of estimated ball position. it's white.
    # cv.circle(maskedFrame, jump, 4, (255, 255, 255), 5)

    show_frame(maskedFrame)

    #another frame
    root.after(50, draw)

def main():
    
    colors = {
        "r" :  ([  0, 100, 120], [ 10, 255, 255]),
        "g" :  ([ 60, 100,  20], [ 90, 255, 255]),
        "b" :  ([110, 100, 100], [130, 255, 255]),
        "a" :  ([ 90, 100,  50], [110, 255, 255]),
        "p" :  ([130, 100,  50], [150, 255, 175]),
        "i" :  ([140, 100, 100], [160, 255, 255]),
        "y" :  ([ 10, 100,  50], [ 40, 255, 255]),
        "o" :  ([  5, 100,  00], [ 20, 255, 214])
    }
    
    colorFilter = colors['r']
    lower = np.array(colorFilter[0])
    upper = np.array(colorFilter[1])
    
    # Read three images first:
    t_minus = cv.cvtColor(webcam.read()[1], cv.COLOR_RGB2GRAY)
    t = cv.cvtColor(webcam.read()[1], cv.COLOR_RGB2GRAY)
    t_plus = cv.cvtColor(webcam.read()[1], cv.COLOR_RGB2GRAY)

    global webcamY, webcamX
    webcamY, webcamX = t.shape[:2]

    draw()

root = Tk()
root.title("Air Etch-A-Sketch")
mainframe = Frame(root)

#webcam on the right
display = Label(mainframe)

#output on the left
outputFrame = Frame(mainframe, width=gui_width, height=gui_height)
canvas = Canvas(outputFrame, width=gui_width, height=gui_height, bg = "#999")


mainframe.pack()

display.pack(side=LEFT)
outputFrame.pack(side=RIGHT)
canvas.pack()

root.bind('<Escape>', lambda e: clear())
root.bind('r', lambda x: changeColor('r'))
root.bind('g', lambda x: changeColor('g'))
root.bind('b', lambda x: changeColor('b'))
root.bind('a', lambda x: changeColor('a'))
root.bind('p', lambda x: changeColor('p'))
root.bind('i', lambda x: changeColor('i'))
root.bind('y', lambda x: changeColor('y'))
root.bind('o', lambda x: changeColor('o'))




root.after(10, main)
root.mainloop()
