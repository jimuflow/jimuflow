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

from jimuflow.gui.web_element_relative_xpath_tool import get_relative_xpath


@pytest.mark.parametrize("source_xpath, target_xpath, expected", [
    ('/body/div[1]/div[1]', '/body/div[1]/div[1]/div/span', 'div/span'),
    ('/body/div[1]/div[2]', '/body/div[1]/div[1]/div/span', '../div[1]/div/span'),
    ('', '/body/div[1]/div[1]/div/span', ''),
    ('/body/div[1]/div[1]', '/body/div[1]/div[1]', '.'),
])
def test_get_relative_xpath(source_xpath, target_xpath, expected):
    assert get_relative_xpath(source_xpath, target_xpath) == expected
