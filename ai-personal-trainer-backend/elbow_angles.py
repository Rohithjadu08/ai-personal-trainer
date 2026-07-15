import cv2
import mediapipe as mp
import numpy as np

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(model_complexity=0,
    min_detection_confidence=0.3,
    min_tracking_confidence=0.3)

def angle(a, b, c):
    a,b,c = np.array(a),np.array(b),np.array(c)
    ba,bc = a-b,c-b
    cos = np.dot(ba,bc)/(np.linalg.norm(ba)*np.linalg.norm(bc)+1e-6)
    return round(np.degrees(np.arccos(np.clip(cos,-1,1))),1)

cap = cv2.VideoCapture(0)
print('Do bicep curls slowly - watch the elbow angles!')
print('Ctrl+C to stop')
fc = 0
while True:
    ret, frame = cap.read()
    if not ret: continue
    frame = cv2.flip(frame, 1)
    h,w = frame.shape[:2]
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    r = pose.process(rgb)
    fc += 1
    if fc % 10 == 0 and r.pose_landmarks:
        lm = r.pose_landmarks.landmark
        def pt(idx):
            return (lm[idx].x*w, lm[idx].y*h)
        try:
            le = angle(pt(11), pt(13), pt(15))
            re = angle(pt(12), pt(14), pt(16))
            print(f'LEFT elbow={le:.0f} | RIGHT elbow={re:.0f}')
        except:
            print('calculating...')
    cv2.waitKey(1)
