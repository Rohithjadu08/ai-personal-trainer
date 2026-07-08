from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class FormChecker:
    """Compare measured angles to ideal ranges and produce a score + feedback."""

    exercise: str = "squat"

    def score(self, angles: Dict[str, float]) -> Tuple[float, List[str]]:
        ex = (self.exercise or "").lower()

        feedback: List[str] = []
        score = 100.0

        def check(name: str, ideal_low: float, ideal_high: float, actual: float, weight: float = 1.0):
            nonlocal score
            if actual == 0:
                # no data; penalize a bit
                score -= 10 * weight
                feedback.append(f"Missing {name} angle; adjust camera/pose visibility.")
                return
            if actual < ideal_low:
                score -= (ideal_low - actual) * 0.3 * weight
                feedback.append(f"Increase {name} (currently too small).")
            elif actual > ideal_high:
                score -= (actual - ideal_high) * 0.3 * weight
                feedback.append(f"Reduce {name} (currently too large).")

        if ex == "squat":
            knee = angles.get("left_knee_angle", 0.0) or angles.get("right_knee_angle", 0.0) or 0.0
            check("knee", 90, 110, float(knee), weight=1.0)

        elif ex == "lunge":
            knee = angles.get("left_knee_angle", 0.0) or angles.get("right_knee_angle", 0.0) or 0.0
            check("knee", 95, 120, float(knee), weight=1.0)

        elif ex == "bicep_curl":
            elbow = angles.get("left_elbow_angle", 0.0) or angles.get("right_elbow_angle", 0.0) or 0.0
            check("elbow", 60, 90, float(elbow), weight=1.0)

        elif ex == "push_up":
            elbow = angles.get("left_elbow_angle", 0.0) or angles.get("right_elbow_angle", 0.0) or 0.0
            check("elbow", 80, 120, float(elbow), weight=1.0)

        elif ex == "shoulder_press":
            elbow = angles.get("left_elbow_angle", 0.0) or angles.get("right_elbow_angle", 0.0) or 0.0
            check("elbow", 90, 130, float(elbow), weight=1.0)

        # clamp
        score = max(0.0, min(100.0, float(score)))
        if not feedback:
            feedback.append("Good form! Keep going.")

        return score, feedback

