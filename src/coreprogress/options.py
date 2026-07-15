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

from aqt import mw
from aqt.qt import (
    QCheckBox,
    QColor,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QIcon,
    QPixmap,
    QSpinBox,
    QVBoxLayout,
    QWidget,
    qconnect,
)

from . import constants
from .i18n import t
from .palettes import DEFAULT_THEME, THEME_KEYS, swatch
from .settings import DEFAULT_CONFIG, Config, load_config, save_config
from .support import build_support_row, build_support_separator


def _log(exc: Exception) -> None:
    print(f"[coreprogress] {exc!r}")


def _color_icon(color_hex: str) -> QIcon:
    pixmap = QPixmap(16, 16)
    pixmap.fill(QColor(color_hex))
    return QIcon(pixmap)


class OptionsDialog(QDialog):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setWindowTitle(constants.ADDON_DISPLAY_NAME)
        self.setMinimumWidth(360)
        self._theme = QComboBox()
        for key in THEME_KEYS:
            self._theme.addItem(_color_icon(swatch(key)), t(f"theme_{key}"), key)
        self._push_down = QSpinBox()
        self._push_down.setRange(0, 300)
        self._push_down.setSingleStep(4)
        self._push_down.setSuffix(" px")
        self._effects = QCheckBox(t("opt_effects"))
        form = QFormLayout()
        form.addRow(t("opt_theme"), self._theme)
        form.addRow(t("opt_push"), self._push_down)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
            | QDialogButtonBox.StandardButton.RestoreDefaults
        )
        qconnect(buttons.accepted, self.accept)
        qconnect(buttons.rejected, self.reject)
        save_button = buttons.button(QDialogButtonBox.StandardButton.Save)
        if save_button is not None:
            save_button.setText(t("opt_save"))
        cancel_button = buttons.button(QDialogButtonBox.StandardButton.Cancel)
        if cancel_button is not None:
            cancel_button.setText(t("opt_cancel"))
        restore_button = buttons.button(QDialogButtonBox.StandardButton.RestoreDefaults)
        if restore_button is not None:
            restore_button.setText(t("opt_defaults"))
            qconnect(restore_button.clicked, self._restore_defaults)
        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(self._effects)
        layout.addWidget(buttons)
        layout.addWidget(build_support_separator(self))
        layout.addWidget(build_support_row(self))
        self.setLayout(layout)
        self._apply(load_config())

    def _apply(self, cfg: Config) -> None:
        index = self._theme.findData(cfg.theme)
        self._theme.setCurrentIndex(max(index, 0))
        self._push_down.setValue(cfg.push_down)
        self._effects.setChecked(cfg.effects_enabled)

    def _restore_defaults(self) -> None:
        self._theme.setCurrentIndex(max(self._theme.findData(DEFAULT_CONFIG.theme), 0))
        self._push_down.setValue(DEFAULT_CONFIG.push_down)
        self._effects.setChecked(DEFAULT_CONFIG.effects_enabled)

    def selected_config(self) -> Config:
        theme_data = self._theme.currentData()
        theme = theme_data if isinstance(theme_data, str) and theme_data in THEME_KEYS else DEFAULT_THEME
        return Config(
            theme=theme,
            effects_enabled=self._effects.isChecked(),
            push_down=self._push_down.value(),
        )


def open_options() -> None:
    try:
        from .controller import notify_config_changed

        dialog = OptionsDialog(mw)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            save_config(dialog.selected_config())
            notify_config_changed()
    except Exception as exc:
        _log(exc)


def setup_menu() -> None:
    try:
        if mw is not None:
            mw.addonManager.setConfigAction(__name__, open_options)
    except Exception as exc:
        _log(exc)