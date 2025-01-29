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

from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtWebEngineWidgets import QWebEngineView

from jimuflow.locales.i18n import gettext

gettext('Back')
gettext('Forward')
gettext('Reload')
gettext('Cut')
gettext('Copy')
gettext('Paste')
gettext('Undo')
gettext('Redo')


def setup_web_view_actions(web_view: QWebEngineView):
    for action in QWebEnginePage.WebAction:
        if action == QWebEnginePage.WebAction.NoWebAction or action == QWebEnginePage.WebAction.WebActionCount:
            continue
        act = web_view.pageAction(action)
        if act is None:
            continue
        if (action != QWebEnginePage.WebAction.Back
                and action != QWebEnginePage.WebAction.Forward
                and action != QWebEnginePage.WebAction.Reload
                and action != QWebEnginePage.WebAction.Copy
                and action != QWebEnginePage.WebAction.Cut
                and action != QWebEnginePage.WebAction.Paste
                and action != QWebEnginePage.WebAction.Undo
                and action != QWebEnginePage.WebAction.Redo):
            act.setVisible(False)
        else:
            act.setText(gettext(act.text()))
