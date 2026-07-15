# Copyright (C) 2026 AnkiCraft
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with this program. If not, see
# <https://www.gnu.org/licenses/>.

from __future__ import annotations

from dataclasses import dataclass

from aqt import mw

from . import constants
from .palettes import DEFAULT_THEME, THEME_KEYS


@dataclass(frozen=True)
class Config:
    theme: str
    effects_enabled: bool
    push_down: int


DEFAULT_CONFIG = Config(
    theme=DEFAULT_THEME,
    effects_enabled=True,
    push_down=0,
)


def _log(exc: Exception) -> None:
    print(f"[coreprogress] {exc!r}")


def _as_int(value: object, fallback: int, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return fallback
    return max(minimum, min(maximum, int(value)))


def _as_bool(value: object, fallback: bool) -> bool:
    return value if isinstance(value, bool) else fallback


def _theme_from_legacy(stored: dict[str, object]) -> str | None:
    for key in THEME_KEYS:
        if stored.get(key) is True:
            return key
    return None


def _as_theme(stored: dict[str, object]) -> str:
    value = stored.get("theme")
    if isinstance(value, str) and value in THEME_KEYS:
        return value
    legacy = _theme_from_legacy(stored)
    return legacy if legacy is not None else DEFAULT_THEME


def load_config() -> Config:
    stored: dict[str, object] = {}
    try:
        loaded = mw.addonManager.getConfig(__name__)
        if isinstance(loaded, dict):
            stored = loaded
    except Exception as exc:
        _log(exc)
    return Config(
        theme=_as_theme(stored),
        effects_enabled=_as_bool(stored.get("effects_enabled"), DEFAULT_CONFIG.effects_enabled),
        push_down=_as_int(stored.get("push_down"), DEFAULT_CONFIG.push_down, 0, 300),
    )


def _load_raw_config() -> dict[str, object]:
    try:
        loaded = mw.addonManager.getConfig(__name__)
        if isinstance(loaded, dict):
            return dict(loaded)
    except Exception as exc:
        _log(exc)
    return {}


def save_config(cfg: Config) -> None:
    # Start from the existing stored config so we never clobber keys we
    # don't manage here (e.g. "_meta").
    data = _load_raw_config()
    data["theme"] = cfg.theme
    data["effects_enabled"] = cfg.effects_enabled
    data["push_down"] = cfg.push_down
    mw.addonManager.writeConfig(__name__, data)


def is_welcome_shown() -> bool:
    data = _load_raw_config()
    meta = data.get(constants.CONFIG_KEY_META)
    if isinstance(meta, dict):
        return bool(meta.get(constants.META_KEY_WELCOME_SHOWN, False))
    return False


def mark_welcome_shown() -> None:
    data = _load_raw_config()
    meta = data.get(constants.CONFIG_KEY_META)
    if not isinstance(meta, dict):
        meta = {}
    meta[constants.META_KEY_WELCOME_SHOWN] = True
    data[constants.CONFIG_KEY_META] = meta
    mw.addonManager.writeConfig(__name__, data)
