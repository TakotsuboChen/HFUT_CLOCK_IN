import cv2
import pytz
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import datetime


def makepic(name: str, phone: str):
    phone = phone[:3] + "****" + phone[-4:]

    # 安康
    img = cv2.imread("akm.jpg")
    im1 = Image.new("RGB", (500, 60), (254, 254, 254))
    dr1 = ImageDraw.Draw(im1)
    dr1.text((0, 0), datetime.datetime.now(
            tz=pytz.timezone('Asia/Shanghai')).strftime("%Y-%m-%d %H:%M:%S"), (0, 0, 0),
             ImageFont.truetype("Medium.otf", 48))
    img[375: 435, 218: 718, :] = cv2.resize(np.array(im1), (500, 60))

    im2 = Image.new("RGB", (90, 40), (254, 254, 254))
    dr2 = ImageDraw.Draw(im2)
    dr2.text((0, 0), name, (0, 0, 0), ImageFont.truetype("Medium.otf", 30))
    img[280: 320, 80: 170, :] = cv2.resize(np.array(im2), (90, 40))
    cv2.imwrite("akm.jpg", img)

    # 行程
    img = cv2.imread("xck.jpg")
    im1 = Image.new("RGB", (176, 23), (254, 254, 254))
    dr1 = ImageDraw.Draw(im1)
    dr1.text((0, 0), datetime.datetime.now(
            tz=pytz.timezone('Asia/Shanghai')).strftime("%Y.%m.%d %H:%M:%S"), (120, 120, 120),
             ImageFont.truetype("Medium.otf", 18))
    img[235: 258, 135: 311, :] = cv2.resize(np.array(im1), (176, 23))

    im2 = Image.new("RGB", (200, 30), (254, 254, 254))
    dr2 = ImageDraw.Draw(im2)
    dr2.text((0, 0), phone + "的动态行程卡", (0, 0, 0), ImageFont.truetype("Medium.otf", 16))
    img[200: 230, 85: 285, :] = cv2.resize(np.array(im2), (200, 30))
    cv2.imwrite("xck.jpg", img)