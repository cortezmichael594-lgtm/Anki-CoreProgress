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

import os

from aqt import mw
from aqt.qt import (
    QDesktopServices,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPixmap,
    QPushButton,
    QTimer,
    QUrl,
    QVBoxLayout,
    QWidget,
    Qt,
    qconnect,
)

from . import constants
from .i18n import t
from .settings import is_welcome_shown, mark_welcome_shown


def _log(exc: Exception) -> None:
    print(f"[{constants.ADDON_NAME}] {exc!r}")


def _open_url(url: str) -> None:
    try:
        QDesktopServices.openUrl(QUrl(url))
    except Exception as exc:
        _log(exc)


def _brand_button(text: str, bg: str, hover: str) -> QPushButton:
    button = QPushButton(text)
    button.setCursor(Qt.CursorShape.PointingHandCursor)
    button.setStyleSheet(
        f"""
        QPushButton {{
            background-color: {bg};
            color: white;
            border: none;
            border-radius: 6px;
            padding: 6px 14px;
            font-weight: 600;
        }}
        QPushButton:hover {{
            background-color: {hover};
        }}
        """
    )
    return button


class WelcomeDialog(QWidget):
    """One-time welcome/support dialog shown after the first launch."""

    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent, Qt.WindowType.Dialog)
        self.setWindowTitle(constants.ADDON_DISPLAY_NAME)
        self.setMinimumWidth(420)

        layout = QVBoxLayout()

        logo_path = os.path.join(os.path.dirname(__file__), constants.LOGO_FILENAME)
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            if not pixmap.isNull():
                logo_label = QLabel()
                logo_label.setPixmap(
                    pixmap.scaled(
                        constants.LOGO_SIZE_PX,
                        constants.LOGO_SIZE_PX,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                )
                logo_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                layout.addWidget(logo_label)

        title = QLabel(
            t("welcome_title").format(name=constants.ADDON_NAME, version=constants.ADDON_VERSION)
        )
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        title.setStyleSheet(f"font-weight: bold; font-size: 15px; color: {constants.COLOR_ACCENT};")
        layout.addWidget(title)

        by_line = QLabel(f"by {constants.AUTHOR_NAME}")
        by_line.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        by_line.setStyleSheet("color: gray; font-size: 11px;")
        layout.addWidget(by_line)

        body = QLabel(t("welcome_body").format(name=constants.ADDON_NAME))
        body.setWordWrap(True)
        layout.addWidget(body)

        note = QLabel(t("welcome_support_note"))
        note.setWordWrap(True)
        note.setStyleSheet("color: gray; font-size: 11px;")
        layout.addWidget(note)

        buttons_row = QHBoxLayout()

        kofi = _brand_button(t("kofi_button"), constants.COLOR_KOFI_BG, constants.COLOR_KOFI_HOVER)
        kofi.setToolTip(t("kofi_tooltip"))
        qconnect(kofi.clicked, lambda: _open_url(constants.URL_KOFI))
        buttons_row.addWidget(kofi)

        patreon = _brand_button(
            t("patreon_button"), constants.COLOR_PATREON_BG, constants.COLOR_PATREON_HOVER
        )
        qconnect(patreon.clicked, lambda: _open_url(constants.URL_PATREON))
        buttons_row.addWidget(patreon)

        if constants.ANKIWEB_ID:
            rate = _brand_button(t("rate_button"), constants.COLOR_RATE_BG, constants.COLOR_RATE_HOVER)
            qconnect(rate.clicked, lambda: _open_url(constants.ANKIWEB_REVIEW_URL))
            buttons_row.addWidget(rate)

        layout.addLayout(buttons_row)

        close_button = QPushButton(t("welcome_close"))
        close_button.setDefault(True)
        close_button.setAutoDefault(True)
        qconnect(close_button.clicked, self.close)
        layout.addWidget(close_button)
        close_button.setFocus()

        self.setLayout(layout)


def maybe_show_welcome() -> None:
    try:
        if is_welcome_shown():
            return
        mark_welcome_shown()
        QTimer.singleShot(constants.WELCOME_DELAY_MS, _show_welcome_dialog)
    except Exception as exc:
        _log(exc)


def _show_welcome_dialog() -> None:
    try:
        dialog = WelcomeDialog(mw)
        dialog.show()
        # Keep a reference so it isn't garbage-collected immediately.
        mw._coreprogress_welcome_dialog = dialog  # type: ignore[attr-defined]
    except Exception as exc:
        _log(exc)


def build_support_row(parent: QWidget) -> QWidget:
    """Sober footer row for the settings dialog: no colors, plain buttons."""
    row = QWidget(parent)
    layout = QHBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)

    info_label = QLabel(
        f'{t("version_line").format(name=constants.ADDON_NAME, version=constants.ADDON_VERSION)}'
        f' · <a href="{constants.URL_REPORT_BUG}">{t("report_button")}</a>'
    )
    info_label.setOpenExternalLinks(True)
    info_label.setStyleSheet("color: gray; font-size: 11px;")
    layout.addWidget(info_label)
    layout.addStretch()

    kofi = QPushButton(t("kofi_button"))
    qconnect(kofi.clicked, lambda: _open_url(constants.URL_KOFI))
    layout.addWidget(kofi)

    patreon = QPushButton(t("patreon_button"))
    qconnect(patreon.clicked, lambda: _open_url(constants.URL_PATREON))
    layout.addWidget(patreon)

    if constants.ANKIWEB_ID:
        rate = QPushButton(t("rate_button"))
        qconnect(rate.clicked, lambda: _open_url(constants.ANKIWEB_REVIEW_URL))
        layout.addWidget(rate)

    row.setLayout(layout)
    return row


def build_support_separator(parent: QWidget) -> QFrame:
    line = QFrame(parent)
    line.setFrameShape(QFrame.Shape.HLine)
    line.setFrameShadow(QFrame.Shadow.Sunken)
    return line
