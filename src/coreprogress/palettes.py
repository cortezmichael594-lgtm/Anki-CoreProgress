from __future__ import annotations

import json
from dataclasses import dataclass

ACCENT_LIGHT: dict[str, tuple[str, ...]] = {
    "classic_green": (
        "#a6d99e", "#8fd08a", "#77c476", "#60b763", "#4aa852",
        "#379a45", "#278a39", "#1a782e", "#106425", "#0a511d",
    ),
    "fire_red": (
        "#f4a9a0", "#f09287", "#ea7b6e", "#e36557", "#d95043",
        "#cb3f33", "#b93327", "#a2281f", "#881e19", "#6d1613",
    ),
    "lagoon_turquoise": (
        "#9adcd6", "#7dd1cb", "#61c4bf", "#48b5b1", "#35a4a1",
        "#279290", "#1c7f7e", "#146a6a", "#0e5757", "#0a4444",
    ),
    "ocean_blue": (
        "#a3cfec", "#88c1e6", "#6db2df", "#54a2d6", "#4090ca",
        "#2f7ebc", "#226cab", "#185a97", "#104a80", "#0b3a68",
    ),
    "rose_pink": (
        "#f7b3cd", "#f39cbe", "#ee85af", "#e76e9f", "#dd598f",
        "#cf477e", "#bd386c", "#a62c5b", "#8c214a", "#71183a",
    ),
    "royal_purple": (
        "#c9b4ea", "#b8a0e3", "#a78bdb", "#9676d1", "#8562c6",
        "#7450b8", "#6440a8", "#543295", "#452680", "#371c6a",
    ),
    "sunset_orange": (
        "#f6bd8b", "#f3ab70", "#ef9958", "#e98643", "#e07331",
        "#d36123", "#c25118", "#ab4210", "#90350b", "#762b08",
    ),
}

ACCENT_DARK: dict[str, tuple[str, ...]] = {
    "classic_green": (
        "#12482c", "#125532", "#136337", "#15723c", "#1a8340",
        "#219544", "#2ba74a", "#3aba54", "#4ecd62", "#69df78",
    ),
    "fire_red": (
        "#521712", "#621c15", "#742118", "#88281b", "#9c301f",
        "#b13a24", "#c6462b", "#da5535", "#ec6743", "#fb7d55",
    ),
    "lagoon_turquoise": (
        "#0d3c3c", "#11494a", "#155758", "#1a6667", "#207677",
        "#288788", "#33999a", "#41abac", "#55bdbe", "#70cfd0",
    ),
    "ocean_blue": (
        "#123a58", "#154668", "#185378", "#1c6189", "#22709b",
        "#2a80ad", "#3491bf", "#42a3d1", "#55b6e2", "#6fc9f1",
    ),
    "rose_pink": (
        "#5a1734", "#6b1c3e", "#7e2249", "#922955", "#a73162",
        "#bc3b70", "#d0497f", "#e05b91", "#ec73a5", "#f58fba",
    ),
    "royal_purple": (
        "#31205c", "#3a276c", "#44307c", "#4f3a8d", "#5b459e",
        "#6851af", "#775fc1", "#886fd2", "#9a81e2", "#ae95f1",
    ),
    "sunset_orange": (
        "#54260e", "#642d10", "#753512", "#883e15", "#9c4817",
        "#b0531a", "#c45f1e", "#d76d26", "#e97d33", "#f99046",
    ),
}

GOLD_LIGHT: tuple[str, ...] = (
    "#ffe9a8", "#ffdf85", "#f8d264", "#efc23f", "#e3ad1f",
    "#d29910", "#bd8408", "#a06d05", "#845905", "#684606",
)

GOLD_DARK: tuple[str, ...] = (
    "#5a4406", "#6e5408", "#84640a", "#9c760c", "#b58a10",
    "#cf9f16", "#e5b62a", "#f2c944", "#f9d766", "#ffe38c",
)

THEME_KEYS: tuple[str, ...] = tuple(ACCENT_LIGHT)
DEFAULT_THEME: str = "classic_green"

_FILL_IDX_LIGHT: tuple[int, int, int, int] = (4, 5, 6, 7)
_FILL_IDX_DARK: tuple[int, int, int, int] = (5, 6, 7, 8)
_LABEL_BASE_SHADOW: str = "0 1px 3px rgba(0,0,0,.25)"


@dataclass(frozen=True)
class ModeStyle:
    gradient: str
    fill_shadow: str
    solid: str
    label_glow: str


@dataclass(frozen=True)
class StyleBundle:
    light: ModeStyle
    dark: ModeStyle

    def to_json(self) -> str:
        return json.dumps(
            {"light": _mode_dict(self.light), "dark": _mode_dict(self.dark)},
            separators=(",", ":"),
        )


def _mode_dict(mode: ModeStyle) -> dict[str, str]:
    return {"gradient": mode.gradient, "shadow": mode.fill_shadow, "solid": mode.solid, "glow": mode.label_glow}


def _hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)


def _rgba(hex_color: str, alpha: float) -> str:
    r, g, b = _hex_to_rgb(hex_color)
    return f"rgba({r},{g},{b},{alpha:.2f})"


def _scale(theme: str, dark: bool) -> tuple[str, ...]:
    table = ACCENT_DARK if dark else ACCENT_LIGHT
    return table.get(theme, table[DEFAULT_THEME])


def _gold_scale(dark: bool) -> tuple[str, ...]:
    return GOLD_DARK if dark else GOLD_LIGHT


def _gradient(tones: tuple[str, str, str, str]) -> str:
    a, b, c, d = tones
    return f"linear-gradient(90deg,{a} 0%,{b} 30%,{c} 70%,{d} 100%)"


def _gold_glow(dark: bool) -> str:
    scale = _gold_scale(dark)
    outer = scale[7] if dark else scale[5]
    inner = scale[8] if dark else scale[6]
    return f"0 0 12px {_rgba(outer, 0.38)}, 0 0 5px {_rgba(inner, 0.30)}"


def _mode_style(theme: str, dark: bool, gold_active: bool) -> ModeStyle:
    tones = _gold_scale(dark) if gold_active else _scale(theme, dark)
    idx = _FILL_IDX_DARK if dark else _FILL_IDX_LIGHT
    picked = (tones[idx[0]], tones[idx[1]], tones[idx[2]], tones[idx[3]])
    drop_tone = tones[7] if dark else tones[6]
    base_drop = f"0 2px 8px {_rgba(drop_tone, 0.38)}"
    fill_shadow = f"{base_drop}, {_gold_glow(dark)}" if gold_active else base_drop
    solid = tones[8] if dark else tones[7]
    if gold_active:
        gold = _gold_scale(dark)
        label_color = gold[7] if dark else gold[6]
        label_glow = f"{_LABEL_BASE_SHADOW}, 0 0 8px {_rgba(label_color, 0.55)}"
    else:
        label_glow = _LABEL_BASE_SHADOW
    return ModeStyle(gradient=_gradient(picked), fill_shadow=fill_shadow, solid=solid, label_glow=label_glow)


def fill_bundle(theme: str, gold_active: bool) -> StyleBundle:
    return StyleBundle(
        light=_mode_style(theme, dark=False, gold_active=gold_active),
        dark=_mode_style(theme, dark=True, gold_active=gold_active),
    )


def swatch(theme: str) -> str:
    return _scale(theme, dark=False)[6]