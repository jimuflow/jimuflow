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

import ctypes
import time
from contextlib import contextmanager

import comtypes
import pywinauto
import pywinauto.base_wrapper
from lxml import etree
from pywinauto import WindowSpecification, ElementAmbiguousError, ElementNotFoundError, win32functions, win32defines
from pywinauto.backend import registry, BackEnd
from pywinauto.controls.uiawrapper import UIAWrapper
from pywinauto.keyboard import ascii_vk, VirtualKeyAction, KeyAction, CODES
from pywinauto.timings import wait_until_passes, Timings
from pywinauto.uia_defines import IUIA
from pywinauto.uia_element_info import UIAElementInfo
from pywinauto.win32defines import SW_SHOW, SW_HIDE
from pywinauto.win32functions import ShowWindow
from pywinauto.win32structures import RECT

from jimuflow.common.uri_utils import parse_variable_uri, parse_window_element_uri
from jimuflow.locales.i18n import gettext

backend: BackEnd = registry.backends['uia']


def element_to_xml(element_info: UIAElementInfo, element_map, depth=0, max_depth=-1, is_dialog=False):
    elem = etree.Element(element_info.control_type)
    automation_id = element_info.automation_id
    if automation_id:
        elem.set('automation_id', automation_id)
    class_name = element_info.class_name
    if class_name:
        elem.set('class_name', class_name)
    control_id = element_info.control_id
    if control_id:
        elem.set('control_id', str(control_id))
    framework_id = element_info.framework_id
    if framework_id:
        elem.set('framework_id', framework_id)
    name = element_info.name
    if name:
        elem.set('name', name)
    if max_depth < 0 or depth < max_depth:
        root = UIAElementInfo()
        for child in element_info.children():
            if (element_info == root or UIAWrapper(child).is_dialog()) == is_dialog:
                elem.append(element_to_xml(child, element_map, depth + 1, max_depth, is_dialog))
    element_map[elem] = element_info
    return elem


def find_windows_by_xpath(xpath):
    element_map = {}
    root = element_to_xml(UIAElementInfo(), element_map, is_dialog=True)
    # print(etree.tostring(root, encoding='utf-8', pretty_print=True).decode())
    result = root.xpath(xpath)
    return [backend.generic_wrapper_class(element_map[elem]) for elem in result]


def find_window_by_xpath(xpath):
    windows = find_windows_by_xpath(xpath)

    if not windows:
        raise ElementNotFoundError(gettext('No windows found'))

    if len(windows) > 1:
        raise ElementAmbiguousError(gettext('Multiple windows found'))

    return windows[0]


def find_controls_by_xpath(window, xpath):
    if isinstance(window, WindowSpecification):
        window_element = window.wrapper_object().element_info
    elif isinstance(window, backend.generic_wrapper_class):
        window_element = window.element_info
    elif isinstance(window, int):
        # check if parent is a handle of element (in case of searching native controls)
        window_element = backend.element_info_class(window)
    elif isinstance(window, backend.element_info_class):
        window_element = window
    else:
        raise Exception('Unsupported window type: {}'.format(type(window)))
    element_map = {}
    root = element_to_xml(window_element, element_map)
    # print(etree.tostring(root, encoding='utf-8', pretty_print=True).decode())
    result = root.xpath(xpath)
    return [backend.generic_wrapper_class(element_map[elem]) for elem in result]


def find_control_by_xpath(window, xpath):
    controls = find_controls_by_xpath(window, xpath)

    if not controls:
        raise ElementNotFoundError(gettext('No controls found'))

    if len(controls) > 1:
        raise ElementAmbiguousError(gettext('Multiple controls found'))

    return controls[0]


def find_elements_by_xpath(window_xpath, element_xpath, raise_exception_if_not_found=False):
    windows = find_windows_by_xpath("/*" + window_xpath)
    result = []
    for window in windows:
        result.extend(find_controls_by_xpath(window, "/*" + element_xpath))
    if not result and raise_exception_if_not_found:
        raise ElementNotFoundError(gettext('No controls found'))
    return result


def find_element_by_xpath(window_xpath, element_xpath):
    controls = find_elements_by_xpath(window_xpath, element_xpath)

    if not controls:
        raise ElementNotFoundError(gettext('No controls found'))

    if len(controls) > 1:
        raise ElementAmbiguousError(gettext('Multiple controls found'))

    return controls[0]


def get_element_by_uri(component: "Component", element_uri: str, timeout: float,
                       wait_for_element=True) -> UIAWrapper:
    try:
        element_var = parse_variable_uri(element_uri)
        if element_var:
            element = component.process.get_variable(element_var)
        else:
            element_id = parse_window_element_uri(element_uri)
            element_info = component.process.component_def.package.get_window_element_by_id(element_id)
            element = wait_until_passes(timeout, 0.1, find_element_by_xpath,
                                        (ElementNotFoundError,),
                                        element_info['windowXPath'], element_info['elementXPath'])
        return element
    except pywinauto.timings.TimeoutError as e:
        if wait_for_element:
            raise e.original_exception
        else:
            return None


def get_elements_by_uri(component: "Component", elements_uri: str, timeout: float,
                        wait_for_element=True) -> list[pywinauto.base_wrapper.BaseWrapper]:
    try:
        elements_var = parse_variable_uri(elements_uri)
        if elements_var:
            elements = component.process.get_variable(elements_var)
        else:
            element_id = parse_window_element_uri(elements_uri)
            element_info = component.process.component_def.package.get_window_element_by_id(element_id)
            elements = wait_until_passes(timeout, 0.1, find_elements_by_xpath,
                                         (ElementNotFoundError,),
                                         element_info['windowXPath'], element_info['elementXPath'], True)
        return elements
    except pywinauto.timings.TimeoutError as e:
        if wait_for_element:
            raise e.original_exception
        else:
            return []


@contextmanager
def timeout_context_manager(timeout=5.0, retry_interval=0.09):
    old_timeout = Timings.window_find_timeout
    old_retry_interval = Timings.window_find_retry
    try:
        Timings.window_find_timeout = timeout
        Timings.window_find_retry = retry_interval
        yield
    except Exception as e:
        raise
    finally:
        Timings.window_find_timeout = old_timeout
        Timings.window_find_retry = old_retry_interval


def get_window_for_component(component: "Component"):
    get_window_method = component.read_input('getWindowMethod')
    if get_window_method == 'window_object':
        window_object = component.read_input('windowObject')
    elif get_window_method == 'title':
        title = component.read_input('title')
        kwargs = {}
        use_regex_matching = component.read_input('useRegexMatching')
        if use_regex_matching:
            kwargs['title_re'] = title
        else:
            kwargs['title'] = title
        use_class_name = component.read_input('useClassName')
        if use_class_name:
            kwargs['class_name'] = component.read_input('className')
        with timeout_context_manager(0):
            window_object = pywinauto.Desktop(backend="uia").window(**kwargs).wrapper_object()
    else:
        element_uri = component.read_input("elementUri")
        control_object = get_element_by_uri(component, element_uri, 0)
        window_object = control_object.top_level_parent()
    return window_object


def move_window(window: UIAWrapper, x=None, y=None, width=None, height=None):
    """Move the window to the new coordinates

    * **x** Specifies the new left position of the window.
      Defaults to the current left position of the window.
    * **y** Specifies the new top position of the window.
      Defaults to the current top position of the window.
    * **width** Specifies the new width of the window. Defaults to the
      current width of the window.
    * **height** Specifies the new height of the window. Default to the
      current height of the window.
    """
    cur_rect = window.rectangle()

    # if no X is specified - so use current coordinate
    if x is None:
        x = cur_rect.left
    else:
        try:
            y = x.top
            width = x.width()
            height = x.height()
            x = x.left
        except AttributeError:
            pass

    # if no Y is specified - so use current coordinate
    if y is None:
        y = cur_rect.top

    # if no width is specified - so use current width
    if width is None:
        width = cur_rect.width()

    # if no height is specified - so use current height
    if height is None:
        height = cur_rect.height()

    # ask for the window to be moved
    ret = win32functions.MoveWindow(window.handle, x, y, width, height, True)

    # check that it worked correctly
    if not ret:
        raise ctypes.WinError()

    win32functions.WaitGuiThreadIdle(window.handle)
    time.sleep(Timings.after_movewindow_wait)


def show_window(window: UIAWrapper):
    ShowWindow(window.handle, SW_SHOW)
    win32functions.WaitGuiThreadIdle(window.handle)
    time.sleep(Timings.after_movewindow_wait)


def hide_window(window: UIAWrapper):
    ShowWindow(window.handle, SW_HIDE)
    win32functions.WaitGuiThreadIdle(window.handle)
    time.sleep(Timings.after_movewindow_wait)


def send_text(text, pause=0.05, vk_packet=True):
    keys = []
    for c in text:
        if c == "\n":
            keys.append(VirtualKeyAction(CODES["ENTER"]))
            continue
        if not vk_packet and c in ascii_vk:
            keys.append(VirtualKeyAction(ascii_vk[c]))
        else:
            keys.append(KeyAction(c))
    for k in keys:
        k.run()
        time.sleep(pause)


def type_text(control: UIAWrapper, text, pause=None, vk_packet=True, set_foreground=True):
    control.verify_actionable()

    if pause is None:
        pause = Timings.after_sendkeys_key_wait

    if set_foreground:
        control.set_focus()

    # attach the Python process with the process that self is in
    if control.element_info.handle:
        window_thread_id = win32functions.GetWindowThreadProcessId(control.handle, None)
        win32functions.AttachThreadInput(win32functions.GetCurrentThreadId(), window_thread_id, win32defines.TRUE)
        # TODO: check return value of AttachThreadInput properly
    else:
        # TODO: UIA stuff maybe
        pass

    # Type the text to the active window
    send_text(text, pause, vk_packet)

    # detach the python process from the window's process
    if control.element_info.handle:
        win32functions.AttachThreadInput(win32functions.GetCurrentThreadId(), window_thread_id, win32defines.FALSE)
        # TODO: check return value of AttachThreadInput properly
    else:
        # TODO: UIA stuff
        pass

    control.wait_for_idle()


def get_control_by_position(x, y):
    desktop = pywinauto.Desktop(backend='uia')
    control: pywinauto.base_wrapper.BaseWrapper = desktop.from_point(x, y)
    if control.is_dialog():
        children = control.children(cache_enable=True)
        topmost_control = None
        while children:
            topmost_child = None
            for child in children:
                if child.is_visible():
                    rect: RECT = child.rectangle()
                    if x >= rect.left and x <= rect.right and y >= rect.top and y <= rect.bottom:
                        topmost_child = child
            if topmost_child:
                topmost_control = topmost_child
                children = topmost_child.children(cache_enable=True)
            else:
                break
        if topmost_control:
            control = topmost_control
    return control


STATE_SYSTEM_INVISIBLE = 0x8000


def is_control_visible(control: UIAWrapper):
    state = control.legacy_properties().get('State', 0)
    return control.is_visible() and state & STATE_SYSTEM_INVISIBLE == 0


text_pattern_range_endpoint_start = IUIA().ui_automation_client.TextPatternRangeEndpoint_Start
text_pattern_range_endpoint_end = IUIA().ui_automation_client.TextPatternRangeEndpoint_End


def move_text_cursor_to_end(control: UIAWrapper):
    try:
        document_range = control.iface_text.DocumentRange
        # 移动光标到整个文本的末尾
        document_range.MoveEndpointByRange(text_pattern_range_endpoint_start, document_range,
                                           text_pattern_range_endpoint_end)
        # 选中范围，光标移动到末尾
        document_range.Select()
    except comtypes.COMError:
        control.type_keys("^{END}", set_foreground=False)
