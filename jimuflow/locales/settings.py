# This software is dual-licensed under the GNU General Public License (GPL)
# and a commercial license.
#
# You may use this software under the terms of the GNU GPL v3 (or, at your option,
# any later version) as published by the Free Software Foundation. See
# <https://www.gnu.org/licenses/> for details.
#
# If you require a proprietary/commercial license for this software, please
# contact us at jimuflow@gmail.com for more information.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# Copyright (C) 2024-2025  Weng Jing

import locale

settings = {
    "preferred_locale": None
}


def set_preferred_locale(l):
    settings["preferred_locale"] = l


def get_current_locale():
    if settings["preferred_locale"]:
        return settings["preferred_locale"]
    else:
        current_locale = locale.getlocale()[0]
        if not current_locale:
            locale.setlocale(locale.LC_ALL, '')
            current_locale = locale.getlocale()[0]
        if not current_locale or current_locale == 'Chinese (Simplified)_China':
            current_locale = 'zh_CN'
        return current_locale
