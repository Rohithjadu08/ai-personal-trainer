from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Optional

import pyttsx3


@dataclass
class VoiceFeedback:
    cooldown_seconds: int = 3

    _last_spoken_at: float = 0.0
    _lock: threading.Lock = threading.Lock()

    def speak_async(self, text: str) -> None:
        if not text:
            return

        now = time.time()
        with self._lock:
            if (now - self._last_spoken_at) < self.cooldown_seconds:
                return
            self._last_spoken_at = now

        def _worker():
            try:
                engine = pyttsx3.init()
                engine.setProperty("rate", 150)
                engine.say(text)
                engine.runAndWait()
            except Exception:
                # Silently ignore audio errors (server environments may lack audio devices)
                return

        t = threading.Thread(target=_worker, daemon=True)
        t.start()

