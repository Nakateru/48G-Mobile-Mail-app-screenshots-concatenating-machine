"""
for concatenated ske Mail app screenshots
"""

from PIL import Image
import sys
import pyocr.builders
import re
import cv2 as cv
import numpy as np
import glob


def pyocrfun():
    tools = pyocr.get_available_tools()
    if len(tools) == 0:
        print("No OCR tool found")
        sys.exit(1)

    else:
        tool = tools[0]
        # print("Will use tool '%s'" % (tool.get_name()))

        langs = tool.get_available_languages()
        # print("Available languages: %s" % ", ".join(langs))
        lang = langs[3]
        # print("Will use lang '%s'" % (lang))

    return tool, lang


def contrast_brightness_demo(image, c, b):
    h, w, ch = image.shape
    blank = np.zeros([h, w, ch], image.dtype)
    dst = cv.addWeighted(image, c, blank, 1 - c, b)
    # cv.imshow('con-bri-demo', dst)

    return dst


def local_threshold_demo(image):
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    binary = cv.adaptiveThreshold(gray, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 25, 10)
    # binary = cv.adaptiveThreshold(gray, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 25, 10)
    # cv.imshow('binary', binary)
    return binary


def img_to_txt(image):
    datetime = None
    dst = contrast_brightness_demo(image, 0.4, 10)
    dst = local_threshold_demo(dst)

    textImage = Image.fromarray(dst)

    tool, lang = pyocrfun()
    txt = tool.image_to_string(
        textImage,
        lang=lang,
        builder=pyocr.builders.TextBuilder())

    # print(txt)
    # print(type(txt))
    # return txt

    line = re.split('\n', txt)
    for s in range(len(line)):
        ss = re.search(r"2020[/|(\d+)]", line[s])
        if not ss is None:
            # print(line[s])
            datetime = correct_datetime(line[s])
            line[s] = datetime
    # print(line)

    return line, datetime


def get_datetime_from_list(line_list):
    datetime = '0000'
    for s in line_list:
        if not re.search(r'2020[/|(\d+)]', s) is None:
            datetime = s
    datetime = re.sub(r'[\/:*?"<>|]', '', datetime)
    return datetime


def correct_datetime(txt):
    datetime = re.findall(r"(\d+)", txt)
    # print(datetime)
    for i in range(len(datetime)):
        error_len = len(datetime[i])
        if error_len > 4:
            # print(datetime[i])
            err = datetime[i].split('7')
            err.reverse()
            # print(err)
            datetime.remove(datetime[i])
            for x in err:
                datetime.insert(i, x)
    datetime = '/'.join(datetime[0:3]) + ' ' + ':'.join(datetime[3:])
    # print(datetime)
    return datetime


def save_concat_img(line_list, concat_file_list, path):
    concat_img_list = []

    first_img = cv.imread(concat_file_list[0])
    width = first_img.shape[1]
    concat_img_list.append(first_img)

    for i in concat_file_list[1:]:
        ssrc = cv.imread(i)
        src = cv.resize(ssrc, (width, ssrc.shape[0]))
        concat_img_list.append(src)

    imgv = cv.vconcat(concat_img_list)
    datetime = get_datetime_from_list(line_list)
    cv.imwrite(path + datetime + '.jpg', imgv)
    concat_img_list.clear()

    print('Saved ' + path + datetime + '.jpg')


def save_txt(line_list, path):
    datetime = get_datetime_from_list(line_list)
    with open(path + datetime + '.txt', "a", encoding='UTF-8') as f:
        for i in line_list:
            f.write(i + '\n')
    print('Saved ' + path + datetime + '.txt')


if __name__ == '__main__':
    print('48G Mobile Mail app screenshots concatenating machine')
    print('Author  :  Nakateru (2020.09.11)')
    img_dir = './ske Mail app screenshots/'
    saved_img_dir = './img/'
    saved_txt_dir = './txt/'

    line_list = []
    concat_file_list = []

    file_list = glob.glob(img_dir + '*.jpg')
    file_list.sort()
    # print(file_list)

    for file in file_list:
        # print(file)
        src = cv.imread(file)
        line, datetime = img_to_txt(src)
        # print(line)

        if datetime is not None:
            if not len(line_list) == 0:
                # print(line_list)
                # print(concat_file_list)
                save_concat_img(line_list, concat_file_list, saved_img_dir)
                save_txt(line_list, saved_txt_dir)

            line_list.clear()
            line_list = line

            concat_file_list.clear()
            concat_file_list.append(file)
        else:
            line_list = line_list + line
            concat_file_list.append(file)

    # print(line_list)
    # print(concat_file_list)
    save_concat_img(line_list, concat_file_list, saved_img_dir)
    save_txt(line_list, saved_txt_dir)

    print('Done')
    # cv.waitKey(0)
    # cv.destroyAllWindows()
