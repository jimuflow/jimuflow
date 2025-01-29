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


def extract_component_def_json(fileobj, keywords, comment_tags, options):
    """Extract messages from JSON files.

    :param fileobj: the file-like object the messages should be extracted
                    from
    :param keywords: a list of keywords (i.e. function names) that should
                     be recognized as translation functions
    :param comment_tags: a list of translator tags to search for and
                         include in the results
    :param options: a dictionary of additional options (optional)
    :return: an iterator over ``(lineno, funcname, message, comments)``
             tuples
    :rtype: ``iterator``
    """
    json_data = json.loads(fileobj.read().decode('utf-8'))
    if "displayName" in json_data:
        yield 0, "gettext", json_data["displayName"], []
    if "primaryCategory" in json_data:
        yield 0, "gettext", json_data["primaryCategory"], []
    if "secondaryCategory" in json_data:
        yield 0, "gettext", json_data["secondaryCategory"], []
    if "variables" in json_data:
        for var_def in json_data["variables"]:
            if "uiConfig" in var_def:
                if "label" in var_def["uiConfig"]:
                    yield 0, "gettext", var_def["uiConfig"]["label"], []
                if "helpInfo" in var_def["uiConfig"]:
                    yield 0, "gettext", var_def["uiConfig"]["helpInfo"], []
                if "placeholder" in var_def["uiConfig"]:
                    yield 0, "gettext", var_def["uiConfig"]["placeholder"], []
                if "options" in var_def["uiConfig"]:
                    for option in var_def["uiConfig"]["options"]:
                        yield 0, "gettext", option["label"], []
