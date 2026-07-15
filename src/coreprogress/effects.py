from __future__ import annotations

GOLD_STREAK_THRESHOLD: int = 5
UPDATE_INTERVAL_MS: int = 120
STREAK_LABEL_MIN_LEFT_PERCENT: float = 2.8
CELEBRATION_SPARKLE_MIN_STREAK: int = 5


def is_celebration_milestone(streak: int) -> bool:
    if streak in (2, 5, 10, 15):
        return True
    return streak > 15 and streak % 10 == 5
