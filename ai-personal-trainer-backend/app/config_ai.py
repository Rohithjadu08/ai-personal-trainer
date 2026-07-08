import os


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


# MediaPipe / OpenCV tuning
CAMERA_INDEX: int = _env_int("CAMERA_INDEX", 0)
FRAME_FPS: int = _env_int("FRAME_FPS", 30)

# Scoring / feedback
FORM_SCORE_MIN: int = 0
FORM_SCORE_MAX: int = 100

# Voice feedback
VOICE_COOLDOWN_SECONDS: int = _env_int("VOICE_COOLDOWN_SECONDS", 3)

# Default exercise removed to prevent unintended exercise selection.
# Keep variable for backward compatibility with existing imports.
DEFAULT_EXERCISE: str = ""


