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

from jimuflow.common import app_base_path
from jimuflow.locales.settings import get_current_locale

gettext = None
ngettext = None

current_locale = get_current_locale()
if current_locale == 'en_US':
    gettext = gt.gettext
    ngettext = gt.ngettext
else:
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
