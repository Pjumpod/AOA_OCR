import cv2
import os
import sys
import glob
from tkinter import filedialog
import numpy as np

filename = filedialog.askopenfilename(title="Choose only 1 file in the folder to be processed", filetypes=[('Picture File', '.jpg .JPG')])
if not isinstance(filename, str):
    filename = filename[0]
f_path = os.path.dirname(filename)
filenames = [F for F in os.listdir(f_path) if F.lower().endswith('jpg')]
# f_mark = r"template/origin_mark.jpg"
# marking = cv2.imread(f_mark,0)
# first file.
for f in filenames:
    f_pic = os.path.join(f_path, f)
    origin = cv2.imread(f_pic)
    rgb_color1 = np.asarray([120, 150, 150])
    rgb_color2 = np.asarray([250, 255, 255])
    gray = cv2.inRange(origin, rgb_color1, rgb_color2)
    buffer2 = gray[500:1200, 300:900]
    gray = cv2.blur(gray, (5,5))
    _, gray = cv2.threshold(gray,150,255,cv2.THRESH_BINARY)
    gray = cv2.convertScaleAbs(gray, alpha=1.0, beta=0.5)
    buffer1 = gray[500:1200, 300:900]
    dst = cv2.cornerHarris(buffer1, 4, 1, 0.02)
    mask = np.zeros_like(buffer1)
    mask[dst>0.01*dst.max()] = 255
    coordinates = np.argwhere(mask)
    coordinates = sorted(coordinates, key=lambda x: (x[0], x[1]))
    c0 = coordinates[0]
    output = buffer1[c0[0]-20:c0[0]+120, c0[1]-20:c0[1]+120]
    lastcorner = output[-1][-1]
    sumcorner = output[0][0] + output[0][-1] + output[-1][0] + output[-1][-1]
    n = 1
    print(output[0][0], output[0][-1], output[-1][0], output[-1][-1])
    while (lastcorner == 0) or (sumcorner != 255):
        c0 = coordinates[n]
        output = buffer1[c0[0]-20:c0[0]+120, c0[1]-20:c0[1]+120]
        n += 1
        print(output[0][0], output[0][-1], output[-1][0], output[-1][-1])
        lastcorner = output[-1][-1]
        sumcorner = output[0][0] + output[0][-1] + output[-1][0] + output[-1][-1]
    output = buffer2[c0[0]-20:c0[0]+120, c0[1]-20:c0[1]+120]
    cv2.imshow("output", output)
    cv2.waitKey(0)