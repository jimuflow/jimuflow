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

import sys
from pathlib import Path

if getattr(sys, 'frozen', False):
    # 如果是打包后的程序
    app_base_path = Path(sys._MEIPASS) / 'jimuflow'
else:
    # 如果是开发模式
    app_base_path = Path(__file__).resolve().parent.parent

app_resources_path = app_base_path / "resources"


def get_resource_file(file_name):
    return app_resources_path / file_name
