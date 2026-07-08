from __future__ import annotations

import base64
from typing import Dict, Optional

import cv2
import numpy as np

# Legacy-simple MediaPipe API (import style required by the task)
import mediapipe as mp

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils


class PoseDetector:
    def __init__(self):
        self.pose = mp_pose.Pose(
            static_image_mode=False,
            model_complexity=0,
            min_detection_confidence=0.3,
            min_tracking_confidence=0.3,
            smooth_landmarks=True,
        )
        self._mp_drawing = mp_drawing

    def extract_keypoints(self, frame: np.ndarray) -> Optional[Dict[str, Dict[str, float]]]:
        """Return required joints with pixel coords and visibility.

        Output format (matches the task requirements):
          {
            joint_name: {"x": <px>, "y": <px>, "visibility": <0..1>}
          }

        Returns None if no pose detected.
        """
        if frame is None:
            return None

        h, w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.pose.process(rgb)

        if not result.pose_landmarks:
            return None

        landmark_names = {
            "left_shoulder": 11,
            "right_shoulder": 12,
            "left_elbow": 13,
            "right_elbow": 14,
            "left_wrist": 15,
            "right_wrist": 16,
            "left_hip": 23,
            "right_hip": 24,
            "left_knee": 25,
            "right_knee": 26,
            "left_ankle": 27,
            "right_ankle": 28,
        }

        kp_all: Dict[str, Dict[str, float]] = {}
        for name, idx in landmark_names.items():
            lm = result.pose_landmarks.landmark[idx]
            kp_all[name] = {
                "x": float(lm.x * w),
                "y": float(lm.y * h),
                "visibility": float(lm.visibility),
            }

        # visibility threshold (lowered)
        visibility_thresh = 0.1
        kp_visible: Dict[str, Dict[str, float]] = {
            k: v for k, v in kp_all.items() if v.get("visibility", 0.0) >= visibility_thresh
        }

        # If after filtering we got nothing, return all landmarks (fallback)
        return kp_visible if kp_visible else kp_all

    @staticmethod
    def calculate_angle(a, b, c) -> float:
        """Angle ABC in degrees."""
        a = np.array(a, dtype=np.float32)
        b = np.array(b, dtype=np.float32)
        c = np.array(c, dtype=np.float32)

        ba = a - b
        bc = c - b
        denom = (np.linalg.norm(ba) * np.linalg.norm(bc)) + 1e-6
        cosine = float(np.dot(ba, bc) / denom)
        cosine = max(-1.0, min(1.0, cosine))
        return float(np.degrees(np.arccos(cosine)))

    def calculate_all_angles(self, kp: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """Calculate angles from extracted keypoints."""
        angles: Dict[str, float] = {}

        def xy(name: str):
            if name not in kp:
                return None
            d = kp[name]
            return (d["x"], d["y"])

        # Arms
        left_shoulder = xy("left_shoulder")
        left_elbow = xy("left_elbow")
        left_wrist = xy("left_wrist")
        right_shoulder = xy("right_shoulder")
        right_elbow = xy("right_elbow")
        right_wrist = xy("right_wrist")

        if left_shoulder and left_elbow and left_wrist:
            angles["left_elbow_angle"] = self.calculate_angle(left_shoulder, left_elbow, left_wrist)
        if right_shoulder and right_elbow and right_wrist:
            angles["right_elbow_angle"] = self.calculate_angle(right_shoulder, right_elbow, right_wrist)

        # Shoulder angle heuristic
        if left_elbow and left_shoulder and right_shoulder:
            angles["left_shoulder_angle"] = self.calculate_angle(left_elbow, left_shoulder, right_shoulder)

        # Legs
        left_hip = xy("left_hip")
        left_knee = xy("left_knee")
        left_ankle = xy("left_ankle")
        right_hip = xy("right_hip")
        right_knee = xy("right_knee")
        right_ankle = xy("right_ankle")

        if left_hip and left_knee and left_ankle:
            angles["left_knee_angle"] = self.calculate_angle(left_hip, left_knee, left_ankle)
        if right_hip and right_knee and right_ankle:
            angles["right_knee_angle"] = self.calculate_angle(right_hip, right_knee, right_ankle)

        if left_knee and left_hip and right_hip:
            angles["left_hip_angle"] = self.calculate_angle(left_knee, left_hip, right_hip)

        return angles

    def draw_skeleton(self, frame: np.ndarray, kp: Dict[str, Dict[str, float]]) -> np.ndarray:
        if frame is None or not kp:
            return frame

        connections = [
            ("left_shoulder", "right_shoulder"),
            ("left_shoulder", "left_elbow"),
            ("left_elbow", "left_wrist"),
            ("right_shoulder", "right_elbow"),
            ("right_elbow", "right_wrist"),
            ("left_shoulder", "left_hip"),
            ("right_shoulder", "right_hip"),
            ("left_hip", "right_hip"),
            ("left_hip", "left_knee"),
            ("left_knee", "left_ankle"),
            ("right_hip", "right_knee"),
            ("right_knee", "right_ankle"),
        ]

        for a, b in connections:
            if a in kp and b in kp:
                cv2.line(
                    frame,
                    (int(kp[a]["x"]), int(kp[a]["y"])),
                    (int(kp[b]["x"]), int(kp[b]["y"])),
                    (0, 255, 255),
                    2,
                )

        for _, d in kp.items():
            cv2.circle(frame, (int(d["x"]), int(d["y"])), 5, (255, 0, 255), -1)

        return frame

    def encode_frame(self, frame: np.ndarray) -> str:
        if frame is None:
            return ""
        ok, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
        if not ok:
            return ""
        return base64.b64encode(buffer).decode("utf-8")

