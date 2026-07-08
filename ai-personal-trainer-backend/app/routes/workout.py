
from __future__ import annotations

import asyncio
import json
import os
import time
import traceback
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, WebSocket, WebSocketDisconnect



from ..config_ai import CAMERA_INDEX, DEFAULT_EXERCISE
from ..form_checker import FormChecker
from ..pose_detector import PoseDetector
from ..rep_counter import RepCounter
from ..session_logger import SessionLogger

router = APIRouter()

# In-memory per-user session state
_sessions: Dict[str, SessionLogger] = {}

# Active per-user engine instances (for exercise switching)
_active_engines: Dict[str, dict] = {}


@router.post("/workout/start")
def workout_start():
    return {"ok": True}


SESSIONS_FILE = "sessions.json"

# Tracks when a user session started (for duration_seconds)
_session_start_times: Dict[str, float] = {}


@router.delete("/sessions")
def clear_sessions():
    if os.path.exists(SESSIONS_FILE):
        os.remove(SESSIONS_FILE)
    return {"status": "cleared"}



def load_sessions() -> List[dict]:
    if os.path.exists(SESSIONS_FILE):
        try:
            with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
                return json.load(f) or []
        except Exception:
            # Corrupt file or invalid JSON -> reset safely
            return []
    return []


def save_session_to_file(session_data: dict) -> None:
    sessions = load_sessions()
    sessions.append(session_data)
    with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(sessions, f, indent=2)


@router.get("/sessions")
def get_sessions():
    # Return [] if file doesn't exist or is unreadable
    return load_sessions()


def _safe_float(x: Any) -> float:
    try:
        return float(x)
    except Exception:
        return 0.0


@router.get("/sessions/stats")
def sessions_stats():
    sessions = load_sessions()

    total_sessions = len(sessions)
    total_reps = int(sum(int(s.get("total_reps", 0) or 0) for s in sessions))

    form_scores = [_safe_float(s.get("avg_form_score", 0)) for s in sessions]
    avg_form_score = (sum(form_scores) / len(form_scores)) if form_scores else 0.0

    best_score = max(form_scores) if form_scores else 0.0

    sessions_by_exercise: Dict[str, int] = {}
    for s in sessions:
        ex = str(s.get("exercise") or "unknown")
        sessions_by_exercise[ex] = int(sessions_by_exercise.get(ex, 0)) + 1

    # recent_sessions: last 7 sessions in storage order
    recent_sessions = sessions[-7:]

    return {
        "total_sessions": total_sessions,
        "total_reps": total_reps,
        "avg_form_score": float(avg_form_score),
        "best_score": float(best_score),
        "sessions_by_exercise": sessions_by_exercise,
        "recent_sessions": recent_sessions,
        "form_score_history": form_scores,
    }



def grade_from_score(avg_form_score: float) -> str:
    if avg_form_score >= 90:
        return "A"
    if avg_form_score >= 75:
        return "B"
    if avg_form_score >= 60:
        return "C"
    if avg_form_score >= 50:
        return "D"
    return "D"


@router.post("/workout/end/{user_id}")
def workout_end(user_id: str):
    # Active engine must exist to know the selected exercise
    engine = _active_engines.get(user_id)
    if not engine:
        return {"user_id": user_id, "summary": {}}

    counter = engine.get("counter")
    logger = _sessions.get(user_id, SessionLogger())

    exercise = engine.get("exercise", "") if engine else ""
    if exercise == "":
        exercise = getattr(engine.get("counter"), "exercise", "unknown") if engine else "unknown"

    # Never use DEFAULT_EXERCISE or any hardcoded fallback for saved exercise name.
    if exercise is None:
        exercise = "unknown"






    reps_logged = logger.reps or []

    # total reps: best-effort from counter, otherwise from logger
    total_reps = 0
    for attr in ("count", "rep_count", "total_reps", "reps"):
        try:
            if counter is not None and hasattr(counter, attr):
                val = getattr(counter, attr)
                if isinstance(val, (int, float)):
                    total_reps = int(val)
                    break
        except Exception:
            continue

    if total_reps == 0:
        total_reps = len(reps_logged)

    # avg form score from all logged reps (not just last N)
    scores = [float(r.get("form_score", 0.0)) for r in reps_logged]
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0.0

    grade = grade_from_score(float(avg_score))

    # duration_seconds: from start timestamp (best-effort)
    start_ts = _session_start_times.get(user_id)
    duration_seconds = 0.0
    if start_ts is not None:
        duration_seconds = max(0.0, time.time() - float(start_ts))

    session_data = {
        "id": str(uuid4()),
        "user_id": str(user_id),
        "exercise": str(exercise),

        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "total_reps": int(total_reps),
        "avg_form_score": float(avg_score),
        "grade": grade,
        "duration_seconds": float(round(duration_seconds, 2)),
    }

    save_session_to_file(session_data)

    _sessions.pop(user_id, None)
    _active_engines.pop(user_id, None)
    _session_start_times.pop(user_id, None)

    return session_data




@router.post("/workout/switch-exercise")
def workout_switch_exercise(payload: dict):
    # Compatibility alias for the frontend contract.
    return workout_switch(payload)


@router.post("/workout/switch")
def workout_switch(payload: dict):



    user_id = str(payload.get("user_id"))
    exercise = str(payload.get("exercise"))
    if not user_id or not exercise:
        return {"status": "error", "message": "Missing user_id or exercise"}

    engine = _active_engines.get(user_id)
    if not engine:
        engine = _active_engines[user_id] = {}

    counter = engine.get("counter")

    if counter is not None and hasattr(counter, "set_exercise"):
        counter.set_exercise(exercise)
    else:
        try:
            engine["counter"] = RepCounter(exercise=exercise)
        except Exception:
            pass

    # FormChecker is simple; recreate for new exercise
    try:
        engine["checker"] = FormChecker(exercise=exercise)
    except Exception:
        pass

    return {"status": "switched", "exercise": exercise}


@router.get("/workout/test-camera")
def test_camera():
    try:
        import cv2
    except Exception:
        return {"camera_working": False, "message": "OpenCV not installed."}

    cap = None
    try:
        cap = cv2.VideoCapture(CAMERA_INDEX)
        if cap is None or not cap.isOpened():
            return {
                "camera_working": False,
                "message": f"Camera not accessible at index {CAMERA_INDEX}.",
            }
        ok, frame = cap.read()
        if not ok or frame is None:
            return {
                "camera_working": False,
                "message": "Camera opened but frame read failed.",
            }
        return {"camera_working": True, "message": "Camera frame capture succeeded."}
    finally:
        if cap is not None:
            cap.release()


@router.websocket("/ws/{user_id}")
async def workout_stream(websocket: WebSocket, user_id: str):
    try:
        await websocket.accept()

        # Mark session start time for duration_seconds
        _session_start_times[str(user_id)] = time.time()


        import cv2

        cap = cv2.VideoCapture(CAMERA_INDEX)
        if cap is None or not cap.isOpened():
            raise RuntimeError(
                "Camera not accessible. Check if another app is using it or permissions are denied."
            )

        # Create PoseDetector inside a try block
        try:
            detector = PoseDetector()
        except Exception as e:
            raise RuntimeError(f"Failed to initialize PoseDetector: {e}")

        counter = RepCounter(exercise=DEFAULT_EXERCISE)
        checker = FormChecker(exercise=DEFAULT_EXERCISE)
        _sessions.setdefault(user_id, SessionLogger())

        _active_engines[user_id] = {
            "counter": counter,
            "checker": checker,
        }

        while True:
            ret, frame = cap.read()
            if not ret or frame is None:
                await asyncio.sleep(0.01)
                continue

            frame = cv2.flip(frame, 1)

            # Use current engine instances (exercise can be switched mid-stream)
            engine = _active_engines.get(user_id) or {}
            counter = engine.get("counter", counter)
            checker = engine.get("checker", checker)

            try:
                keypoints = detector.extract_keypoints(frame)
                is_visible = bool(keypoints)
                angles = detector.calculate_all_angles(keypoints) if is_visible else {}

                rep_count, stage, new_rep = counter.update(angles)
                form_score, feedback = checker.score(angles)

                # Log the rep under the currently active exercise
                active_exercise = getattr(counter, "exercise", DEFAULT_EXERCISE)
                if new_rep:
                    _sessions[user_id].log_rep(str(active_exercise), rep_count, form_score)


                frame_out = detector.draw_skeleton(frame, keypoints)
                frame_b64 = detector.encode_frame(frame_out)

                msg = {
                    "frame": frame_b64,
                    "rep_count": int(rep_count),
                    "stage": str(stage).lower(),
                    "form_score": float(form_score),
                    "feedback": feedback,
                    "is_visible": bool(is_visible),
                }
                await websocket.send_text(json.dumps(msg))
            except Exception:
                await websocket.send_text(
                    json.dumps(
                        {
                            "error": "Frame processing error",
                            "trace": traceback.format_exc(),
                        }
                    )
                )

            await asyncio.sleep(0.033)

    except WebSocketDisconnect:
        return
    except Exception as e:
        try:
            await websocket.send_text(
                json.dumps({"error": str(e), "trace": traceback.format_exc()})
            )
        except Exception:
            pass
        return
    finally:
        try:
            if "cap" in locals() and cap is not None:
                cap.release()
        except Exception:
            pass

