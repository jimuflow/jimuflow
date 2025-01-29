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

import pytest

from jimuflow.common.web_element_utils import parse_xpath, escape_xpath_string


@pytest.mark.parametrize("value,expected", [
    ('abc\nefg', '\'abc\nefg\''),
    ('a\'b', '"a\'b"'),
    ('a"b', '\'a"b\''),
    ('a\'bc"d', 'concat("a\'bc",\'"d\')')
])
def test_escape_xpath_string(value, expected):
    assert escape_xpath_string(value) == expected


@pytest.mark.parametrize("xpath,expected", [
    (' /html/div[1]//div[@id=\'abc\']/div[@name=\'efg\' and position()=2]',
     ['/html', '/div[1]', '//div[@id=\'abc\']', '/div[@name=\'efg\' and position()=2]']),
    ('div/span[text()="abc"]/span[text()=concat(\'"\',"\'")]',
     ['div', '/span[text()="abc"]', '/span[text()=concat(\'"\',"\'")]'])
])
def test_parse_xpath(xpath, expected):
    assert parse_xpath(xpath) == expected
