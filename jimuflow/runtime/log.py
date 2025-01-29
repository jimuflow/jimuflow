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
import traceback
from enum import Enum

from jimuflow.locales.i18n import gettext


class LogLevel(Enum):
    DEBUG = 0
    INFO = 1
    WARN = 2
    ERROR = 3

    @property
    def display_name(self):
        if self == LogLevel.DEBUG:
            return gettext("Debug")
        if self == LogLevel.INFO:
            return gettext("Info")
        if self == LogLevel.WARN:
            return gettext("Warning")
        if self == LogLevel.ERROR:
            return gettext("Error")


class LogEntry:
    def __init__(self, timestamp: datetime.datetime, level: LogLevel, process_id: str, comp_id: str, line_no: int,
                 message: str, exception: Exception):
        self.timestamp = timestamp
        self.level = level
        self.process_id = process_id
        self.comp_id = comp_id
        self.line_no = line_no
        self.message = message
        self.exception = exception
        self.traceback = traceback.format_exc() if exception else None


class Logger:

    def __init__(self, level: LogLevel = LogLevel.INFO):
        self.level = level

    def log(self, message: str, level: LogLevel = LogLevel.INFO, process_id: str = None,
            comp_id: str = None, line_no: int = None, exception: Exception = None):
        self.do_log(
            LogEntry(datetime.datetime.now(), level, process_id, comp_id, line_no, message, exception))

    def do_log(self, log_entry: LogEntry):
        pass

    def is_level_enabled(self, level: LogLevel):
        return self.level.value <= level.value


class ConsoleLogger(Logger):
    def do_log(self, log_entry: LogEntry):
        t = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"{t} {log_entry.level.name} {log_entry.process_id} {log_entry.line_no} {log_entry.comp_id}: {log_entry.message}")
        if log_entry.traceback:
            print(log_entry.traceback)
