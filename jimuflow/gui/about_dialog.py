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
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QDialogButtonBox

import jimuflow
from jimuflow.locales.i18n import gettext


class AboutDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(gettext("About JimuFlow"))
        layout = QVBoxLayout()

        layout.addWidget(self.__create_label(gettext("JimuFlow is a simple and easy-to-use cross-platform RPA tool.")))
        layout.addWidget(self.__create_label(gettext("Version: {version}").format(version=jimuflow.__version__)))
        layout.addWidget(self.__create_label(
            gettext("Git Info: {git_info}").format(git_info=f'{jimuflow.__git_tag__} {jimuflow.__git_commit_date__}')))
        layout.addWidget(self.__create_link_label(
            gettext("Project Link: <a href='{link_url}'>{link_name}</a>").format(
                link_url="https://github.com/jimuflow/jimuflow", link_name="https://github.com/jimuflow/jimuflow")))
        layout.addWidget(self.__create_label("Copyright (C) 2024-2025  Weng Jing"))
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.close)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def __create_label(self, text):
        label = QLabel(text)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        return label

    def __create_link_label(self, text):
        label = QLabel(text)
        label.setTextFormat(Qt.TextFormat.RichText)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        label.setOpenExternalLinks(True)
        return label
