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

from jimuflow.common.constants import APP_VERSION
from jimuflow.locales.i18n import gettext


class AboutDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(gettext("About JimuFlow"))
        layout = QVBoxLayout()

        layout.addWidget(QLabel(gettext("JimuFlow is a simple and easy-to-use cross-platform RPA tool.")))
        layout.addWidget(QLabel(gettext("Version: {version}").format(version=APP_VERSION)))
        project_link_label = QLabel(gettext("Project Link: <a href='{link_url}'>{link_name}</a>").format(
            link_url="https://github.com/jimuflow/jimuflow", link_name="https://github.com/jimuflow/jimuflow"))
        project_link_label.setTextFormat(Qt.TextFormat.RichText)
        project_link_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        project_link_label.setOpenExternalLinks(True)
        layout.addWidget(project_link_label)
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.close)
        layout.addWidget(button_box)

        self.setLayout(layout)
