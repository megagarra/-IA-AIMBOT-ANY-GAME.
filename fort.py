# Importar bibliotecas
import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import pyautogui
import win32api, win32con, win32gui
import cv2
import math
import time

# Carregar detector de objetos
detector = hub.load("https://tfhub.dev/tensorflow/centernet/resnet50v1_fpn_512x512/1")
size_scale = 3

while True:
    # Capturar imagem da tela
    ori_img = np.array(pyautogui.screenshot())
    ori_img = cv2.resize(ori_img, (ori_img.shape[1] // size_scale, ori_img.shape[0] // size_scale))
    image = np.expand_dims(ori_img, 0)
    img_w, img_h = image.shape[2], image.shape[1]

    # Detectar objetos
    result = detector(image)
    result = {key:value.numpy() for key,value in result.items()}
    boxes = result['detection_boxes'][0]
    scores = result['detection_scores'][0]
    classes = result['detection_classes'][0]
    human_classes = [1, 17, 18]

    # Check every detected object
    detected_boxes = []
    detected_scores = []
    for i, box in enumerate(boxes):
        # Choose only person(class:1) or animal classes (class: 17 and 18)
        if classes[i] in human_classes and scores[i] >= 0.5:
            ymin, xmin, ymax, xmax = tuple(box)
            # Adjust the following condition for Fortnite
            left, right, top, bottom = int(xmin * img_w), int(xmax * img_w), int(ymin * img_h), int(ymax * img_h)
            detected_boxes.append((left, right, top, bottom))
            detected_scores.append(scores[i])
            #cv2.rectangle(ori_img, (left, top), (right, bottom), (255, 255, 0), 2)

    if len(detected_boxes) == 0:
        print("No humans or animals detected")
        continue

    # Check Closest
    min = 99999
    at = 0
    centers = []
    for i, box in enumerate(detected_boxes):
        x1, x2, y1, y2 = box
        c_x = ((x2 - x1) / 2) + x1
        c_y = ((y2 - y1) / 2) + y1
        centers.append((c_x, c_y))
        dist = math.sqrt(math.pow(img_w/2 - c_x, 2) + math.pow(img_h/2 - c_y, 2))
        if dist < min:
            min = dist
            at = i

    # Pixel difference between crosshair(center) and the closest object
    x = centers[at][0] - img_w/2
    y = centers[at][1] - img_h/2 - (detected_boxes[at][3] - detected_boxes[at][2]) * 0.45


    # Check if closest object is in the crosshair
    if abs(x) < 10 and abs(y) < 10:
        # Move mouse and shoot
        # Move mouse and shoot
        scale = 1.7 * size_scale
        x = int(x * scale)
        y = int(y * scale)
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, x, y, 0, 0)
        time.sleep(0.01)
        y = int(y) # Converte "y" em inteiro
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        time.sleep(0.1)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)

    # Check if human is within crosshair
    crosshair_x = img_w/2
    crosshair_y = img_h/2
    crosshair_radius = 50
    human_x1, human_x2, human_y1, human_y2 = detected_boxes[at]
    human_center_x = (human_x1 + human_x2) / 2
    human_center_y = (human_y1 + human_y2) / 2
    distance = math.sqrt((human_center_x - crosshair_x)**2 + (human_center_y - crosshair_y)**2)
    if distance <= crosshair_radius:
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, int(x), int(y), 0, 0)
        time.sleep(0.1)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, int(x), int(y), 0, 0)

    ori_img = cv2.cvtColor(ori_img, cv2.COLOR_BGR2RGB)
    cv2.imshow("ori_img", ori_img)
    cv2.waitKey(1)

    time.sleep(0.1)

