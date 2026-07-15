from __future__ import annotations

from dataclasses import dataclass, field

from .data import compute_progress, remaining_count
from .effects import GOLD_STREAK_THRESHOLD


@dataclass(frozen=True)
class AnswerRecord:
    card_id: int
    was_correct: bool


@dataclass
class SessionState:
    deck_id: int | None = None
    initial_total: int = 0
    completed_ids: set[int] = field(default_factory=set)
    seen_ids: set[int] = field(default_factory=set)
    answer_history: list[AnswerRecord] = field(default_factory=list)
    bar_injected: bool = False
    active: bool = False
    correct_streak: int = 0
    pending_celebration: bool = False
    gold_active: bool = False

    def reset(self) -> None:
        self.deck_id = None
        self.initial_total = 0
        self.completed_ids.clear()
        self.seen_ids.clear()
        self.answer_history.clear()
        self.bar_injected = False
        self.active = False
        self.correct_streak = 0
        self.pending_celebration = False
        self.gold_active = False

    def progress(self) -> float:
        return compute_progress(self.initial_total, len(self.completed_ids), remaining_count())

    def register_answer(self, card_id: int, was_correct: bool, completed: bool) -> None:
        if completed:
            self.completed_ids.add(card_id)
        if was_correct:
            self.correct_streak += 1
            self.gold_active = self.correct_streak >= GOLD_STREAK_THRESHOLD
        else:
            self.correct_streak = 0
            self.gold_active = False
        self.answer_history.append(AnswerRecord(card_id, was_correct))
        self.seen_ids.add(card_id)

    def undo_card(self, card_id: int) -> None:
        self.completed_ids.discard(card_id)
        history = self.answer_history
        for index in range(len(history) - 1, -1, -1):
            if history[index].card_id == card_id:
                del history[index]
                break
        self._recompute_streak()

    def _recompute_streak(self) -> None:
        streak = 0
        for record in reversed(self.answer_history):
            if not record.was_correct:
                break
            streak += 1
        self.correct_streak = streak
        self.gold_active = streak >= GOLD_STREAK_THRESHOLD
