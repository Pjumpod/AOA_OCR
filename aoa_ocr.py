import cv2
import os
from tkinter import filedialog, Tk, Button
import numpy as np
import sys


def find_roi(origin):
    sumcorner = 0
    lastcorner = 0
    rgb_color1 = np.asarray([120, 150, 150])
    rgb_color2 = np.asarray([250, 255, 255])
    gray = cv2.inRange(origin, rgb_color1, rgb_color2)
    buffer2 = gray[500:1200, 300:1200]
    gray = cv2.blur(gray, (5,5))
    _, gray = cv2.threshold(gray,150,255,cv2.THRESH_BINARY)
    gray = cv2.convertScaleAbs(gray, alpha=1.0, beta=0.5)
    buffer1 = gray[500:1200, 300:1200]
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
    # print(output[0][0], output[0][-1], output[-1][0], output[-1][-1])
    while (lastcorner == 0) or (sumcorner != 255):
        sumcorner = 0
        c0 = coordinates[n]
        output = buffer1[c0[0]-20:c0[0]+120, c0[1]-20:c0[1]+120]
        n += 1
        # print(output[0][0], output[0][-1], output[-1][0], output[-1][-1])
        lastcorner = output[-1][-1]
        sumcorner = output[0][0] + output[0][-1] + output[-1][0] + output[-1][-1]
    # Capture full area
    crosscheck = [1000001]
    n = 0
    while sum(crosscheck) > 0:
        output = buffer2[c0[0] + 10:c0[0]+90, c0[1] + n :c0[1]+ 80 + n]
        crosscheck = []
        try:
            for line in output:
                crosscheck.append(int(line[-1]))
        except:
            n = 0
            break
        crosscheck = crosscheck[3:len(crosscheck) - 3]
        output = buffer2[c0[0] + 10:c0[0]+90, c0[1] + n :c0[1]+ 80 + n]
        n += 1
    return output


def find_char(img, model_folder: str):
    model_files = [F for F in os.listdir(model_folder) if F.lower().endswith('jpg')]
    value_map = np.array([])
    code_map = np.array([])
    for model_f in model_files:
        model_fullname = os.path.join(model_folder, model_f)
        model_type = model_f.split("_")[0]
        model_pic = cv2.imread(model_fullname, 0)
        res_num = cv2.matchTemplate(img, model_pic, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res_num)
        value_map = np.append(value_map, max_val)
        code_map = np.append(code_map, model_type)
    if len(value_map) > 0:
        # print(value_map)
        # print(code_map)
        max_value = value_map.max()
        positions = np.where(value_map == max_value)[0]
        position = positions[0]
        charList = [str(element) for element in code_map]
        char = charList[position]
        return char
    else:
        return "N"

def openfiles():
    btn.configure(state="disabled")
    filename = filedialog.askopenfilename(title="Choose only 1 file in the folder to be processed", filetypes=[('Picture File', '.jpg .JPG')])
    if not isinstance(filename, str):
        filename = filename[0]
    f_path = os.path.dirname(filename)
    filenames = [F for F in os.listdir(f_path) if F.lower().endswith('jpg')]
    if getattr(sys, 'frozen', False):
        template_folder = os.path.join(sys._MEIPASS, r"model/")
    else:
        template_folder = r"model/"
    # f_mark = r"template/origin_mark.jpg"
    # marking = cv2.imread(f_mark,0)
    # first file.
    for f in filenames:
        f_pic = os.path.join(f_path, f)
        origin = cv2.imread(f_pic)
        output = find_roi(origin)
        # cv2.imshow("output", output)
        # cv2.waitKey(0)
        char1_img = output[41:80, 0:40]
        char2_img = output[0:40, 0:40]
        char3_img = output[41:80, 41:80]
        char4_img = output[0:40, 41:80]
        ans = ""
        c0 = find_char(char1_img, template_folder)
        c1 = find_char(char2_img, template_folder)
        c2 = find_char(char3_img, template_folder)
        c3 = find_char(char4_img, template_folder)
        ans = c0 + c1 + c2 + c3
        if "N" in ans:
            error_file = os.path.join(f_path, ans + ".jpg")
            if os.path.exists(error_file):
                os.remove(error_file)
            cv2.imwrite(error_file, output)
        # cv2.imshow("output", output)
        # print(ans)
        # cv2.waitKey(0)
        cv2.destroyAllWindows()
        os.rename(f_pic, os.path.join(f_path, ans + ".jpg"))
    btn.configure(state="normal")


# Main
root = Tk()
root.geometry('100x100')
btn = Button(root, text = 'Browse', pady=30, command=openfiles)
btn.pack(side = 'top')
root.mainloop()