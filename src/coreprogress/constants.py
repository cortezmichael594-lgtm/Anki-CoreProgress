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

ADDON_NAME: str = "CoreProgress"
ADDON_DISPLAY_NAME: str = "CoreProgress — Animated progress bar for Anki (by AnkiCraft)"
ADDON_VERSION: str = "1.0.0"

AUTHOR_NAME: str = "AnkiCraft"

ANKIWEB_ID: str = "1712537288"
ANKIWEB_PAGE_URL: str = f"https://ankiweb.net/shared/info/{ANKIWEB_ID}"
ANKIWEB_REVIEW_URL: str = f"https://ankiweb.net/shared/review/{ANKIWEB_ID}"

URL_KOFI: str = "https://ko-fi.com/ankicraft"
URL_PATREON: str = "https://www.patreon.com/cw/Ankicraft594"
URL_REPORT_BUG: str = ANKIWEB_PAGE_URL

LOGO_FILENAME: str = "logo.png"
LOGO_SIZE_PX: int = 72

# AnkiCraft brand palette
COLOR_ACCENT: str = "#7C5CE0"
COLOR_KOFI_BG: str = "#29ABE0"
COLOR_KOFI_HOVER: str = "#1E8FBF"
COLOR_PATREON_BG: str = "#FF424D"
COLOR_PATREON_HOVER: str = "#E0313C"
COLOR_RATE_BG: str = "#F5A623"
COLOR_RATE_HOVER: str = "#D98E12"

CONFIG_KEY_META: str = "_meta"
META_KEY_WELCOME_SHOWN: str = "welcome_shown"
WELCOME_DELAY_MS: int = 2000
