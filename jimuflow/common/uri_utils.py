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

from jimuflow.definition import Package
from jimuflow.locales.i18n import gettext

VARIABLE_URI_PREFIX = "jimuflow:variable:"


def build_variable_uri(variable_name):
    return f"{VARIABLE_URI_PREFIX}{variable_name}"


def parse_variable_uri(uri):
    if not uri or not uri.startswith(VARIABLE_URI_PREFIX):
        return None
    return uri[len(VARIABLE_URI_PREFIX):]


def is_variable_uri(uri):
    return parse_variable_uri(uri) is not None


WEB_ELEMENT_URI_PREFIX = "jimuflow:webelement:"


def build_web_element_uri(element_info):
    return f"{WEB_ELEMENT_URI_PREFIX}{element_info['id']}"


def parse_web_element_uri(uri):
    if not uri or not uri.startswith(WEB_ELEMENT_URI_PREFIX):
        return None
    element_id = uri[len(WEB_ELEMENT_URI_PREFIX):]
    return element_id


def is_web_element_uri(uri):
    return parse_web_element_uri(uri) is not None


WINDOW_ELEMENT_URI_PREFIX = "jimuflow:windowelement:"


def build_window_element_uri(element_id):
    return f"{WINDOW_ELEMENT_URI_PREFIX}{element_id}"


def parse_window_element_uri(uri):
    if not uri or not uri.startswith(WINDOW_ELEMENT_URI_PREFIX):
        return None
    element_id = uri[len(WINDOW_ELEMENT_URI_PREFIX):]
    return element_id


def is_window_element_uri(uri):
    return parse_window_element_uri(uri) is not None


def describe_element_uri(package: Package, element_uri: str) -> str:
    element_var = parse_variable_uri(element_uri)
    if element_var:
        return element_var
    else:
        element_id = parse_web_element_uri(element_uri)
        if element_id:
            element_info = package.get_web_element_by_id(element_id)
            if element_info:
                return element_info['name']
        else:
            element_id = parse_window_element_uri(element_uri)
            if element_id:
                element_info = package.get_window_element_by_id(element_id)
                if element_info:
                    return element_info['name']
    return gettext('Unknown element')
