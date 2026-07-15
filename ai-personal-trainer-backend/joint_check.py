import cv2
import mediapipe as mp

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(model_complexity=0,
    min_detection_confidence=0.3,
    min_tracking_confidence=0.3)

cap = cv2.VideoCapture(0)
print('Checking which joints are visible...')
print('Press Ctrl+C to stop')
fc = 0
while True:
    ret, frame = cap.read()
    if not ret: continue
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = pose.process(rgb)
    fc += 1
    if fc % 20 == 0 and result.pose_landmarks:
        lms = result.pose_landmarks.landmark
        joints = {
            'L_shoulder': lms[11],
            'R_shoulder': lms[12],
            'L_elbow':    lms[13],
            'R_elbow':    lms[14],
            'L_wrist':    lms[15],
            'R_wrist':    lms[16],
            'L_hip':      lms[23],
            'R_hip':      lms[24],
            'L_knee':     lms[25],
            'R_knee':     lms[26],
        }
        visible = [
            name for name, lm in joints.items()
            if lm.visibility > 0.3
        ]
        print(f'VISIBLE: {visible}')
    cv2.waitKey(1)
