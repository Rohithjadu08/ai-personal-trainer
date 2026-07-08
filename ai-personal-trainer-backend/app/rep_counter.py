import time
from typing import Dict, Optional


EXERCISE_CONFIG = {
    "bicep_curl": {
        "angle_key": "elbow",
        "down_thresh": 55,
        "up_thresh": 110,
        "side": "left",
    },
    "push_up": {
        "angle_key": "elbow",
        "down_thresh": 55,
        "up_thresh": 110,
        "side": "left",
    },
    "shoulder_press": {
        "angle_key": "elbow",
        "down_thresh": 55,
        "up_thresh": 110,
        "side": "left",
    },
    # since knees/hips are not visible, use elbow as proxy
    "squat": {
        "angle_key": "elbow",
        "down_thresh": 55,
        "up_thresh": 110,
        "side": "left",
    },
    "lunge": {
        "angle_key": "elbow",
        "down_thresh": 55,
        "up_thresh": 110,
        "side": "left",
    },
}


class RepCounter:
    """Angle-based rep counter with smoothing + minimum rep time.

    State machine:
      - stage starts as "up"
      - if angle < down_thresh and stage == "up": stage='down' + print >>> DOWN detected
      - if angle > up_thresh and stage == 'down': stage='up', count++, new_rep=True
        + print >>> REP counted! Total=X

    Rep increments are throttled by at least 0.5 seconds.
    """

    def __init__(self, exercise: str = "bicep_curl"):
        self.exercise = (exercise or "bicep_curl").lower()
        self.config = EXERCISE_CONFIG.get(self.exercise, EXERCISE_CONFIG["bicep_curl"])

        self.count = 0
        self.stage = "up"

        self.rep_timestamps = []

        # minimum rep interval
        self.last_rep_time = 0.0

        # smoothing window (last 3 frames)
        self.angle_history = []  # type: list[float]

        self.frame_count = 0

    def reset(self) -> None:
        self.count = 0
        self.stage = "up"
        self.rep_timestamps = []
        self.last_rep_time = 0.0
        self.angle_history = []
        self.frame_count = 0

    def set_exercise(self, exercise: str) -> None:
        self.exercise = (exercise or "bicep_curl").lower()
        self.config = EXERCISE_CONFIG.get(self.exercise, EXERCISE_CONFIG["bicep_curl"])
        self.reset()

    def switch_exercise(self, exercise: str):
        self.set_exercise(exercise)

    def _get_angle(self, angles: Dict[str, float]) -> Optional[float]:
        """Return the raw (unsmoothed) angle for the configured exercise."""
        angle_key = self.config["angle_key"]
        side = self.config["side"]  # always 'left' in your config

        # PoseDetector uses key names like: left_elbow_angle, right_elbow_angle, etc.
        joint = angle_key
        key = f"{side}_{joint}_angle"
        val = angles.get(key)
        if val is None:
            return None
        return float(val)

    def update(self, angles: Dict[str, float]):
        self.frame_count += 1

        raw_angle = self._get_angle(angles)
        if raw_angle is None:
            return self.count, self.stage, False

        # Smooth angle over last 3 frames
        self.angle_history.append(float(raw_angle))
        if len(self.angle_history) > 3:
            self.angle_history.pop(0)
        angle = sum(self.angle_history) / len(self.angle_history)

        down_thresh = self.config["down_thresh"]
        up_thresh = self.config["up_thresh"]

        new_rep = False
        current_time = time.time()

        # down detection
        if angle < down_thresh and self.stage == "up":
            self.stage = "down"
            print(">>> DOWN detected")

        # rep counted on up transition
        elif angle > up_thresh and self.stage == "down":
            if current_time - self.last_rep_time > 0.5:
                self.stage = "up"
                self.count += 1
                self.last_rep_time = current_time
                self.rep_timestamps.append(current_time)
                new_rep = True
                print(f">>> REP counted! Total={self.count}")
            else:
                # still go back to up to allow next down
                self.stage = "up"

        # keep compatibility with your existing UI
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

