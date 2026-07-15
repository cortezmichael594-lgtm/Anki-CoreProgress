from __future__ import annotations

from aqt import mw


def _log(exc: Exception) -> None:
    print(f"[coreprogress] {exc!r}")


def remaining_count() -> int:
    try:
        if mw and mw.col and hasattr(mw.col, "sched"):
            counts = mw.col.sched.counts()
            return int(counts[0]) + int(counts[1]) + int(counts[2])
    except Exception as exc:
        _log(exc)
    return 0


def compute_progress(initial_total: int, completed: int, remaining: int) -> float:
    if initial_total == 0:
        return 0.0
    effective_total = max(initial_total, completed + remaining)
    done = max(completed, effective_total - remaining)
    return min(100.0, done / effective_total * 100.0)
