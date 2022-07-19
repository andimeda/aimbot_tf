import tensorflow as tf
import tensorflow_hub as hub
import pyautogui
import cv2
import numpy as np
import time
import math
import win32api
import win32con
import win32gui

detector = hub.load("https://tfhub.dev/tensorflow/centernet/resnet50v1_fpn_512x512/1")

while True:
    # find window rectangle
    wind = win32gui.FindWindow(None, 'Counter-Strike: Global Offensive - Direct3D 9')
    rect = win32gui.GetWindowRect(wind)
    region = rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1]

    # get an image of the screen
    original_image = np.array(pyautogui.screenshot(region=region))
    image = np.expand_dims(original_image, 0)
    image_height, image_width = image.shape[1], image.shape[2]

    # detection of enemy player
    result = detector(image)
    result = {key:value.numpy() for key, value in result.items()}
    boxes = result['detection_boxes'][0]
    scores = result['detection_scores'][0]
    classes = result['detection_classes'][0]

    # check every detected object
    detected_boxes = []
    for i, box in enumerate(boxes):
        # choose only person(class:1)
        if classes[i] == 1 and scores[i] >= 0.5:
            ymin, xmin, ymax, xmax = tuple(box)
            if ymin > 0.5 and ymax > 0.8:
                continue
            left, right, top, bottom = int(xmin * image_width), int(xmax * image_width), int(ymin * image_height), int(ymax * image_height)
            detected_boxes.append((left, right, top, bottom))

    print("Detected:", len(detected_boxes))

    # find closest enemy
    if len(detected_boxes) >= 1:
        min = 99999
        at = 0
        centers = []
        for i, box in enumerate(detected_boxes):
            x1, x2, y1, y2 = box
            c_x = ((x2 - x1) / 2) + x1
            c_y = ((y2 - y1) / 2) + y1
            centers.append((c_x, c_y))
            dist = math.sqrt(math.pow(image_width/2 - c_x, 2) + math.pow(image_height/2 - c_y, 2))
            if dist < min:
                min = dist
                at = i
        x = centers[at][0] - image_width/2
        y = centers[at][1] - image_height/2 - (detected_boxes[at][3] - detected_boxes[at][2]) * 0.45

        # move mouse and left click to shoot
        scale = 2   # pixel difference between crosshair and the closest object
        x = int(x * scale)
        y = int(y * scale)
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, x, y, 0, 0)
        time.sleep(0.05)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        time.sleep(0.1)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)

    time.sleep(0.1)
