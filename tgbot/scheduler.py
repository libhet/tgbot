"""Task scheduling primitives for exercise rotation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from .exercises.models import ExerciseType


@dataclass
class PerformanceSnapshot:
    """Tracks statistics for a single exercise type."""

    attempts: int = 0
    correct: int = 0

    def score(self) -> float:
        if self.attempts == 0:
            return 1.0
        return self.correct / self.attempts


@dataclass
class ExerciseScheduler:
    """Chooses the next exercise type based on performance."""

    weights: Dict[ExerciseType, float] = field(
        default_factory=lambda: {
            ExerciseType.COMPOSE_SENTENCE: 1.0,
            ExerciseType.ANSWER_QUESTION: 1.0,
            ExerciseType.MULTIPLE_CHOICE: 1.0,
            ExerciseType.TRUE_FALSE: 1.0,
        }
    )
    performance: Dict[ExerciseType, PerformanceSnapshot] = field(
        default_factory=lambda: {exercise_type: PerformanceSnapshot() for exercise_type in ExerciseType}
    )

    def register_result(self, exercise_type: ExerciseType, is_correct: bool) -> None:
        snapshot = self.performance.setdefault(exercise_type, PerformanceSnapshot())
        snapshot.attempts += 1
        if is_correct:
            snapshot.correct += 1

    def next_type(self) -> ExerciseType:
        """Select the next exercise type, prioritising weak spots."""

        weighted_scores: List[tuple[ExerciseType, float]] = []
        for exercise_type, weight in self.weights.items():
            snapshot = self.performance.setdefault(exercise_type, PerformanceSnapshot())
            priority = weight * (1.0 - snapshot.score())
            weighted_scores.append((exercise_type, priority))

        weighted_scores.sort(key=lambda item: item[1], reverse=True)
        return weighted_scores[0][0]

