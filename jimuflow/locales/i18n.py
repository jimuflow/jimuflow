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

import gettext as gt
import locale

from jimuflow.common import app_base_path

gettext = None
ngettext = None

locale.setlocale(locale.LC_ALL, '')
current_locale, encoding = locale.getlocale()
if not current_locale or current_locale == 'Chinese (Simplified)_China':
    current_locale = 'zh_CN'


try:
    translation = gt.translation('messages', app_base_path / 'locales', [current_locale])
    if translation:
        translation.install()
        gettext = translation.gettext
        ngettext = translation.ngettext
except FileNotFoundError as e:
    print(e)
    pass
if not gettext:
    gettext = gt.gettext
    ngettext = gt.ngettext
    print(f'No translation found for {current_locale}')
