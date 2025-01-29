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

import datetime
import math

from jimuflow.locales.i18n import gettext
from .core import DataTypeRegistry, DataTypeDef, DataTypeProperty
from .file_path_info import file_path_info_type
from .table import table_data_type

builtin_data_type_registry = DataTypeRegistry()

# any type
any_data_type = DataTypeDef("any", gettext('Any Type'))
builtin_data_type_registry.register(any_data_type)

# text type
text_data_type = DataTypeDef("text", gettext('Text'), [
    DataTypeProperty("length", "number", gettext("Text length"), lambda x: len(x)),
    DataTypeProperty("lower", "text", gettext("Lowercase text"), lambda x: x.lower()),
    DataTypeProperty("upper", "text", gettext("Uppercase text"), lambda x: x.upper()),
], types=(str,))
builtin_data_type_registry.register(text_data_type)

# number type
number_data_type = DataTypeDef("number", gettext('Number'), [
    DataTypeProperty("round", "number", gettext("Round number"), lambda x: round(x)),
    DataTypeProperty("floor", "number", gettext("Floor number"), lambda x: math.floor(x)),
    DataTypeProperty("ceil", "number", gettext("Ceil number"), lambda x: math.ceil(x)),
    DataTypeProperty("abs", "number", gettext("Absolute value"), lambda x: math.ceil(x)),
], types=(int, float))
builtin_data_type_registry.register(number_data_type)

# bool type
bool_data_type = DataTypeDef("bool", gettext('Boolean'), types=(bool,))
builtin_data_type_registry.register(bool_data_type)

# list type
list_data_type = DataTypeDef("list", gettext('List'), [
    DataTypeProperty("size", "number", gettext("Number of items in the list"), lambda x: len(x)),
], is_list=True, types=(list, tuple))
builtin_data_type_registry.register(list_data_type)

# dict type
dict_data_type = DataTypeDef("dict", gettext('Dictionary'), [
    DataTypeProperty("size", "number", gettext("Number of items in the dict"), lambda x: len(x)),
    DataTypeProperty("keys", "list", gettext("Keys in the dict"), lambda x: list(x.keys())),
    DataTypeProperty("values", "list", gettext("Values in the dict"), lambda x: list(x.values())),
    DataTypeProperty("items", "list", gettext("Items in the dict"), lambda x: list(x.items())),
], types=(dict,))
builtin_data_type_registry.register(dict_data_type)

# table type
builtin_data_type_registry.register(table_data_type)

# date type
date_data_type = DataTypeDef("date", gettext('Date'), [
    DataTypeProperty("year", "number", gettext("The year of the date")),
    DataTypeProperty("month", "number", gettext("The month of the date")),
    DataTypeProperty("day", "number", gettext("The day of the date")),
], types=(datetime.date,))
builtin_data_type_registry.register(date_data_type)

# time type
time_data_type = DataTypeDef("time", gettext('Time'), [
    DataTypeProperty("hour", "number", gettext("The hour of the time")),
    DataTypeProperty("minute", "number", gettext("The minute of the time")),
    DataTypeProperty("second", "number", gettext("The second of the time")),
    DataTypeProperty("microsecond", "number", gettext("The microsecond of the time")),
], types=(datetime.time,))
builtin_data_type_registry.register(time_data_type)

# datetime type
datetime_data_type = DataTypeDef("datetime", gettext('DateTime'), [
    DataTypeProperty("date", "date", gettext("The date of the datetime")),
    DataTypeProperty("time", "time", gettext("The time of the datetime")),
    DataTypeProperty("year", "number", gettext("The year of the datetime")),
    DataTypeProperty("month", "number", gettext("The month of the datetime")),
    DataTypeProperty("day", "number", gettext("The day of the datetime")),
    DataTypeProperty("hour", "number", gettext("The hour of the datetime")),
    DataTypeProperty("minute", "number", gettext("The minute of the datetime")),
    DataTypeProperty("second", "number", gettext("The second of the datetime")),
    DataTypeProperty("microsecond", "number", gettext("The microsecond of the datetime")),
    DataTypeProperty("timestamp", "number", gettext("The timestamp of the datetime, in seconds"),
                     lambda x: x.timestamp()),
], types=(datetime.datetime,))
builtin_data_type_registry.register(datetime_data_type)

# FilePathInfo type
builtin_data_type_registry.register(file_path_info_type)
