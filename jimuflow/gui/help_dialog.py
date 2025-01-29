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

import sys
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer
from pathlib import Path

from PySide6.QtCore import Slot, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox, QPushButton

from jimuflow.gui.web_view_utils import setup_web_view_actions
from jimuflow.locales.i18n import gettext


class HelpHTTPRequestHandler(SimpleHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        if getattr(sys, 'frozen', False):
            # 如果是打包后的程序
            directory = Path(sys._MEIPASS) / 'jimuflow' / 'site'
        else:
            # 如果是开发模式
            directory = Path(__file__).parent.parent.parent / 'site'

        super().__init__(*args, directory=str(directory), **kwargs)


class HelpHTTPServer:
    def __init__(self):
        self.server = HTTPServer(('localhost', 0), HelpHTTPRequestHandler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()


class HelpDialog(QDialog):
    SINGLETON = None

    def __init__(self):
        super().__init__()
        HelpDialog.SINGLETON = self
        self.setWindowTitle(gettext("Help"))
        layout = QVBoxLayout()
        self._web_view = QWebEngineView()
        self._web_view.titleChanged.connect(self._on_title_changed)
        self._web_view.setMinimumSize(QSize(1000, 500))
        setup_web_view_actions(self._web_view)
        layout.addWidget(self._web_view)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.close)
        button_box.button(QDialogButtonBox.StandardButton.Close).setText(gettext('Close'))
        back_button = QPushButton(QIcon.fromTheme(QIcon.ThemeIcon.GoPrevious), gettext('Back'))
        back_button.setDisabled(True)
        back_button.clicked.connect(self._back)
        forward_button = QPushButton(QIcon.fromTheme(QIcon.ThemeIcon.GoNext), gettext('Forward'))
        forward_button.setDisabled(True)
        forward_button.clicked.connect(self._forward)
        button_box.addButton(back_button, QDialogButtonBox.ButtonRole.ActionRole)
        button_box.addButton(forward_button, QDialogButtonBox.ButtonRole.ActionRole)
        self._web_view.pageAction(QWebEnginePage.WebAction.Back).enabledChanged.connect(
            lambda enabled: back_button.setDisabled(not enabled))
        self._web_view.pageAction(QWebEnginePage.WebAction.Forward).enabledChanged.connect(
            lambda enabled: forward_button.setDisabled(not enabled))
        layout.addWidget(button_box)

        self.setLayout(layout)

        self._server = HelpHTTPServer()
        self._base_uri = f'http://localhost:{self._server.server.server_port}'

    def load(self, url: str):
        self.show()
        self.raise_()
        self.activateWindow()
        if '://' in url:
            self._web_view.load(url)
        else:
            self._web_view.load(self._base_uri + '/' + url)

    def _back(self):
        self._web_view.back()

    def _forward(self):
        self._web_view.forward()

    @classmethod
    def show_help(cls, url: str):
        if cls.SINGLETON:
            cls.SINGLETON.load(url)
        else:
            HelpDialog().load(url)

    @Slot(str)
    def _on_title_changed(self, title):
        self.setWindowTitle(title + ' - ' + gettext("Help"))

    @classmethod
    def dispose(cls):
        if cls.SINGLETON:
            cls.SINGLETON.close()
            cls.SINGLETON.deleteLater()
            cls.SINGLETON = None
