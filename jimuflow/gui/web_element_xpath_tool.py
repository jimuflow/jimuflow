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

from collections import defaultdict

from PySide6.QtCore import Slot, QSize, QEvent, Qt, QObject
from PySide6.QtGui import QMouseEvent
from PySide6.QtWebEngineCore import QWebEngineScript
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, \
    QGridLayout, QTabWidget, QWidget, QApplication

from jimuflow.gui.utils import Utils
from jimuflow.gui.web_view_utils import setup_web_view_actions
from jimuflow.locales.i18n import gettext

preload_js = """
function getXPath(element) {
    if (element === document.body) {
        return '/html/body';
    }
    let ix = 0;
    let siblings = element.parentNode.childNodes;
    for (let i = 0; i < siblings.length; i++) {
        let sibling = siblings[i];
        if (sibling === element) {
            return getXPath(element.parentNode) + '/' + element.tagName.toLowerCase() + '[' + (ix + 1) + ']';
        }
        if (sibling.nodeType === 1 && sibling.tagName === element.tagName) {
            ix++;
        }
    }
}
"""
css = """
.qt-highlight-hover {
    box-shadow: 0 0 10px rgba(255, 165, 0, 0.8) !important;
}
.qt-highlight-selected {
    box-shadow: 0 0 10px rgba(255, 165, 0, 0.8) !important;
}
"""
after_load_js = f"""
var style = document.createElement('style');
style.type = 'text/css';
style.appendChild(document.createTextNode(`{css}`));
document.head.appendChild(style);
document.body.addEventListener('mouseover', (event) => {{
    if (event.target !== document.body) {{
        event.target.classList.add('qt-highlight-hover');
    }}
}}, true);
document.body.addEventListener('mouseout', (event) => {{
    event.target.classList.remove('qt-highlight-hover');
}}, true);
"""


class XPathSelection(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_list = []
        self.finished = False


def merge_xpath(xpath_list: list[str]) -> str:
    if len(xpath_list) == 1:
        return xpath_list[0]
    processed_xpath_list = []
    for xpath in xpath_list:
        arr = xpath.split('|')
        for i in arr:
            processed_xpath_list.append([p.strip() for p in i.strip().split('/')])
    group_by_merged_xpath = defaultdict(list)
    merged_xpath_list = []
    for xpath1 in processed_xpath_list:
        if xpath1 in merged_xpath_list:
            continue
        found_match = False
        for xpath2 in processed_xpath_list:
            if xpath2 == xpath1 or len(xpath1) != len(xpath2):
                continue
            merged_xpath = []
            idx_mismatch_times = 0
            for i in range(len(xpath1)):
                if xpath1[i] == xpath2[i]:
                    merged_xpath.append(xpath1[i])
                elif idx_mismatch_times > 0:
                    break
                else:
                    tag1, idx1 = parse_path_node(xpath1[i])
                    tag2, idx2 = parse_path_node(xpath2[i])
                    if tag1 != tag2:
                        break
                    idx_mismatch_times = 1
                    merged_xpath.append(tag1)
            if len(merged_xpath) != len(xpath1):
                continue
            merged_xpath = '/'.join(merged_xpath)
            group_by_merged_xpath[merged_xpath].append(xpath1)
            group_by_merged_xpath[merged_xpath].append(xpath2)
            merged_xpath_list.append(xpath1)
            merged_xpath_list.append(xpath2)
            found_match = True
            break
        if not found_match:
            group_by_merged_xpath['/'.join(xpath1)].append(xpath1)
    return ' | '.join([k for k in group_by_merged_xpath.keys()])


def parse_path_node(node: str):
    idx1 = node.find('[')
    if idx1 == -1:
        return node, None
    idx2 = node.rfind(']')
    if idx2 != len(node) - 1:
        return node, None
    return node[:idx1], node[idx1 + 1:idx2]


class WebElementXpathTool(QDialog):
    last_url = ''

    def __init__(self, init_xpath='', url='', parent=None):
        super().__init__(parent)
        self.setWindowTitle(gettext('Web Element XPath Tool'))
        self.accepted_xpath = ''
        self._init_xpath = init_xpath
        main_layout = QVBoxLayout()
        top_layout = QGridLayout()
        url_label = QLabel(gettext('URL: '))
        url_editor = QLineEdit()
        url_editor.setPlaceholderText(
            gettext('Please enter the URL where the web page element you want to get is located.'))
        if WebElementXpathTool.last_url:
            url_editor.setText(WebElementXpathTool.last_url)
        open_button = QPushButton(gettext('Open'))
        open_button.clicked.connect(self._open_url)
        top_layout.addWidget(url_label, 0, 0, 1, 1)
        top_layout.addWidget(url_editor, 0, 1, 1, 1)
        top_layout.addWidget(open_button, 0, 2, 1, 1)
        main_layout.addLayout(top_layout)
        tab_widget = QTabWidget()
        tab_widget.setTabsClosable(True)
        tab_widget.tabCloseRequested.connect(self._close_tab)
        main_layout.addWidget(tab_widget)
        bottom_layout = QGridLayout()
        merged_xpath_label = QLabel(gettext('Merged XPath: '))
        merged_xpath_edit = QLineEdit()
        merged_xpath_edit.setPlaceholderText(gettext('Click the merge button to merge the XPath on all tabs'))
        if init_xpath:
            merged_xpath_edit.setText(init_xpath)
        self._merged_xpath_edit = merged_xpath_edit
        merge_button = QPushButton(gettext('Merge'))
        merge_button.setToolTip(gettext('Merge XPath on all tabs'))
        merge_button.clicked.connect(self._merge_all_xpaths)
        match_button = QPushButton(gettext('Match'))
        match_button.setToolTip(gettext('Match the merged XPath on the current tab'))
        match_button.clicked.connect(self._match_all)
        copy_button = QPushButton(gettext('Copy'))
        copy_button.setToolTip(gettext('Copy the merged XPath to clipboard'))
        copy_button.clicked.connect(self._copy_xpath)
        accept_button = QPushButton(gettext('Accept'))
        accept_button.setToolTip(gettext('Accept the merged XPath and close the dialog'))
        accept_button.clicked.connect(self._accept_merged_xpath)
        close_button = QPushButton(gettext('Close'))
        close_button.clicked.connect(self.reject)
        bottom_layout.addWidget(merged_xpath_label, 0, 0, 1, 1)
        bottom_layout.addWidget(merged_xpath_edit, 0, 1, 1, 1)
        bottom_layout.addWidget(merge_button, 0, 2, 1, 1)
        bottom_layout.addWidget(match_button, 0, 3, 1, 1)
        bottom_layout.addWidget(copy_button, 0, 4, 1, 1)
        bottom_layout.addWidget(accept_button, 0, 5, 1, 1)
        bottom_layout.addWidget(close_button, 0, 6, 1, 1)
        main_layout.addLayout(bottom_layout)
        self.setLayout(main_layout)
        self._tab_widget = tab_widget
        self._url_editor = url_editor
        self.resize(QSize(1200, 700))

    @Slot()
    def _open_url(self):
        url = self._url_editor.text().strip()
        if not url:
            return
        tab_content_widget = QWidget()
        tab_content_widget.setProperty('customData', XPathSelection(tab_content_widget))
        tab_content_widget.setObjectName('tabContentWidget')
        tab_content_layout = QVBoxLayout()
        web_view = QWebEngineView()
        setup_web_view_actions(web_view)
        web_view.loadFinished.connect(self._on_load_finished)
        web_view.setObjectName('webView')
        web_view.titleChanged.connect(self._on_title_changed)
        script = QWebEngineScript()
        script.setWorldId(QWebEngineScript.ScriptWorldId.UserWorld)
        script.setSourceCode(preload_js)
        script.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentCreation)
        web_view.page().scripts().insert(script)
        script = QWebEngineScript()
        script.setWorldId(QWebEngineScript.ScriptWorldId.UserWorld)
        script.setSourceCode(after_load_js)
        script.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentReady)
        web_view.page().scripts().insert(script)
        tab_content_layout.addWidget(web_view, 1)
        help_label = QLabel(gettext(
            'Operation instructions: Ctrl+left-click to get a single element, and Shift+left-click two elements to get multiple similar elements.'))
        tab_content_layout.addWidget(help_label)
        tab_content_bottom_layout = QGridLayout()
        xpath_label = QLabel(gettext('XPath: '))
        xpath_edit = QLineEdit()
        xpath_edit.setObjectName('xpathEdit')
        if self._init_xpath:
            xpath_edit.setText(self._init_xpath)
        matches_count_label = QLabel()
        matches_count_label.setObjectName('matchesCountLabel')
        match_button = QPushButton(gettext('Match'))
        match_button.setToolTip(gettext('Match the XPath on the current tab'))
        match_button.clicked.connect(self._on_match_button_clicked)
        accept_button = QPushButton(gettext('Accept'))
        accept_button.setToolTip(gettext('Accept the XPath and close the dialog'))
        accept_button.clicked.connect(self._accept_current_xpath)
        self._set_matches_count(matches_count_label, 0)
        tab_content_bottom_layout.addWidget(xpath_label, 0, 0, 1, 1)
        tab_content_bottom_layout.addWidget(xpath_edit, 0, 1, 1, 1)
        tab_content_bottom_layout.addWidget(matches_count_label, 0, 2, 1, 1)
        tab_content_bottom_layout.addWidget(match_button, 0, 3, 1, 1)
        tab_content_bottom_layout.addWidget(accept_button, 0, 4, 1, 1)
        tab_content_layout.addLayout(tab_content_bottom_layout)
        tab_content_widget.setLayout(tab_content_layout)
        self._tab_widget.addTab(tab_content_widget, gettext("New tab"))
        self._tab_widget.setCurrentWidget(tab_content_widget)
        web_view.load(url)
        web_view.focusProxy().installEventFilter(self)
        WebElementXpathTool.last_url = url

    @Slot(bool)
    def _on_load_finished(self, ok):
        web_view = self.sender()
        # 初始化时installEventFilter和脚本注入可能会失败，具体原因不明，所以在页面加载完成之后再尝试一遍
        web_view.focusProxy().installEventFilter(self)
        web_view.page().runJavaScript(preload_js, QWebEngineScript.ScriptWorldId.UserWorld)
        web_view.page().runJavaScript(after_load_js, QWebEngineScript.ScriptWorldId.UserWorld)

    @Slot(int)
    def _close_tab(self, index: int):
        self._tab_widget.removeTab(index)

    @Slot(str)
    def _on_title_changed(self, title):
        tab_content_widget = Utils.find_ancestor(self.sender(), 'tabContentWidget')
        index = self._tab_widget.indexOf(tab_content_widget)
        self._tab_widget.setTabToolTip(index, title)
        if len(title) > 20:
            title = title[:20] + '...'
        self._tab_widget.setTabText(index, title)

    def eventFilter(self, watched, event):
        if event.type() == QEvent.Type.MouseButtonPress:
            if event.button() == Qt.MouseButton.LeftButton:
                if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                    self._select_element(Utils.find_ancestor(watched, 'webView'), event)
                    return True
                elif event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
                    self._multi_select_element(Utils.find_ancestor(watched, 'webView'), event)
                    return True
        return super().eventFilter(watched, event)

    def _select_element(self, web_view: QWebEngineView, event: QMouseEvent):
        web_view.page().runJavaScript(f'''(function(){{
        const highlightedElements = document.querySelectorAll('.qt-highlight-selected');
        highlightedElements.forEach(element => {{
            element.classList.remove('qt-highlight-selected');
        }});
        const ele = document.elementFromPoint({event.position().x()},{event.position().y()});
        ele.classList.add('qt-highlight-selected');
        return getXPath(ele);
        }})()
        ''', QWebEngineScript.ScriptWorldId.UserWorld, lambda xpath: self._select_xpath(web_view, xpath))

    def _select_xpath(self, web_view: QWebEngineView, xpath: str):
        tab_content_widget = Utils.find_ancestor(web_view, 'tabContentWidget')
        custom_data: XPathSelection = tab_content_widget.property('customData')
        xpath_edit: QLineEdit = tab_content_widget.findChild(QLineEdit, 'xpathEdit')
        custom_data.selected_list = [xpath]
        custom_data.finished = True
        xpath_edit.setText(xpath)
        matches_count_label: QLabel = tab_content_widget.findChild(QLabel, 'matchesCountLabel')
        self._set_matches_count(matches_count_label, 1)

    def _set_matches_count(self, label: QLabel, count: int):
        label.setText(gettext('Matches count: {}').format(count))

    def _multi_select_element(self, web_view: QWebEngineView, event: QMouseEvent):
        tab_content_widget = Utils.find_ancestor(web_view, 'tabContentWidget')
        custom_data: XPathSelection = tab_content_widget.property('customData')
        if custom_data.finished:
            self._clear_selection(web_view)
            custom_data.selected_list = []
            custom_data.finished = False
        web_view.page().runJavaScript(f'''(function(){{
        const ele = document.elementFromPoint({event.position().x()},{event.position().y()});
        ele.classList.add('qt-highlight-selected');
        return getXPath(ele);
        }})()
        ''', QWebEngineScript.ScriptWorldId.UserWorld, lambda xpath: self._multi_select_xpath(web_view, xpath))

    def _clear_selection(self, web_view: QWebEngineView):
        web_view.page().runJavaScript(f'''(function(){{
        const highlightedElements = document.querySelectorAll('.qt-highlight-selected');
        highlightedElements.forEach(element => {{
            element.classList.remove('qt-highlight-selected');
        }});
        }})()
        ''', QWebEngineScript.ScriptWorldId.UserWorld)

    def _multi_select_xpath(self, web_view: QWebEngineView, xpath: str):
        tab_content_widget = Utils.find_ancestor(web_view, 'tabContentWidget')
        custom_data: XPathSelection = tab_content_widget.property('customData')
        xpath_edit: QLineEdit = tab_content_widget.findChild(QLineEdit, 'xpathEdit')
        custom_data.selected_list.append(xpath)
        merged_xpath = merge_xpath(custom_data.selected_list)
        xpath_edit.setText(merged_xpath)
        matches_count_label: QLabel = tab_content_widget.findChild(QLabel, 'matchesCountLabel')
        if len(custom_data.selected_list) >= 2:
            custom_data.finished = True
            self._highlight_element(web_view, merged_xpath, matches_count_label)
        else:
            self._set_matches_count(matches_count_label, 1)

    def _highlight_element(self, web_view: QWebEngineView, xpath: str, matches_count_label: QLabel):
        web_view.page().runJavaScript(f'''(function(){{
                            const xpath = "{xpath}";
                            const result = document.evaluate(xpath, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                            for (let i = 0; i < result.snapshotLength; i++) {{
                                if(i==0){{
                                    result.snapshotItem(i).scrollIntoView();
                                }}
                                result.snapshotItem(i).classList.add('qt-highlight-selected');
                            }}
                            return result.snapshotLength;
                            }})()
                            ''', QWebEngineScript.ScriptWorldId.UserWorld,
                                      lambda count: self._set_matches_count(matches_count_label, int(count)))

    @Slot()
    def _on_match_button_clicked(self):
        tab_content_widget = Utils.find_ancestor(self.sender(), 'tabContentWidget')
        custom_data: XPathSelection = tab_content_widget.property('customData')
        xpath_edit: QLineEdit = tab_content_widget.findChild(QLineEdit, 'xpathEdit')
        web_view: QWebEngineView = tab_content_widget.findChild(QWebEngineView, 'webView')
        matches_count_label: QLabel = tab_content_widget.findChild(QLabel, 'matchesCountLabel')
        xpath = xpath_edit.text().strip()
        self._clear_selection(web_view)
        if xpath:
            self._highlight_element(web_view, xpath, matches_count_label)
            custom_data.selected_list = [xpath]
            custom_data.finished = True
        else:
            custom_data.selected_list = []
            custom_data.finished = True
            self._set_matches_count(matches_count_label, 0)

    @Slot()
    def _merge_all_xpaths(self):
        if self._tab_widget.count() == 0:
            return
        all_xpaths = []
        for i in range(self._tab_widget.count()):
            tab_content_widget = self._tab_widget.widget(i)
            custom_data: XPathSelection = tab_content_widget.property('customData')
            all_xpaths.extend(custom_data.selected_list)
        if len(all_xpaths) == 0:
            return
        merged_xpath = merge_xpath(all_xpaths)
        self._merged_xpath_edit.setText(merged_xpath)

    @Slot()
    def _match_all(self):
        xpath = self._merged_xpath_edit.text().strip()
        if not xpath:
            return
        tab_content_widget = self._tab_widget.currentWidget()
        if not tab_content_widget:
            return
        web_view: QWebEngineView = tab_content_widget.findChild(QWebEngineView, 'webView')
        matches_count_label: QLabel = tab_content_widget.findChild(QLabel, 'matchesCountLabel')
        self._highlight_element(web_view, xpath, matches_count_label)

    @Slot()
    def _copy_xpath(self):
        xpath = self._merged_xpath_edit.text().strip()
        QApplication.clipboard().setText(xpath)

    @Slot()
    def _accept_merged_xpath(self):
        self.accepted_xpath = self._merged_xpath_edit.text().strip()
        self.accept()

    @Slot()
    def _accept_current_xpath(self):
        tab_content_widget = self._tab_widget.currentWidget()
        xpath_edit: QLineEdit = tab_content_widget.findChild(QLineEdit, 'xpathEdit')
        self.accepted_xpath = xpath_edit.text().strip()
        self.accept()


if __name__ == '__main__':
    app = QApplication()
    tool = WebElementXpathTool()
    tool.show()
    app.exec()
