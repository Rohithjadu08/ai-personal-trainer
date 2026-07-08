from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class SessionLogger:
    """In-memory session logger (can be replaced later with DB)."""

    reps: List[Dict[str, Any]] = field(default_factory=list)

    def log_rep(self, exercise: str, rep_number: int, form_score: float) -> None:
        self.reps.append(
            {
                "exercise": exercise,
                "rep_number": rep_number,
                "form_score": float(form_score),
            }
        )

    def get_summary(self) -> Dict[str, Any]:
        total = len(self.reps)
        avg = (sum(r["form_score"] for r in self.reps) / total) if total else 0.0
        return {"total_reps": total, "avg_form_score": avg}

