"""Session model and persistence utilities for the Telegram training mini-app."""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


class SessionStatus(str, Enum):
    """Enumeration of supported session statuses."""

    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class UserResponse:
    """Single user interaction within a session."""

    step: int
    answer: Any
    correct: bool
    feedback: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_json(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["timestamp"] = self.timestamp.isoformat()
        return payload

    @classmethod
    def from_json(cls, payload: Dict[str, Any]) -> "UserResponse":
        data = dict(payload)
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)


@dataclass
class Session:
    """Keeps track of a learning mini-app session for a single user."""

    session_id: str
    user_id: str
    task_type: str
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status: SessionStatus = SessionStatus.ACTIVE
    responses: List[UserResponse] = field(default_factory=list)

    def record_response(
        self,
        answer: Any,
        correct: bool,
        *,
        step: Optional[int] = None,
        feedback: Optional[str] = None,
    ) -> UserResponse:
        """Persist the user response and return the created record."""

        response = UserResponse(
            step=step if step is not None else len(self.responses) + 1,
            answer=answer,
            correct=correct,
            feedback=feedback,
        )
        self.responses.append(response)
        if correct:
            self._maybe_complete()
        else:
            if self.status is SessionStatus.COMPLETED:
                self.status = SessionStatus.ACTIVE
        return response

    def _maybe_complete(self) -> None:
        """Mark the session completed if every recorded answer is correct."""

        if self.responses and all(response.correct for response in self.responses):
            self.status = SessionStatus.COMPLETED

    def fail(self, feedback: Optional[str] = None) -> None:
        """Mark the session as failed and optionally append feedback."""

        self.status = SessionStatus.FAILED
        if feedback is not None:
            self.responses.append(
                UserResponse(
                    step=len(self.responses) + 1,
                    answer="__system__",
                    correct=False,
                    feedback=feedback,
                )
            )

    def to_json(self) -> Dict[str, Any]:
        """Serialize the session to a JSON-compatible dict."""

        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "task_type": self.task_type,
            "started_at": self.started_at.isoformat(),
            "status": self.status.value,
            "responses": [response.to_json() for response in self.responses],
        }

    @classmethod
    def from_json(cls, payload: Dict[str, Any]) -> "Session":
        """Deserialize a :class:`Session` from a JSON-compatible dict."""

        return cls(
            session_id=payload["session_id"],
            user_id=payload["user_id"],
            task_type=payload["task_type"],
            started_at=datetime.fromisoformat(payload["started_at"]),
            status=SessionStatus(payload["status"]),
            responses=[UserResponse.from_json(item) for item in payload.get("responses", [])],
        )

    def progress(self) -> float:
        """Return the progress percentage as a float in [0, 1]."""

        if not self.responses:
            return 0.0
        correct_answers = sum(1 for response in self.responses if response.correct)
        return correct_answers / len(self.responses)

    def summary(self) -> Dict[str, Any]:
        """Return a compact summary of the session progress."""

        return {
            "status": self.status.value,
            "completed_steps": sum(1 for response in self.responses if response.correct),
            "total_steps": len(self.responses),
            "progress": self.progress(),
        }
