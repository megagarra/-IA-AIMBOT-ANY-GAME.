import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import pyautogui
import win32api, win32con, win32gui
import cv2
import math
import time

# Carregar detector de objetos
detector = hub.load("https://tfhub.dev/tensorflow/ssd_mobilenet_v2/2")
size_scale = 2

# Adicionar variável global para armazenar as coordenadas do clique
clicked_coordinates = []

def mouse_click(event, x, y, flags, param):
    global clicked_coordinates
    if event == cv2.EVENT_LBUTTONDOWN:
        clicked_coordinates = [x, y]

# Adicionar função de callback do mouse
cv2.namedWindow("ori_img")
cv2.setMouseCallback("ori_img", mouse_click)

def mouse_smooth_move(dx, dy, duration=0.1, steps=10):
    for i in range(steps):
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(dx / steps), int(dy / steps), 0, 0)
        time.sleep(duration / steps)

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
    human_classes = [1, 17, 18]  # Atualize essa lista para incluir as classes específicas das partes do corpo humano

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
            cv2.rectangle(ori_img, (left, top), (right, bottom), (255, 255, 0), 2)

# Check if no humans or animals are detected
    if len(detected_boxes) == 0:
        print("No humans or animals detected")
        continue

        # Adicionar verificação de clique do mouse
    target_detected = False
    if clicked_coordinates:
        for i, box in enumerate(detected_boxes):
            x1, x2, y1, y2 = box
            if x1 <= clicked_coordinates[0] <= x2 and y1 <= clicked_coordinates[1] <= y2:
                target_detected = True
                at = i
                break

    # Se o alvo não foi detectado, continue com a detecção normal
    if not target_detected:
        # Check Closest
        min = 99999
        at = 0
        centers = []
        for i, box in enumerate(detected_boxes):
            x1, x2, y1, y2 = box
            c_x = ((x2 - x1) / 2) + x1
            c_y = ((y2 - y1) / 2) + y1  # Modifique esta linha para centralizar no centro da caixa delimitadora
            centers.append((c_x, c_y))
            dist = math.sqrt(math.pow(img_w/2 - c_x, 2) + math.pow(img_h/2 - c_y, 2))
            if dist < min:
                min = dist
                at = i

    # Pixel difference between crosshair(center) and the closest object
    x = centers[at][0] - img_w/2
    y = centers[at][1] - img_h/2

    # Check if closest object is in the crosshair
    if abs(x) < 10 and abs(y) < 10:
        # Move mouse and shoot
        scale = 1.7 * size_scale
        x = int(x * scale)
        y = int(y * scale)
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, x, y, 0, 0)
        time.sleep(0.01)
        y = int(y)  # Converte "y" em inteiro
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
        # Move mouse smoothly
        scale = 1.5 * size_scale
        mouse_smooth_move((human_center_x - img_w/2) * scale, (human_center_y - img_h/2) * scale, duration=0.1, steps=10)

        # Shoot 10 times
        for _ in range(10):
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, int(x), int(y), 0, 0)
            time.sleep(0.01)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, int(x), int(y), 0, 0)
            time.sleep(0.01)  # Adjust this value for faster/slower clicks


    # Desenhar cross
    
    cv2.line(ori_img, (int(img_w/2), int(img_h/2) - 10), (int(img_w/2), int(img_h/2) + 10), (0, 0, 255), 2)
    cv2.line(ori_img, (int(img_w/2) - 10, int(img_h/2)), (int(img_w/2) + 10, int(img_h/2)), (0, 0, 255), 2)

    # Desenhar círculo ao redor do crosshair
    cv2.circle(ori_img, (int(img_w/2), int(img_h/2)), crosshair_radius, (0, 255, 0), 2)

    # Mostrar a imagem original na janela
    ori_img = cv2.cvtColor(ori_img, cv2.COLOR_BGR2RGB)
    cv2.imshow("ori_img", ori_img)
    cv2.waitKey(1)

    if clicked_coordinates:
        # Mover mouse para a posição clicada
        x, y = clicked_coordinates
        x *= size_scale
        y *= size_scale
        win32api.SetCursorPos((x, y))

        # Clicar com botão esquerdo do mouse
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0) 
        time.sleep(0.1)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)

        # Resetar coordenadas clicadas
        clicked_coordinates = []

    # Resetar coordenadas clicadas
    
    clicked_coordinates = []

    
