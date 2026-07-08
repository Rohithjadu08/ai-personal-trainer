import time
from typing import Dict, Optional


EXERCISE_CONFIG = {
    "squat": {
        "angle_key": "knee",
        "down_thresh": 155,
        "up_thresh": 160,
        "side": "avg",
    },
    "bicep_curl": {
        "angle_key": "elbow",
        "down_thresh": 120,
        "up_thresh": 140,
        "side": "avg",
    },
    "push_up": {
        "angle_key": "elbow",
        "down_thresh": 120,
        "up_thresh": 140,
        "side": "avg",
    },
    "shoulder_press": {
        "angle_key": "elbow",
        "down_thresh": 120,
        "up_thresh": 150,
        "side": "avg",
    },
    "lunge": {
        "angle_key": "knee",
        "down_thresh": 155,
        "up_thresh": 160,
        "side": "left",
    },
}



class RepCounter:
    """Rep counter driven by joint angles.

    Implemented improvements:
      1) Relaxed thresholds (faster triggers)
      2) Rolling average smoothing over last 3 frames
      3) Minimum 0.5s between rep counts (prevents double counting)
      4) Debug logging every 30 frames
      5) Squat angle fallback: knee first, then hip

    PoseDetector angle key expectations:
      - left_knee_angle / right_knee_angle
      - left_elbow_angle / right_elbow_angle
      - left_shoulder_angle / right_shoulder_angle
      - left_hip_angle / right_hip_angle
    """

    def __init__(self, exercise: str = "squat"):
        self.exercise = (exercise or "squat").lower()
        self.config = EXERCISE_CONFIG.get(self.exercise, EXERCISE_CONFIG["squat"])

        self.count = 0
        self.stage = "up"  # "up" | "down"

        self.rep_timestamps = []

        # Improvement 2
        self.angle_history = []  # rolling window of last 3 raw angles

        # Improvement 3
        self.last_rep_time = 0.0

        # Improvement 4
        self.frame_count = 0

    def reset(self) -> None:
        self.count = 0
        self.stage = "up"
        self.rep_timestamps = []
        self.angle_history = []
        self.last_rep_time = 0.0
        self.frame_count = 0

    def set_exercise(self, exercise: str) -> None:
        self.exercise = (exercise or "squat").lower()
        self.config = EXERCISE_CONFIG.get(self.exercise, EXERCISE_CONFIG["squat"])
        self.reset()

    def switch_exercise(self, exercise: str):
        # Backwards compatibility with older callers
        self.set_exercise(exercise)

    def _get_angle(self, angles: Dict[str, float]) -> Optional[float]:
        """Return raw (unsmoothed) angle based on current exercise.

        Includes fallback logic to avoid returning None when a primary
        angle is missing (requested by the task):
          - squat/lunge: try knee → then hip
          - bicep_curl/push_up: try elbow → then shoulder
          - shoulder_press: try shoulder → then elbow
        """

        ex = (self.exercise or "squat").lower()

        # Primary selection from config
        key = self.config["angle_key"]
        side = self.config["side"]

        # Helper to fetch per side and per joint
        def get_joint(joint: str, s: str) -> Optional[float]:
            return angles.get(f"{s}_{joint}_angle")

        def avg_sides(joint: str) -> Optional[float]:
            l = get_joint(joint, "left")
            r = get_joint(joint, "right")
            if l is not None and r is not None:
                return (float(l) + float(r)) / 2.0
            if l is not None:
                return float(l)
            if r is not None:
                return float(r)
            return None

        # Fallbacks per exercise
        if ex in ("squat", "lunge"):
            # try knee first
            knee_joint = "knee"
            if side == "avg":
                v = avg_sides(knee_joint)
            else:
                v = get_joint(knee_joint, side)
            if v is not None:
                return v

            # then hip
            hip_joint = "hip"
            if side == "avg":
                return avg_sides(hip_joint)
            return get_joint(hip_joint, side)

        if ex in ("bicep_curl", "push_up"):
            # try elbow first
            elbow_joint = "elbow"
            if side == "avg":
                v = avg_sides(elbow_joint)
            else:
                v = get_joint(elbow_joint, side)
            if v is not None:
                return v

            # then shoulder
            shoulder_joint = "shoulder"
            if side == "avg":
                return avg_sides(shoulder_joint)
            return get_joint(shoulder_joint, side)

        if ex == "shoulder_press":
            # try shoulder first
            shoulder_joint = "shoulder"
            if side == "avg":
                v = avg_sides(shoulder_joint)
            else:
                v = get_joint(shoulder_joint, side)
            if v is not None:
                return v

            # then elbow
            elbow_joint = "elbow"
            if side == "avg":
                return avg_sides(elbow_joint)
            return get_joint(elbow_joint, side)

        # Default best-effort: use config angle_key as joint name
        joint = key
        if side == "avg":
            return avg_sides(joint)
        v = get_joint(joint, side)
        return float(v) if v is not None else None


    def update(self, angles: Dict[str, float]):
        """Update and return (count, stage, new_rep_completed)."""

        self.frame_count += 1

        raw_angle = self._get_angle(angles)
        if raw_angle is None:
            # Final fallback: no usable angle from PoseDetector
            return self.count, self.stage, False


        # Improvement 2: smoothing using rolling average of last 3 frames
        self.angle_history.append(float(raw_angle))
        if len(self.angle_history) > 3:
            self.angle_history.pop(0)
        angle = sum(self.angle_history) / len(self.angle_history)

        down_thresh = self.config["down_thresh"]
        up_thresh = self.config["up_thresh"]

        new_rep = False

        # If bent => down
        if angle < down_thresh:
            if self.stage == "up":
                self.stage = "down"

        # If extended => up; count rep on down -> up
        elif angle > up_thresh:
            if self.stage == "down":
                # Improvement 3: min time between counted reps
                current_time = time.time()
                if current_time - self.last_rep_time > 0.5:
                    self.count += 1
                    self.rep_timestamps.append(current_time)
                    self.last_rep_time = current_time
                    new_rep = True

                # Always progress stage to up (prevents getting stuck)
                self.stage = "up"

        # Improvement 4: debug logging every 30 frames
        if self.frame_count % 30 == 0:
            print(
                f"Exercise: {self.exercise} | "
                f"Angle: {angle:.1f} | "
                f"Stage: {self.stage} | "
                f"Reps: {self.count} | "
                f"Down thresh: {down_thresh} | "
                f"Up thresh: {up_thresh}"
            )

        return self.count, self.stage, new_rep

    def get_reps_per_minute(self) -> float:
        if len(self.rep_timestamps) < 2:
            return 0.0
        recent = self.rep_timestamps[-5:]
        if len(recent) < 2:
            return 0.0
        duration = recent[-1] - recent[0]
        if duration == 0:
            return 0.0
        return round((len(recent) - 1) / duration * 60, 1)

