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

import json

from PySide6.QtCore import Slot, QSize, QDateTime, QTimeZone
from PySide6.QtGui import QStandardItemModel, QStandardItem, Qt
from PySide6.QtNetwork import QNetworkCookie
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, \
    QGridLayout, QApplication, QDialogButtonBox, QTableView, QAbstractItemView, QSplitter

from jimuflow.locales.i18n import gettext


class WebCookieTool(QDialog):
    last_url = ''

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(gettext('Web Cookie Tool'))
        self.accepted_xpath = ''
        main_layout = QVBoxLayout()
        top_layout = QGridLayout()
        url_label = QLabel(gettext('URL: '))
        url_editor = QLineEdit()
        url_editor.setPlaceholderText(
            gettext('Please enter the URL'))
        if WebCookieTool.last_url:
            url_editor.setText(WebCookieTool.last_url)
        open_button = QPushButton(gettext('Open'))
        open_button.clicked.connect(self._open_url)
        top_layout.addWidget(url_label, 0, 0, 1, 1)
        top_layout.addWidget(url_editor, 0, 1, 1, 1)
        top_layout.addWidget(open_button, 0, 2, 1, 1)
        main_layout.addLayout(top_layout, 0)
        splitter = QSplitter(Qt.Orientation.Vertical)
        web_view = QWebEngineView()
        web_view.page().profile().cookieStore().cookieAdded.connect(self._on_cookie_added)
        web_view.page().profile().cookieStore().cookieRemoved.connect(self._on_cookie_removed)
        web_view.loadFinished.connect(self._on_load_finished)
        splitter.addWidget(web_view)
        table_view = QTableView()
        table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        list_model = QStandardItemModel()
        list_model.setHorizontalHeaderLabels(
            ['Name', 'Value', 'Domain', 'Path', 'Expires', 'HttpOnly', 'Secure', 'SameSite'])
        table_view.setModel(list_model)
        table_view.setColumnWidth(0, 150)
        table_view.setColumnWidth(1, 250)
        table_view.setColumnWidth(2, 120)
        table_view.setColumnWidth(3, 90)
        table_view.setColumnWidth(4, 140)
        table_view.setColumnWidth(5, 60)
        table_view.setColumnWidth(6, 60)
        table_view.setColumnWidth(7, 60)
        splitter.addWidget(table_view)
        splitter.setSizes([500, 200])
        main_layout.addWidget(splitter, 1)
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self._on_ok)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.StandardButton.Ok).setText(gettext('Ok'))
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setText(gettext('Cancel'))
        main_layout.addWidget(button_box, 0)
        self.setLayout(main_layout)
        self._url_editor = url_editor
        self._web_view = web_view
        self._list_model = list_model
        self._table_view = table_view
        self.resize(QSize(1200, 700))
        self.cookies = ''

    @Slot()
    def _open_url(self):
        url = self._url_editor.text().strip()
        if not url:
            return
        self._web_view.load(url)
        WebCookieTool.last_url = url

    @Slot(bool)
    def _on_load_finished(self, ok: bool):
        pass

    @Slot(QNetworkCookie)
    def _on_cookie_added(self, cookie: QNetworkCookie):
        name = QStandardItem(cookie.name().toStdString())
        name.setData(name.text(), Qt.ItemDataRole.ToolTipRole)
        name.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
        value = QStandardItem(cookie.value().toStdString())
        value.setData(value.text(), Qt.ItemDataRole.ToolTipRole)
        domain = QStandardItem(cookie.domain())
        domain.setData(domain.text(), Qt.ItemDataRole.ToolTipRole)
        domain.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
        path = QStandardItem(cookie.path())
        path.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
        path.setData(path.text(), Qt.ItemDataRole.ToolTipRole)
        expires_text = cookie.expirationDate().toString(
            'yyyy-MM-dd hh:mm.ss') if cookie.expirationDate().isValid() else 'Session'
        expires = QStandardItem(expires_text)
        expires.setData(expires.text(), Qt.ItemDataRole.ToolTipRole)
        expires.setData(cookie.expirationDate(), Qt.ItemDataRole.UserRole)
        expires.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
        http_only = QStandardItem('✓' if cookie.isHttpOnly() else '')
        http_only.setData(cookie.isHttpOnly(), Qt.ItemDataRole.UserRole)
        http_only.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
        secure = QStandardItem('✓' if cookie.isSecure() else '')
        secure.setData(cookie.isSecure(), Qt.ItemDataRole.UserRole)
        secure.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
        if cookie.sameSitePolicy() == QNetworkCookie.SameSite.None_:
            same_site = QStandardItem('None')
        elif cookie.sameSitePolicy() == QNetworkCookie.SameSite.Lax:
            same_site = QStandardItem('Lax')
        elif cookie.sameSitePolicy() == QNetworkCookie.SameSite.Strict:
            same_site = QStandardItem('Strict')
        else:
            same_site = QStandardItem('')
        same_site.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
        self._list_model.appendRow([name, value, domain, path, expires, http_only, secure, same_site])

    @Slot(QNetworkCookie)
    def _on_cookie_removed(self, cookie: QNetworkCookie):
        for i in range(self._list_model.rowCount()):
            name = self._list_model.item(i, 0).text()
            domain = self._list_model.item(i, 2).text()
            path = self._list_model.item(i, 3).text()
            if name == cookie.name().toStdString() and domain == cookie.domain() and path == cookie.path():
                self._list_model.removeRow(i)
                break

    @Slot()
    def _on_ok(self):
        cookies = []
        for index in self._table_view.selectionModel().selectedRows():
            row = index.row()
            cookie = {
                "name": self._list_model.item(row, 0).text(),
                "value": self._list_model.item(row, 1).text(),
                "domain": self._list_model.item(row, 2).text(),
                "path": self._list_model.item(row, 3).text(),
                "httpOnly": self._list_model.item(row, 5).data(Qt.ItemDataRole.UserRole),
                "secure": self._list_model.item(row, 6).data(Qt.ItemDataRole.UserRole),
            }
            expires: QDateTime = self._list_model.item(row, 4).data(Qt.ItemDataRole.UserRole)
            if expires.isValid():
                cookie['expires'] = expires.toTimeZone(QTimeZone.systemTimeZone()).toString(Qt.DateFormat.ISODateWithMs)
            same_site = self._list_model.item(row, 7).text()
            if same_site:
                cookie['sameSite'] = same_site
            cookies.append(cookie)
        self.cookies = json.dumps(cookies, ensure_ascii=False)
        self.accept()


if __name__ == '__main__':
    app = QApplication()
    tool = WebCookieTool()
    tool.show()
    app.exec()
