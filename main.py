import cv2
import threading
import pygame
from datetime import datetime

# Paths
CONFIG_PATH = 'ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt'
MODEL_PATH = 'frozen_inference_graph.pb'
CLASSES_PATH = 'coco.names'
VIDEO_PATH = 0

# Globals
person_count = 0
roi_x, roi_y, roi_width, roi_height = 250, 100, 500, 200
resizing = False
mouse_start = (0, 0)
resize_mode = None

alert_active = False
alert_count = 0
video_recording = False
video_writer = None

active_people = []
min_distance = 50

# Init model
net = cv2.dnn_DetectionModel(CONFIG_PATH, MODEL_PATH)
net.setInputSize(320, 320)
net.setInputScale(1.0 / 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)

with open(CLASSES_PATH, 'r') as f:
    classes_list = f.read().splitlines()

desired_class_index = classes_list.index('person') + 1

pygame.mixer.init()
alert_sound = pygame.mixer.Sound('alert_sound.wav.mp3')

# ----------------------- FUNCTIONS -----------------------

def mouse_callback(event, x, y, flags, param):
    global resizing, roi_x, roi_y, roi_width, roi_height, mouse_start, resize_mode
    border = 15
    on_right_edge = abs((roi_x + roi_width) - x) < border
    on_bottom_edge = abs((roi_y + roi_height) - y) < border
    inside_roi = roi_x < x < roi_x + roi_width and roi_y < y < roi_y + roi_height

    if event == cv2.EVENT_LBUTTONDOWN:
        mouse_start = (x, y)
        if on_right_edge and on_bottom_edge:
            resize_mode = "bottom_right"
            resizing = True
        elif on_right_edge:
            resize_mode = "right"
            resizing = True
        elif on_bottom_edge:
            resize_mode = "bottom"
            resizing = True
        elif inside_roi:
            resize_mode = "move"
            resizing = True
    elif event == cv2.EVENT_MOUSEMOVE and resizing:
        dx = x - mouse_start[0]
        dy = y - mouse_start[1]
        mouse_start = (x, y)
        if resize_mode == "move":
            roi_x += dx
            roi_y += dy
        elif resize_mode == "right":
            roi_width = max(50, roi_width + dx)
        elif resize_mode == "bottom":
            roi_height = max(50, roi_height + dy)
        elif resize_mode == "bottom_right":
            roi_width = max(50, roi_width + dx)
            roi_height = max(50, roi_height + dy)
    elif event == cv2.EVENT_LBUTTONUP:
        resizing = False
        resize_mode = None

def draw_roi_rectangle(image):
    global roi_x, roi_y, roi_width, roi_height
    overlay = image.copy()
    cv2.rectangle(overlay, (roi_x, roi_y), (roi_x + roi_width, roi_y + roi_height), (0, 0, 255), -1)
    cv2.addWeighted(overlay, 0.3, image, 0.7, 0, image)

    cv2.rectangle(image, (roi_x, roi_y), (roi_x + roi_width, roi_y + roi_height), (0, 0, 255), 2)
    cv2.circle(image, (roi_x, roi_y), 5, (0, 0, 255), -1)
    cv2.circle(image, (roi_x + roi_width, roi_y), 5, (0, 0, 255), -1)
    cv2.circle(image, (roi_x, roi_y + roi_height), 5, (0, 0, 255), -1)
    cv2.circle(image, (roi_x + roi_width, roi_y + roi_height), 5, (0, 0, 255), -1)

    return (roi_x, roi_y, roi_width, roi_height)

def is_point_inside_area(cx, cy, area):
    x, y, w, h = area
    return x <= cx <= x + w and y <= cy <= y + h

def start_video_recording():
    global video_recording, video_writer
    video_filename = f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
    video_writer = cv2.VideoWriter(video_filename, cv2.VideoWriter_fourcc(*'mp4v'), 20, (1000, 700))
    video_recording = True

def stop_video_recording():
    global video_recording, video_writer
    if video_writer is not None:
        video_writer.release()
    video_recording = False

def trigger_alert():
    global alert_active, alert_count
    alert_active = True
    start_video_recording()
    alert_sound.play()
    pygame.time.wait(int(alert_sound.get_length() * 1000))
    stop_video_recording()
    alert_active = False
    alert_count = 0

def is_new_person(cx, cy):
    global active_people
    for (px, py) in active_people:
        dist = ((cx - px)**2 + (cy - py)**2) ** 0.5
        if dist < min_distance:
            return False
    return True

def update_active_people(detected_people):
    global active_people, person_count
    active_people = detected_people
    if len(active_people) == 0:
        person_count = 0

def process_detections(classes, confidences, boxes, img):
    global alert_active, alert_count, person_count
    area_of_interest = draw_roi_rectangle(img)
    detected_people = []

    if len(classes):
        for classId, confidence, box in zip(classes.flatten(), confidences.flatten(), boxes):
            if classId == desired_class_index:
                x, y, w, h = box
                cx = x + w // 2
                cy = y + h // 2
                if is_point_inside_area(cx, cy, area_of_interest):
                    if is_new_person(cx, cy):
                        person_count += 1
                        if not alert_active and alert_count < 3:
                            threading.Thread(target=trigger_alert).start()
                            alert_count += 1
                    detected_people.append((cx, cy))
                cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                cv2.putText(img, 'person', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

    update_active_people(detected_people)

# ---------------- MAIN LOOP FUNC ----------------
def run_system():
    global alert_active, video_recording, video_writer
    cv2.namedWindow('IMG')
    cv2.setMouseCallback('IMG', mouse_callback)
    video = cv2.VideoCapture(VIDEO_PATH)

    while True:
        ret, img = video.read()
        if not ret:
            break

        img = cv2.resize(img, (1000, 700))
        classes, confidences, boxes = net.detect(img, confThreshold=0.6)
        process_detections(classes, confidences, boxes, img)

        if video_recording:
            video_writer.write(img)

        cv2.putText(img, f'Detected People: {person_count}', (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        if alert_active:
            cv2.putText(img, 'INTRUDER DETECTED', (105, 65), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

        cv2.imshow('IMG', img)
        key = cv2.waitKey(1) & 0xFF
        if key == 13:  # Enter
            if alert_active:
                alert_sound.stop()
                alert_active = False

    if video_recording and video_writer is not None:
        video_writer.release()
    video.release()
    cv2.destroyAllWindows()
