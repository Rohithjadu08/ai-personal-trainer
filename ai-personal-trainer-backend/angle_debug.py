import cv2, sys
sys.path.insert(0, '.')
from app.pose_detector import PoseDetector

def fmt(v):
    return f'{v:.0f}' if isinstance(v, float) else 'N/A'

detector = PoseDetector()
cap = cv2.VideoCapture(0)
print('Watching angles - do your exercises now!')
print('Ctrl+C to stop')
fc = 0
while True:
    ret, frame = cap.read()
    if not ret:
        continue
    frame = cv2.flip(frame, 1)
    kp = detector.extract_keypoints(frame)
    if kp:
        a = detector.calculate_all_angles(kp)
        fc += 1
        if fc % 15 == 0:
            le = fmt(a.get('left_elbow'))
            re = fmt(a.get('right_elbow'))
            lk = fmt(a.get('left_knee'))
            rk = fmt(a.get('right_knee'))
            lh = fmt(a.get('left_hip'))
            rh = fmt(a.get('right_hip'))
            print(f'ELBOW L={le} R={re} | KNEE L={lk} R={rk} | HIP L={lh} R={rh}')
    cv2.waitKey(1)
