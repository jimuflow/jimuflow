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

from datetime import datetime as dt_datetime
from typing import Optional

from arrow import ArrowFactory, Arrow
from arrow.arrow import TZ_EXPR


class CustomArrow(Arrow):

    @classmethod
    def fromdatetime(cls, dt: dt_datetime, tzinfo: Optional[TZ_EXPR] = None) -> "Arrow":
        # 将默认时区从UTC改为本地时区
        if tzinfo is None:
            if dt.tzinfo is None:
                tzinfo = 'local'
            else:
                tzinfo = dt.tzinfo
        return super().fromdatetime(dt, tzinfo)


custom_arrow = ArrowFactory(CustomArrow)
