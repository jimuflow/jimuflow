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
from typing import Callable

from PySide6.QtCore import Slot, QSize, QEvent, Qt, QTimer, QPointF, QUrl
from PySide6.QtGui import QMouseEvent, QIcon
from PySide6.QtWebEngineCore import QWebEngineScript, QWebEnginePage, QWebEngineFrame, QWebEngineNewWindowRequest
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QVBoxLayout, QLabel, QLineEdit, QPushButton, \
    QGridLayout, QApplication

from jimuflow.common import get_resource_file
from jimuflow.common.web_element_utils import get_relative_xpath, get_full_element_xpath
from jimuflow.gui.dialog_with_webengine import DialogWithWebEngine
from jimuflow.gui.web_element_capture_tool import validate_and_fix_url
from jimuflow.gui.web_view_utils import setup_web_view_actions
from jimuflow.locales.i18n import gettext

preload_js_path = get_resource_file('web_element_capture_preload.js')
with open(preload_js_path, 'r', encoding='utf-8') as f:
    preload_js = f.read()
postload_js_path = get_resource_file('web_element_capture_postload.js')
with open(postload_js_path, 'r', encoding='utf-8') as f:
    after_load_js = f.read()
highlight_source_css_class = 'qt-highlight-source'
highlight_target_css_class = 'qt-highlight-target'


class WebElementRelativeXpathTool(DialogWithWebEngine):
    last_url = ''

    def __init__(self, parent=None):
        super().__init__(parent)
        self._pick_mode = None
        self.setWindowTitle(gettext('Web Element Relative XPath Tool'))
        self.accepted_xpath = ''
        main_layout = QVBoxLayout(self)
        top_layout = QGridLayout()
        url_label = QLabel(gettext('URL: '))
        url_editor = QLineEdit()
        self._url_editor = url_editor
        url_editor.setPlaceholderText(
            gettext('Please enter the URL'))
        if WebElementRelativeXpathTool.last_url:
            url_editor.setText(WebElementRelativeXpathTool.last_url)
        open_button = QPushButton(gettext('Open'))
        open_button.clicked.connect(self._open_url)
        back_button = QPushButton(QIcon.fromTheme(QIcon.ThemeIcon.GoPrevious), '')
        back_button.setDisabled(True)
        self._back_button = back_button
        back_button.clicked.connect(self._back)
        forward_button = QPushButton(QIcon.fromTheme(QIcon.ThemeIcon.GoNext), '')
        forward_button.setDisabled(True)
        self._forward_button = forward_button
        forward_button.clicked.connect(self._forward)
        reload_button = QPushButton(QIcon.fromTheme(QIcon.ThemeIcon.ViewRefresh), '')
        reload_button.setDisabled(False)
        self._reload_button = reload_button
        reload_button.clicked.connect(self._reload)
        top_layout.addWidget(url_label, 0, 0, 1, 1)
        top_layout.addWidget(url_editor, 0, 1, 1, 1)
        top_layout.addWidget(open_button, 0, 2, 1, 1)
        top_layout.addWidget(back_button, 0, 3, 1, 1)
        top_layout.addWidget(forward_button, 0, 4, 1, 1)
        top_layout.addWidget(reload_button, 0, 5, 1, 1)
        main_layout.addLayout(top_layout)
        self._web_view = self._create_web_view()
        main_layout.addWidget(self._web_view, 1)
        help_label = QLabel(gettext(
            'Operation instructions: Ctrl+left-click to capture a single element.'))
        help_label.setVisible(False)
        self._help_label = help_label
        main_layout.addWidget(help_label)

        bottom_layout = QVBoxLayout()
        bottom_layout.setSpacing(0)
        source_element_layout, source_xpath_edit, source_matches_count_label = self._create_source_element_layout()
        bottom_layout.addLayout(source_element_layout)
        self._source_xpath_edit = source_xpath_edit
        self._source_matches_count_label = source_matches_count_label

        target_element_layout, target_xpath_edit, target_matches_count_label = self._create_target_element_layout()
        bottom_layout.addLayout(target_element_layout)
        self._target_xpath_edit = target_xpath_edit
        self._target_matches_count_label = target_matches_count_label

        result_layout, result_xpath_edit = self._create_result_layout()
        bottom_layout.addLayout(result_layout)
        self._result_xpath_edit = result_xpath_edit

        main_layout.addLayout(bottom_layout)

        self.resize(QSize(1200, 700))
        self._iframe_setup_timer = QTimer(self)
        self._iframe_setup_timer.setInterval(500)
        self._iframe_setup_timer.timeout.connect(self._init_all_iframes)
        self._iframe_setup_timer.start()

    def get_web_view(self):
        return self._web_view

    def _create_web_view(self):
        web_view = QWebEngineView()
        setup_web_view_actions(web_view)
        web_view.loadFinished.connect(self._on_load_finished)
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
        web_view.pageAction(QWebEnginePage.WebAction.Back).enabledChanged.connect(
            lambda enabled: self._back_button.setDisabled(not enabled))
        web_view.pageAction(QWebEnginePage.WebAction.Forward).enabledChanged.connect(
            lambda enabled: self._forward_button.setDisabled(not enabled))
        web_view.pageAction(QWebEnginePage.WebAction.Reload).enabledChanged.connect(
            lambda enabled: self._reload_button.setDisabled(not enabled))
        web_view.urlChanged.connect(self._on_url_changed)
        web_view.page().newWindowRequested.connect(self.on_new_window_requested)
        return web_view

    def _back(self):
        self._web_view.back()

    def _forward(self):
        self._web_view.forward()

    def _reload(self):
        self._web_view.reload()

    @Slot(QUrl)
    def _on_url_changed(self, url: QUrl):
        self._url_editor.setText(url.toString())

    @Slot(QWebEngineNewWindowRequest)
    def on_new_window_requested(self, request: QWebEngineNewWindowRequest):
        self._url_editor.setText(request.requestedUrl().toString())
        self._open_url()

    @Slot(bool)
    def _on_load_finished(self, ok):
        web_view = self.sender()
        # 初始化时installEventFilter和脚本注入可能会失败，具体原因不明，所以在页面加载完成之后再尝试一遍
        web_view.focusProxy().installEventFilter(self)
        self._init_all_iframes()

    @Slot()
    def _init_all_iframes(self):
        page: QWebEnginePage = self._web_view.page()
        stack = []
        page.mainFrame().runJavaScript(preload_js, QWebEngineScript.ScriptWorldId.UserWorld)
        page.mainFrame().runJavaScript(after_load_js, QWebEngineScript.ScriptWorldId.UserWorld)
        stack.extend(page.mainFrame().children())
        while stack:
            frame: QWebEngineFrame = stack.pop()
            frame.runJavaScript(preload_js, QWebEngineScript.ScriptWorldId.UserWorld)
            frame.runJavaScript(after_load_js, QWebEngineScript.ScriptWorldId.UserWorld)
            stack.extend(frame.children())

    def _create_source_element_layout(self):
        source_element_layout = QGridLayout()
        source_element_layout.setSpacing(4)
        xpath_label = QLabel(gettext('Source Element XPath: '))
        xpath_edit = QLineEdit()
        xpath_edit.setPlaceholderText(
            gettext('Click the Capture Element button to obtain the XPath of the source element'))
        xpath_edit.editingFinished.connect(self._update_result)
        matches_count_label = QLabel()
        pick_button = QPushButton(gettext('Capture Source Element'))
        pick_button.setToolTip(gettext('Capture the source element'))
        pick_button.clicked.connect(self._pick_source_element_xpath)
        match_button = QPushButton(gettext('Match'))
        match_button.setToolTip(gettext('Match the source element XPath on the current web page'))
        match_button.clicked.connect(self._on_source_match_button_clicked)
        self._set_matches_count(matches_count_label, 0)
        source_element_layout.addWidget(xpath_label, 0, 0, 1, 1)
        source_element_layout.addWidget(xpath_edit, 0, 1, 1, 1)
        source_element_layout.addWidget(matches_count_label, 0, 2, 1, 1)
        source_element_layout.addWidget(pick_button, 0, 3, 1, 1)
        source_element_layout.addWidget(match_button, 0, 4, 1, 1)
        return source_element_layout, xpath_edit, matches_count_label

    @Slot()
    def _pick_source_element_xpath(self):
        self._pick_mode = 'pick_source'
        self._help_label.setVisible(True)

    def _create_target_element_layout(self):
        target_element_layout = QGridLayout()
        target_element_layout.setSpacing(4)
        xpath_label = QLabel(gettext('Target Element XPath: '))
        xpath_edit = QLineEdit()
        xpath_edit.setPlaceholderText(
            gettext('Click the Capture Element button to obtain the XPath of the target element'))
        xpath_edit.editingFinished.connect(self._update_result)
        matches_count_label = QLabel()
        pick_button = QPushButton(gettext('Capture Target Element'))
        pick_button.setToolTip(gettext('Capture the target element'))
        pick_button.clicked.connect(self._pick_target_element_xpath)
        match_button = QPushButton(gettext('Match'))
        match_button.setToolTip(gettext('Match the target element XPath on the current web page'))
        match_button.clicked.connect(self._on_target_match_button_clicked)
        self._set_matches_count(matches_count_label, 0)
        target_element_layout.addWidget(xpath_label, 0, 0, 1, 1)
        target_element_layout.addWidget(xpath_edit, 0, 1, 1, 1)
        target_element_layout.addWidget(matches_count_label, 0, 2, 1, 1)
        target_element_layout.addWidget(pick_button, 0, 3, 1, 1)
        target_element_layout.addWidget(match_button, 0, 4, 1, 1)
        return target_element_layout, xpath_edit, matches_count_label

    @Slot()
    def _pick_target_element_xpath(self):
        self._pick_mode = 'pick_target'
        self._help_label.setVisible(True)

    def _create_result_layout(self):
        result_layout = QGridLayout()
        result_layout.setSpacing(4)
        xpath_label = QLabel(gettext('Relative XPath: '))
        xpath_edit = QLineEdit()
        xpath_edit.setReadOnly(True)
        xpath_edit.setPlaceholderText(gettext('Relative XPath of the target element relative to the source element'))
        accept_button = QPushButton(gettext('Accept'))
        accept_button.setToolTip(gettext('Accept the relative XPath and close the dialog'))
        accept_button.clicked.connect(self._accept_result_xpath)
        close_button = QPushButton(gettext('Close'))
        close_button.clicked.connect(self.reject)
        result_layout.addWidget(xpath_label, 0, 0, 1, 1)
        result_layout.addWidget(xpath_edit, 0, 1, 1, 1)
        result_layout.addWidget(accept_button, 0, 2, 1, 1)
        result_layout.addWidget(close_button, 0, 3, 1, 1)
        return result_layout, xpath_edit

    @Slot()
    def _open_url(self):
        input_url = self._url_editor.text()
        url = validate_and_fix_url(input_url)
        if not url:
            return
        if input_url != url:
            self._url_editor.setText(url)
        self._web_view.load(url)
        self._web_view.focusProxy().installEventFilter(self)
        WebElementRelativeXpathTool.last_url = url

    def eventFilter(self, watched, event):
        if (event.type() == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton
                and event.modifiers() == Qt.KeyboardModifier.ControlModifier):
            if self._pick_mode:
                self._select_element(self._web_view, event)
                return True
        return super().eventFilter(watched, event)

    def _select_element(self, web_view: QWebEngineView, event: QMouseEvent):
        def on_element_captured(element_info: dict):
            self._select_xpath(web_view, element_info['fullXPath'])

        css_class = 'qt-highlight-source' if self._pick_mode == 'pick_source' else 'qt-highlight-target'
        self._capture_element_by_position(web_view, event.position(), css_class, on_element_captured)

    def _capture_element_by_position(self, web_view: QWebEngineView, position: QPointF, css_class,
                                     result_callback: Callable[[dict], None]):
        self._capture_element_in_frame_by_position(web_view, web_view.page().mainFrame(), position, css_class, [],
                                                   result_callback)

    def _capture_element_in_frame_by_position(self, web_view: QWebEngineView, frame: QWebEngineFrame, position: QPointF,
                                              css_class,
                                              captured_elements: list, result_callback: Callable[[dict], None]):
        frame.runJavaScript(f'getElementInfoFromPoint({position.x()}, {position.y()}, "{css_class}")',
                            QWebEngineScript.ScriptWorldId.UserWorld,
                            lambda element_info: self._on_element_captured(web_view, frame, json.loads(element_info),
                                                                           css_class,
                                                                           captured_elements, result_callback))

    def _on_element_captured(self, web_view: QWebEngineView, frame: QWebEngineFrame, element_info: dict, css_class,
                             captured_elements: list, result_callback: Callable[[dict], None]):
        captured_elements.append(element_info)
        if 'iframeId' in element_info:
            def on_frame_id(frame: QWebEngineFrame, frame_id):
                if frame_id != element_info['iframeId']:
                    return
                self._capture_element_in_sub_frame(web_view, frame, element_info, css_class, captured_elements,
                                                   result_callback)

            for subFrame in frame.children():
                self._get_frame_id(subFrame, on_frame_id)
        else:
            merged_rect = None
            merged_iframe_xpath = ''
            merged_iframe_path = []
            for i in range(len(captured_elements)):
                rect = captured_elements[i]['rect']
                if not merged_rect:
                    merged_rect = rect.copy()
                else:
                    merged_rect['x'] = merged_rect['x'] + rect['x']
                    merged_rect['y'] = merged_rect['y'] + rect['y']
                    merged_rect['width'] = rect['width']
                    merged_rect['height'] = rect['height']
                if i < len(captured_elements) - 1:
                    merged_iframe_xpath = merged_iframe_xpath + captured_elements[i]['iframeXPath']
                    merged_iframe_path.extend(captured_elements[i]['iframePath'])
            full_xpath = get_full_element_xpath(captured_elements[-1]['elementPath'])
            final_element_info = {
                "groupName": web_view.title(),
                "groupIcon": web_view.icon(),
                "name": captured_elements[-1]['name'],
                "elementType": captured_elements[-1]['elementType'],
                "iframeXPath": merged_iframe_xpath,
                "elementXPath": captured_elements[-1]['elementXPath'],
                "webPageUrl": captured_elements[0]['webPageUrl'],
                "inIframe": len(captured_elements) > 1,
                "useCustomIframeXPath": False,
                "iframePath": merged_iframe_path,
                "customIframeXPath": '',
                "useCustomElementXPath": False,
                "elementPath": captured_elements[-1]['elementPath'],
                "customElementXPath": '',
                "rect": merged_rect,
                "point": captured_elements[0]['point'],
                "iframeId": captured_elements[-2]["iframeId"] if len(captured_elements) > 1 else None,
                "frame": frame,
                "fullXPath": full_xpath
            }
            result_callback(final_element_info)

    def _get_frame_id(self, frame: QWebEngineFrame, result_callback: Callable[[QWebEngineFrame, str], None]):
        frame.runJavaScript('window.__iframe_id__', QWebEngineScript.ScriptWorldId.UserWorld,
                            lambda frame_id: result_callback(frame, frame_id))

    def _capture_element_in_sub_frame(self, web_view: QWebEngineView, sub_frame: QWebEngineFrame, element_info: dict,
                                      css_class,
                                      captured_elements: list, result_callback: Callable[[dict], None]):
        x_in_sub_frame = element_info['point'][0] - element_info['rect']['x']
        y_in_sub_frame = element_info['point'][1] - element_info['rect']['y']
        self._capture_element_in_frame_by_position(web_view, sub_frame, QPointF(x_in_sub_frame, y_in_sub_frame),
                                                   css_class,
                                                   captured_elements, result_callback)

    def _select_xpath(self, web_view: QWebEngineView, xpath: str):
        if self._pick_mode == 'pick_source':
            self._source_xpath_edit.setText(xpath)
            self._set_matches_count(self._source_matches_count_label, 1)
        else:
            self._target_xpath_edit.setText(xpath)
            self._set_matches_count(self._target_matches_count_label, 1)
        self._update_result()
        self._pick_mode = ''
        self._help_label.setVisible(False)

    @Slot()
    def _update_result(self):
        self._result_xpath_edit.setText(
            get_relative_xpath(self._source_xpath_edit.text(), self._target_xpath_edit.text()))

    def _set_matches_count(self, label: QLabel, count: int):
        label.setText(gettext('Matches count: {}').format(count))

    def _clear_selection(self, css_class: str):
        for frame in self.get_all_frames(self._web_view):
            frame.runJavaScript(f'''(function(){{
            const highlightedElements = document.querySelectorAll('.{css_class}');
            highlightedElements.forEach(element => {{
                element.classList.remove('{css_class}');
            }});
            }})()
            ''', QWebEngineScript.ScriptWorldId.UserWorld)

    def get_all_frames(self, web_view: QWebEngineView):
        stack = [web_view.page().mainFrame()]
        while stack:
            frame = stack.pop()
            yield frame
            stack.extend(frame.children())

    def _highlight_element(self, xpath: str, matches_count_label: QLabel, css_class: str):
        matches = []
        frames = list(self.get_all_frames(self._web_view))

        def on_highlighted(count: int):
            matches.append(count)
            if len(matches) == len(frames):
                self._set_matches_count(matches_count_label, int(sum(matches)))

        for frame in frames:
            frame.runJavaScript(f'highlightElement({json.dumps(xpath, ensure_ascii=False)}, "{css_class}")',
                                QWebEngineScript.ScriptWorldId.UserWorld, on_highlighted)

    @Slot()
    def _on_source_match_button_clicked(self):
        xpath = self._source_xpath_edit.text().strip()
        self._clear_selection(highlight_source_css_class)
        if xpath:
            self._highlight_element(xpath, self._source_matches_count_label, highlight_source_css_class)
        else:
            self._set_matches_count(self._source_matches_count_label, 0)

    @Slot()
    def _on_target_match_button_clicked(self):
        xpath = self._target_xpath_edit.text().strip()
        self._clear_selection(highlight_target_css_class)
        if xpath:
            self._highlight_element(xpath, self._target_matches_count_label, highlight_target_css_class)
        else:
            self._set_matches_count(self._target_matches_count_label, 0)

    @Slot()
    def _accept_result_xpath(self):
        self.accepted_xpath = self._result_xpath_edit.text().strip()
        self.accept()


if __name__ == '__main__':
    app = QApplication()
    tool = WebElementRelativeXpathTool()
    tool.show()
    app.exec()
