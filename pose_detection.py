import cv2
import mediapipe as mp
import sys
import json
import numpy as np

mp_pose = mp.solutions.pose
mp_hands = mp.solutions.hands

pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)

cap = cv2.VideoCapture(0)

count = 0
stage = None
counting = False
ready = False

def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360 - angle

    return angle

def detect_swipe_right(hand_landmarks):
    wrist_x = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].x
    index_finger_x = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x
    return index_finger_x > wrist_x + 0.2

def detect_thumbs_up(hand_landmarks):
    thumb_tip_y = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].y
    thumb_ip_y = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP].y
    return thumb_tip_y < thumb_ip_y

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results_pose = pose.process(image)
    results_hands = hands.process(image)

    if results_hands.multi_hand_landmarks:
        for hand_landmarks in results_hands.multi_hand_landmarks:
            if not counting and detect_thumbs_up(hand_landmarks):
                counting = True
                ready = True
            elif detect_swipe_right(hand_landmarks):
                counting = False

    if counting and results_pose.pose_landmarks:
        landmarks = results_pose.pose_landmarks.landmark
        shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].y]
        elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW].x, landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW].y]
        wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST].x, landmarks[mp_pose.PoseLandmark.RIGHT_WRIST].y]

        angle = calculate_angle(shoulder, elbow, wrist)

        if angle > 160:
            stage = "down"
        if angle < 30 and stage == 'down':
            stage = "up"
            count += 1

    result = {
        "count": count,
        "counting": counting,
        "ready": ready
    }
    print(json.dumps(result))
    sys.stdout.flush()
    ready = False  

cap.release()
