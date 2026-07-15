from __future__ import annotations

from typing import TYPE_CHECKING

from anki.cards import Card
from anki.collection import OpChanges
from aqt import gui_hooks, mw
from aqt.qt import QTimer

from .effects import CELEBRATION_SPARKLE_MIN_STREAK, UPDATE_INTERVAL_MS, is_celebration_milestone
from .i18n import streak_label
from .palettes import StyleBundle, fill_bundle
from .settings import Config, load_config
from .state import SessionState
from .view import (
    build_celebrate_js,
    build_hide_streak_js,
    build_inject_js,
    build_push_js,
    build_streak_label_js,
    build_update_js,
    reviewer_eval,
)

if TYPE_CHECKING:
    from aqt.reviewer import Reviewer


def _log(exc: Exception) -> None:
    print(f"[coreprogress] {exc!r}")


class ProgressBarTracker:
    def __init__(self) -> None:
        self._state = SessionState()
        self._config: Config = load_config()
        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.setInterval(UPDATE_INTERVAL_MS)
        self._timer.timeout.connect(self._flush_update)
        self._setup_hooks()
        self._register_config_action()

    def _setup_hooks(self) -> None:
        gui_hooks.state_did_change.append(self._on_state_change)
        gui_hooks.reviewer_did_answer_card.append(self._on_answer_card)
        gui_hooks.reviewer_did_show_question.append(self._on_show_question)
        gui_hooks.reviewer_did_show_answer.append(self._on_show_answer)
        gui_hooks.operation_did_execute.append(self._on_operation_did_execute)

    def _register_config_action(self) -> None:
        try:
            if mw:
                mw.addonManager.setConfigUpdatedAction(__name__, self._on_config_updated)
        except Exception as exc:
            _log(exc)

    def _on_config_updated(self, _new_config: dict[str, object]) -> None:
        try:
            self._config = load_config()
            if self._state.active and self._state.bar_injected:
                self._schedule_flush()
        except Exception as exc:
            _log(exc)

    def _gold_for_style(self) -> bool:
        return self._state.gold_active if self._config.effects_enabled else False

    def _bundle(self) -> StyleBundle:
        return fill_bundle(self._config.theme, self._gold_for_style())

    def _on_state_change(self, new_state: str, old_state: str) -> None:
        try:
            if new_state == "review":
                self._handle_review_enter()
            elif new_state in ("deckBrowser", "overview") and old_state == "review":
                self._handle_review_exit()
        except Exception as exc:
            _log(exc)

    def _handle_review_enter(self) -> None:
        if not (mw and mw.col):
            return
        deck_id = int(mw.col.decks.current()["id"])
        if self._state.active and self._state.deck_id == deck_id:
            return
        self._state.reset()
        self._state.deck_id = deck_id
        self._state.active = True
        try:
            counts = mw.col.sched.counts()
            self._state.initial_total = int(counts[0]) + int(counts[1]) + int(counts[2])
        except Exception as exc:
            _log(exc)
            self._state.initial_total = 0
        QTimer.singleShot(0, self._inject_bar)

    def _handle_review_exit(self) -> None:
        self._timer.stop()
        self._state.reset()

    def _inject_bar(self) -> None:
        try:
            if self._state.bar_injected or not self._state.active:
                return
            if self._state.initial_total == 0:
                return
            js = build_inject_js(self._bundle(), self._state.progress())
            reviewer_eval(js)
            reviewer_eval(build_push_js(self._config.push_down))
            self._state.bar_injected = True
        except Exception as exc:
            _log(exc)

    def _on_show_question(self, card: Card) -> None:
        try:
            if self._state.active:
                if card.id in self._state.completed_ids:
                    self._state.undo_card(card.id)
                    self._schedule_flush()
                self._state.seen_ids.add(card.id)
            if not self._state.bar_injected:
                self._inject_bar()
        except Exception as exc:
            _log(exc)

    def _on_show_answer(self, _card: Card) -> None:
        try:
            if self._state.active and self._state.bar_injected:
                reviewer_eval(build_hide_streak_js())
        except Exception as exc:
            _log(exc)

    def _on_answer_card(self, _reviewer: Reviewer, card: Card, ease: int) -> None:
        try:
            if not self._state.active or self._state.initial_total == 0:
                return
            was_correct = ease >= 3
            self._state.register_answer(card.id, was_correct, completed=ease > 1)
            if (
                self._config.effects_enabled
                and was_correct
                and is_celebration_milestone(self._state.correct_streak)
            ):
                self._state.pending_celebration = True
            self._schedule_flush()
        except Exception as exc:
            _log(exc)

    def _on_operation_did_execute(self, _changes: OpChanges, _handler: object | None) -> None:
        try:
            if self._state.active:
                self._schedule_flush()
        except Exception as exc:
            _log(exc)

    def _schedule_flush(self) -> None:
        if not self._timer.isActive():
            self._timer.start()

    def _flush_update(self) -> None:
        try:
            if not self._state.active or not self._state.bar_injected:
                return
            progress = self._state.progress()
            bundle = self._bundle()
            reviewer_eval(build_update_js(bundle, progress))
            reviewer_eval(build_push_js(self._config.push_down))
            if self._state.pending_celebration:
                self._state.pending_celebration = False
                if not self._config.effects_enabled:
                    return
                if self._state.correct_streak >= CELEBRATION_SPARKLE_MIN_STREAK:
                    reviewer_eval(build_celebrate_js())
                reviewer_eval(build_streak_label_js(streak_label(self._state.correct_streak), bundle))
        except Exception as exc:
            _log(exc)

    def teardown(self) -> None:
        gui_hooks.state_did_change.remove(self._on_state_change)
        gui_hooks.reviewer_did_answer_card.remove(self._on_answer_card)
        gui_hooks.reviewer_did_show_question.remove(self._on_show_question)
        gui_hooks.reviewer_did_show_answer.remove(self._on_show_answer)
        gui_hooks.operation_did_execute.remove(self._on_operation_did_execute)
        self._timer.stop()


_tracker: ProgressBarTracker | None = None


def notify_config_changed() -> None:
    if _tracker is not None:
        _tracker._on_config_updated({})


def register() -> None:
    global _tracker
    from .options import setup_menu

    _tracker = ProgressBarTracker()
    setup_menu()
