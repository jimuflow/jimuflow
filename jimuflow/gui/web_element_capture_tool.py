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
import re
import tempfile
from typing import Callable

from PySide6.QtCore import Slot, QSize, QEvent, Qt, QObject, QRect, QMargins, QTimer, QPointF, QUrl
from PySide6.QtGui import QMouseEvent, QIcon
from PySide6.QtWebEngineCore import QWebEngineScript, QWebEnginePage, QWebEngineFrame
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QVBoxLayout, QLabel, QLineEdit, QPushButton, \
    QGridLayout, QTabWidget, QWidget, QApplication, QMessageBox, QSplitter, QDialogButtonBox

from jimuflow.common import get_resource_file
from jimuflow.common.web_element_utils import build_xpath, parse_xpath
from jimuflow.gui.dialog_with_webengine import DialogWithWebEngine
from jimuflow.gui.utils import Utils
from jimuflow.gui.web_element_editor import WebElementEditor
from jimuflow.gui.web_view_utils import setup_web_view_actions
from jimuflow.locales.i18n import gettext

preload_js_path = get_resource_file('web_element_capture_preload.js')
with open(preload_js_path, 'r', encoding='utf-8') as f:
    preload_js = f.read()
postload_js_path = get_resource_file('web_element_capture_postload.js')
with open(postload_js_path, 'r', encoding='utf-8') as f:
    after_load_js = f.read()

localized_element_types = {
    'Link': gettext('Link'),
    'Abbreviation Text': gettext('Abbreviation Text'),
    'Address': gettext('Address'),
    'Image Map Area': gettext('Image Map Area'),
    'Article Contents': gettext('Article Contents'),
    'Aside': gettext('Aside'),
    'Audio': gettext('Audio'),
    'Text': gettext('Text'),
    'Document Base URL': gettext('Document Base URL'),
    'Block Quotation': gettext('Block Quotation'),
    'DocumentBody': gettext('Document Body'),
    'Line Break': gettext('Line Break'),
    'Button': gettext('Button'),
    'Canvas': gettext('Canvas'),
    'Table Caption': gettext('Table Caption'),
    'Citation': gettext('Citation'),
    'Code': gettext('Code'),
    'Table Column': gettext('Table Column'),
    'Table Column Group': gettext('Table Column Group'),
    'Data': gettext('Data'),
    'Data List': gettext('Data List'),
    'Description Details': gettext('Description Details'),
    'Deleted Text': gettext('Deleted Text'),
    'Details disclosure': gettext('Details disclosure'),
    'Definition': gettext('Definition'),
    'Dialog': gettext('Dialog'),
    'Block Element': gettext('Block Element'),
    'Description List': gettext('Description List'),
    'Description Term': gettext('Description Term'),
    'Emphasis': gettext('Emphasis'),
    'Embedded Content': gettext('Embedded Content'),
    'Fieldset': gettext('Fieldset'),
    'Figure Caption': gettext('Figure Caption'),
    'Figure': gettext('Figure'),
    'Footer': gettext('Footer'),
    'Form': gettext('Form'),
    'First-level title': gettext('First-level title'),
    'Second-level title': gettext('Second-level title'),
    'Third-level title': gettext('Third-level title'),
    'Fourth-level title': gettext('Fourth-level title'),
    'Fifth-level title': gettext('Fifth-level title'),
    'Sixth-level title': gettext('Sixth-level title'),
    'Document Head': gettext('Document Head'),
    'Header': gettext('Header'),
    'Heading Group': gettext('Heading Group'),
    'Horizontal Rule': gettext('Horizontal Rule'),
    'Document': gettext('Document'),
    'Inline Frame': gettext('Inline Frame'),
    'Image': gettext('Image'),
    'Inserted Text': gettext('Inserted Text'),
    'Keyboard Input': gettext('Keyboard Input'),
    'Label': gettext('Label'),
    'Field Set Legend': gettext('Field Set Legend'),
    'List Item': gettext('List Item'),
    'External Resource Link': gettext('External Resource Link'),
    'Main Content': gettext('Main Content'),
    'Image Map': gettext('Image Map'),
    'Mark Text': gettext('Mark Text'),
    'Menu': gettext('Menu'),
    'Metadata': gettext('Metadata'),
    'Meter': gettext('Meter'),
    'Navigation': gettext('Navigation'),
    'Embedded Object': gettext('Embedded Object'),
    'Ordered List': gettext('Ordered List'),
    'Option Group': gettext('Option Group'),
    'Option': gettext('Option'),
    'Output': gettext('Output'),
    'Picture': gettext('Picture'),
    'Preformatted Text': gettext('Preformatted Text'),
    'Progress Indicator': gettext('Progress Indicator'),
    'Inline Quotation': gettext('Inline Quotation'),
    'Script': gettext('Script'),
    'Search': gettext('Search'),
    'Section': gettext('Section'),
    'Drop-down box': gettext('Drop-down box'),
    'Web Component Slot': gettext('Web Component Slot'),
    'Side Comment': gettext('Side Comment'),
    'Media Source': gettext('Media Source'),
    'Style': gettext('Style'),
    'Subscript': gettext('Subscript'),
    'Summary': gettext('Summary'),
    'Superscript': gettext('Superscript'),
    'Table': gettext('Table'),
    'Table Body': gettext('Table Body'),
    'Table Cell': gettext('Table Cell'),
    'Content Template': gettext('Content Template'),
    'Text Area': gettext('Text Area'),
    'Table Footer': gettext('Table Footer'),
    'Table Header Cell': gettext('Table Header Cell'),
    'Table Header': gettext('Table Header'),
    'Time': gettext('Time'),
    'Document Title': gettext('Document Title'),
    'Table Row': gettext('Table Row'),
    'Media Track': gettext('Media Track'),
    'Unordered List': gettext('Unordered List'),
    'Variable': gettext('Variable'),
    'Video': gettext('Video'),
    'Line Break Opportunity': gettext('Line Break Opportunity'),
    'Password Input': gettext('Password Input'),
    'Checkbox': gettext('Checkbox'),
    'Radio Button': gettext('Radio Button'),
    'File Input': gettext('File Input'),
    'Input box': gettext('Input box')
}


class ElementSelection(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_list = []
        self.finished = False


def merge_elements(first: dict, second: dict):
    if first['iframeXPath'] != second['iframeXPath'] or first['elementXPath'] == second['elementXPath'] or len(
            first['elementPath']) != len(second['elementPath']):
        return None
    loop_node_index = -1
    for i in range(len(first['elementPath'])):
        first_node = first['elementPath'][i]
        second_node = second['elementPath'][i]
        if first_node['element'] != second_node['element']:
            return None
        first_node_pred = next((pred for pred in first_node['predicates'] if pred[3]), None)
        second_node_pred = next((pred for pred in second_node['predicates'] if pred[3]), None)
        if first_node_pred != second_node_pred:
            if loop_node_index == -1:
                loop_node_index = i
                first_node['enabled'] = True
                second_node['enabled'] = True
            first_node_pred[3] = False
            second_node_pred[3] = False
            first_node_class_pred = next((pred for pred in first_node['predicates'] if pred[0] == 'class'), None)
            second_node_class_pred = next((pred for pred in second_node['predicates'] if pred[0] == 'class'), None)
            if (first_node_class_pred and second_node_class_pred
                    and first_node_class_pred[2] == second_node_class_pred[2]):
                first_node_class_pred[3] = True
                second_node_class_pred[3] = True

    merged_element = first
    # 重新计算第一个不同点的父节点的XPATH
    element_path = merged_element['elementPath']
    if loop_node_index >= 1:
        for i in range(loop_node_index - 1, -1, -1):
            element_path[i]['enabled'] = True
            enabled_pred = next(pred for pred in element_path[i]['predicates'] if pred[3])
            if enabled_pred[0] == 'id':
                break
    element_type = first['elementType']
    merged_element['name'] = localized_element_types.get(element_type, element_type) + '_' + first['name'] + '_' + \
                             second['name'] + '_' + gettext('Element List')
    merged_element['elementXPath'] = build_xpath(element_path)
    return merged_element


def is_valid_url(url):
    # 定义一个正则表达式，用于检查URL是否合法
    url_pattern = re.compile(
        r'^https?://'  # http或https
        r'([\w.-]+)'  # 域名部分
        r'(\.[a-zA-Z]{2,6})'  # 顶级域名部分
        r'(:\d+)?'  # 可选的端口号
        r'(/.*)?$',  # 可选的路径
        re.IGNORECASE
    )
    return bool(url_pattern.match(url))


def validate_and_fix_url(url):
    if not url:
        return None
    url = url.strip()
    if is_valid_url(url):
        return url  # 如果URL合法，直接返回

    # 如果URL没有以http或https开头，尝试添加https://
    if not url.lower().startswith(('http://', 'https://')):
        url = 'https://' + url

    # 再次校验修复后的URL
    if is_valid_url(url):
        return url

    return None  # 如果修复后仍然不合法，返回None


class WebElementCaptureWebView(QWebEngineView):

    def __init__(self, capture_tool: 'WebElementCaptureTool', parent=None):
        super().__init__(parent)
        self.capture_tool = capture_tool

    def createWindow(self, type):
        return self.capture_tool.add_new_tab('')


class WebElementCaptureTool(DialogWithWebEngine):
    last_url = ''

    def __init__(self, url='', element_info=None, parent=None):
        super().__init__(parent)
        self.element_info = element_info
        self.setWindowTitle(gettext('Web Element Capture Tool'))
        main_layout = QVBoxLayout(self)
        splitter = QSplitter(Qt.Orientation.Vertical)
        tab_widget = QTabWidget()
        tab_widget.setTabsClosable(True)
        tab_widget.tabCloseRequested.connect(self._close_tab)
        splitter.addWidget(tab_widget)
        self._element_editor = WebElementEditor()
        self._element_editor.setVisible(False)
        self._element_editor.check_element_clicked.connect(self._check_element_info)
        splitter.addWidget(self._element_editor)
        splitter.setSizes([500, 300])
        main_layout.addWidget(splitter)
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.StandardButton.Ok).setText(gettext('Ok'))
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setText(gettext('Cancel'))
        main_layout.addWidget(button_box)
        self._tab_widget = tab_widget
        self.resize(QSize(1200, 800))
        self._iframe_setup_timer = QTimer(self)
        self._iframe_setup_timer.setInterval(500)
        self._iframe_setup_timer.timeout.connect(self._init_all_iframes)
        self._iframe_setup_timer.start()
        if element_info:
            self.add_new_tab(element_info['webPageUrl'])
            self._edit_element_info(element_info)
        else:
            self.add_new_tab(url)

    def add_new_tab(self, url: str):
        tab_content_widget = QWidget()
        tab_content_widget.setProperty('customData', ElementSelection(tab_content_widget))
        tab_content_widget.setObjectName('tabContentWidget')
        tab_content_layout = QGridLayout(tab_content_widget)
        url_label = QLabel(gettext('URL: '))
        url_editor = QLineEdit()
        url_editor.setObjectName('urlEditor')
        url_editor.installEventFilter(self)
        url_editor.setPlaceholderText(
            gettext('Please enter the URL where the web page element you want to get is located.'))
        if url:
            url_editor.setText(url)
        open_button = QPushButton(gettext('Open'))
        back_button = QPushButton(QIcon.fromTheme(QIcon.ThemeIcon.GoPrevious), '')
        back_button.setDisabled(True)
        back_button.clicked.connect(self._back)
        forward_button = QPushButton(QIcon.fromTheme(QIcon.ThemeIcon.GoNext), '')
        forward_button.setDisabled(True)
        forward_button.clicked.connect(self._forward)
        reload_button = QPushButton(QIcon.fromTheme(QIcon.ThemeIcon.ViewRefresh), '')
        reload_button.setDisabled(False)
        reload_button.clicked.connect(self._reload)
        tab_content_layout.addWidget(url_label, 0, 0, 1, 1)
        tab_content_layout.addWidget(url_editor, 0, 1, 1, 1)
        tab_content_layout.addWidget(open_button, 0, 2, 1, 1)
        tab_content_layout.addWidget(back_button, 0, 3, 1, 1)
        tab_content_layout.addWidget(forward_button, 0, 4, 1, 1)
        tab_content_layout.addWidget(reload_button, 0, 5, 1, 1)
        web_view = WebElementCaptureWebView(self)
        setup_web_view_actions(web_view)
        web_view.loadFinished.connect(self._on_load_finished)
        web_view.setObjectName('webView')
        web_view.titleChanged.connect(self._on_title_changed)
        web_view.iconChanged.connect(self._on_icon_changed)
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
        tab_content_layout.addWidget(web_view, 1, 0, 1, 6)
        tab_content_layout.setRowStretch(1, 1)
        help_label = QLabel(gettext(
            'Operation instructions: Ctrl+left-click to get a single element, and Shift+left-click two elements to get multiple similar elements.'))
        tab_content_layout.addWidget(help_label, 2, 0, 1, 3)
        self._tab_widget.addTab(tab_content_widget, gettext("New tab"))
        self._tab_widget.setCurrentWidget(tab_content_widget)
        web_view.urlChanged.connect(self._on_url_changed)
        web_view.pageAction(QWebEnginePage.WebAction.Back).enabledChanged.connect(
            lambda enabled: back_button.setDisabled(not enabled))
        web_view.pageAction(QWebEnginePage.WebAction.Forward).enabledChanged.connect(
            lambda enabled: forward_button.setDisabled(not enabled))
        web_view.pageAction(QWebEnginePage.WebAction.Reload).enabledChanged.connect(
            lambda enabled: reload_button.setDisabled(not enabled))
        if url:
            web_view.load(url)
            web_view.focusProxy().installEventFilter(self)
        web_view.show()
        open_button.clicked.connect(lambda: self._open_url(url_editor, web_view))
        return web_view

    def _open_url(self, url_editor: QLineEdit, web_view: QWebEngineView):
        input_url = url_editor.text()
        url = validate_and_fix_url(input_url)
        if not url:
            return
        if input_url != url:
            url_editor.setText(url)
        web_view.load(url)
        web_view.focusProxy().installEventFilter(self)

    def _back(self):
        tab_content_widget = Utils.find_ancestor(self.sender(), "tabContentWidget")
        web_view= tab_content_widget.findChild(QWebEngineView, "webView")
        web_view.back()

    def _forward(self):
        tab_content_widget = Utils.find_ancestor(self.sender(), "tabContentWidget")
        web_view = tab_content_widget.findChild(QWebEngineView, "webView")
        web_view.forward()

    def _reload(self):
        tab_content_widget = Utils.find_ancestor(self.sender(), "tabContentWidget")
        web_view = tab_content_widget.findChild(QWebEngineView, "webView")
        web_view.reload()

    @Slot(QUrl)
    def _on_url_changed(self, url: QUrl):
        web_view: QWebEngineView = self.sender()
        tab_content_widget=Utils.find_ancestor(web_view, "tabContentWidget")
        url_editor:QLineEdit = tab_content_widget.findChild(QLineEdit, "urlEditor")
        url_editor.setText(url.toString())

    @Slot(bool)
    def _on_load_finished(self, ok):
        web_view: QWebEngineView = self.sender()
        # 初始化时installEventFilter和脚本注入可能会失败，具体原因不明，所以在页面加载完成之后再尝试一遍
        web_view.focusProxy().installEventFilter(self)
        self._init_all_iframes()

    @Slot()
    def _init_all_iframes(self):
        for web_view in self.findChildren(QWebEngineView, "webView"):
            page: QWebEnginePage = web_view.page()
            stack = []
            page.mainFrame().runJavaScript(preload_js, QWebEngineScript.ScriptWorldId.UserWorld)
            page.mainFrame().runJavaScript(after_load_js, QWebEngineScript.ScriptWorldId.UserWorld)
            stack.extend(page.mainFrame().children())
            while stack:
                frame: QWebEngineFrame = stack.pop()
                frame.runJavaScript(preload_js, QWebEngineScript.ScriptWorldId.UserWorld)
                frame.runJavaScript(after_load_js, QWebEngineScript.ScriptWorldId.UserWorld)
                stack.extend(frame.children())

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

    @Slot(QIcon)
    def _on_icon_changed(self, icon):
        tab_content_widget = Utils.find_ancestor(self.sender(), 'tabContentWidget')
        index = self._tab_widget.indexOf(tab_content_widget)
        self._tab_widget.setTabIcon(index, icon)

    def eventFilter(self, watched: QObject, event):
        if event.type() == QEvent.Type.MouseButtonPress:
            if event.button() == Qt.MouseButton.LeftButton:
                if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                    web_view = Utils.find_ancestor(watched, 'webView')
                    if web_view:
                        self._select_element(web_view, event)
                        return True
                elif event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
                    web_view = Utils.find_ancestor(watched, 'webView')
                    if web_view:
                        self._multi_select_element(web_view, event)
                        return True
        elif event.type() == QEvent.Type.KeyPress and watched.objectName() == 'urlEditor':
            if event.key() == Qt.Key.Key_Enter or event.key() == Qt.Key.Key_Return:
                tab_content_widget = Utils.find_ancestor(watched, 'tabContentWidget')
                web_view = tab_content_widget.findChild(QWebEngineView, "webView")
                self._open_url(watched, web_view)
                return True
        return super().eventFilter(watched, event)

    def _select_element(self, web_view: QWebEngineView, event: QMouseEvent):
        def on_element_captured(element_info: dict):
            element_type = element_info['elementType']
            element_info['name'] = localized_element_types.get(element_type, element_type) + '_' + element_info['name']
            self.element_info = element_info
            self._edit_element_info(element_info)

        self._capture_element_by_position(web_view, event.position(), on_element_captured)

    def _edit_element_info(self, element_info: dict):
        self._element_editor.set_element_info(element_info)
        self._element_editor.setVisible(True)

    def _capture_element_by_position(self, web_view: QWebEngineView, position: QPointF,
                                     result_callback: Callable[[dict], None]):
        self._capture_element_in_frame_by_position(web_view, web_view.page().mainFrame(), position, [], result_callback)

    def _capture_element_in_frame_by_position(self, web_view: QWebEngineView, frame: QWebEngineFrame, position: QPointF,
                                              captured_elements: list, result_callback: Callable[[dict], None]):
        frame.runJavaScript(f'getElementInfoFromPoint({position.x()}, {position.y()}, "qt-highlight-selected")',
                            QWebEngineScript.ScriptWorldId.UserWorld,
                            lambda element_info: self._on_element_captured(web_view, frame, json.loads(element_info),
                                                                           captured_elements, result_callback))

    def _on_element_captured(self, web_view: QWebEngineView, frame: QWebEngineFrame, element_info: dict,
                             captured_elements: list, result_callback: Callable[[dict], None]):
        captured_elements.append(element_info)
        if 'iframeId' in element_info:
            def on_frame_id(frame: QWebEngineFrame, frame_id):
                if frame_id != element_info['iframeId']:
                    return
                self._capture_element_in_sub_frame(web_view, frame, element_info, captured_elements, result_callback)

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
                'snapshot': self._grab_screenshot(web_view, merged_rect['x'], merged_rect['y'], merged_rect['width'],
                                                  merged_rect['height'])
            }
            result_callback(final_element_info)

    def _get_frame_id(self, frame: QWebEngineFrame, result_callback: Callable[[QWebEngineFrame, str], None]):
        frame.runJavaScript('window.__iframe_id__', QWebEngineScript.ScriptWorldId.UserWorld,
                            lambda frame_id: result_callback(frame, frame_id))

    def _capture_element_in_sub_frame(self, web_view: QWebEngineView, sub_frame: QWebEngineFrame, element_info: dict,
                                      captured_elements: list, result_callback: Callable[[dict], None]):
        x_in_sub_frame = element_info['point'][0] - element_info['rect']['x']
        y_in_sub_frame = element_info['point'][1] - element_info['rect']['y']
        self._capture_element_in_frame_by_position(web_view, sub_frame, QPointF(x_in_sub_frame, y_in_sub_frame),
                                                   captured_elements, result_callback)

    def _grab_screenshot(self, web_view: QWebEngineView, x, y, width, height):
        rect = QRect(x, y, width, height).marginsAdded(QMargins(5, 5, 5, 5)).intersected(web_view.rect())
        image = web_view.grab(rect)
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
            image.save(temp_file.name)
            return temp_file.name

    def _multi_select_element(self, web_view: QWebEngineView, event: QMouseEvent):
        tab_content_widget = Utils.find_ancestor(web_view, 'tabContentWidget')
        custom_data: ElementSelection = tab_content_widget.property('customData')
        if custom_data.finished:
            self._clear_selection(web_view)
            custom_data.selected_list = []
            custom_data.finished = False

        def on_element_captured(element_info: dict):
            custom_data.selected_list.append(element_info)
            if len(custom_data.selected_list) >= 2:
                custom_data.finished = True
                merged_element = merge_elements(*custom_data.selected_list)
                if not merged_element:
                    QMessageBox.warning(self, gettext("Error"),
                                        gettext(
                                            "The second element does not match the first element, please select again!"))
                    self._clear_selection(web_view)
                else:
                    self._highlight_element(merged_element['frame'], merged_element['elementXPath'])
                    self.element_info = merged_element
                    self._edit_element_info(merged_element)

        self._capture_element_by_position(web_view, event.position(), on_element_captured)

    def _clear_selection(self, web_view: QWebEngineView):
        for frame in self.get_all_frames(web_view):
            frame.runJavaScript(f'''(function(){{
            const highlightedElements = document.querySelectorAll('.qt-highlight-selected');
            highlightedElements.forEach(element => {{
                element.classList.remove('qt-highlight-selected');
            }});
            }})()
            ''', QWebEngineScript.ScriptWorldId.UserWorld)

    def get_all_frames(self, web_view: QWebEngineView):
        stack = [web_view.page().mainFrame()]
        while stack:
            frame = stack.pop()
            yield frame
            stack.extend(frame.children())

    def _highlight_element(self, frame: QWebEngineFrame, xpath: str):
        frame.runJavaScript(f'highlightElement({json.dumps(xpath, ensure_ascii=False)}, "qt-highlight-selected")',
                            QWebEngineScript.ScriptWorldId.UserWorld)

    @Slot()
    def _check_element_info(self):
        if not self.element_info:
            return
        element_info = self.element_info
        tab_content_widget = self._tab_widget.currentWidget()
        current_web_view: QWebEngineView = tab_content_widget.findChild(QWebEngineView, 'webView')
        self._clear_selection(current_web_view)
        frame = current_web_view.page().mainFrame()
        if not element_info['inIframe']:
            self._highlight_element(frame, element_info['elementXPath'])
            return
        iframe_xpath_steps = parse_xpath(element_info['iframeXPath'])

        def on_sub_iframe_found(sub_iframe_info: dict):
            if not sub_iframe_info['iframeId']:
                return

            def on_frame_found(sub_frame: QWebEngineFrame):
                if not sub_iframe_info['xpath_steps']:
                    self._highlight_element(sub_frame, element_info['elementXPath'])
                    return
                self._find_sub_iframe_by_xpath_steps(sub_frame, sub_iframe_info['xpath_steps'], True,
                                                     on_sub_iframe_found)

            self._get_frame_by_id(current_web_view, sub_iframe_info['iframeId'], on_frame_found)

        self._find_sub_iframe_by_xpath_steps(frame, iframe_xpath_steps, True, on_sub_iframe_found)

    def _find_sub_iframe_by_xpath_steps(self, frame: QWebEngineFrame, xpath_steps: list, scroll_into_view,
                                        callback: Callable[[dict], None]):
        frame.runJavaScript(
            f'findIframeByXpathSteps({json.dumps(xpath_steps, ensure_ascii=False)},{json.dumps(scroll_into_view)})',
            QWebEngineScript.ScriptWorldId.UserWorld,
            lambda result: callback(json.loads(result)))

    def _get_frame_by_id(self, web_view: QWebEngineView, frame_id: str, callback: Callable[[QWebEngineFrame], None]):
        def on_frame_id_received(frame, result):
            if result == frame_id:
                callback(frame)

        for frame in self.get_all_frames(web_view):
            self._get_frame_id(frame, on_frame_id_received)


if __name__ == '__main__':
    app = QApplication()
    tool = WebElementCaptureTool(
        url='https://scm.chinaoct.com/octdzzc/spw/portal/detail.html?selectTab=jiaoyixinxi&primaryId=C0523739DCD04C009811C9603EFA806A&noticePath=变更公告&pageCode=noticeDetailFrame&pageName=变更公告')
    tool.show()
    app.exec()
