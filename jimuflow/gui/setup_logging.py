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

import locale
import logging
import os
import platform
import sys
import time

from jimuflow.common.constants import APP_NAME, APP_VERSION


def get_log_file_path(log_file_name="app.log"):
    platform_name = platform.system()
    if platform_name == 'Windows':
        local_appdata_dir = os.getenv('LOCALAPPDATA')  # 获取 LocalAppData 路径
        log_dir = os.path.join(local_appdata_dir, APP_NAME)
        os.makedirs(log_dir, exist_ok=True)  # 确保目录存在
        return os.path.join(log_dir, log_file_name)
    elif platform_name == 'Linux':
        home_dir = os.path.expanduser("~")
        log_dir = os.path.join(home_dir, ".local", "share", APP_NAME, "logs")
        os.makedirs(log_dir, exist_ok=True)  # 确保目录存在
        return os.path.join(log_dir, log_file_name)
    elif platform_name == 'Darwin':
        home_dir = os.path.expanduser("~")
        log_dir = os.path.join(home_dir, "Library", "Logs", APP_NAME)
        os.makedirs(log_dir, exist_ok=True)  # 确保目录存在
        return os.path.join(log_dir, log_file_name)

def get_timezone_offset():
    offset_seconds= -time.timezone
    hours, remainder = divmod(offset_seconds, 3600)
    minutes = remainder // 60
    sign = "+" if offset_seconds >= 0 else "-"
    return f"{sign}{int(abs(hours)):02}:{int(abs(minutes)):02}"

LOGGING_FORMAT="%(asctime)s %(levelname)s %(name)s %(threadName)s %(filename)s:%(lineno)d : %(message)s"
def setup_logging_and_redirect():
    if not getattr(sys, 'frozen', False):
        # 开发环境
        logging.basicConfig(
            level=logging.DEBUG,
            format=LOGGING_FORMAT,
            handlers=[
                logging.StreamHandler(sys.stdout)
            ]
        )
    else:
        # 打包环境
        log_file_path = get_log_file_path()
        if os.path.exists(log_file_path):
            # 删除旧日志
            os.remove(log_file_path)
        logging.basicConfig(
            level=logging.INFO,
            format=LOGGING_FORMAT,
            handlers=[
                logging.FileHandler(log_file_path, encoding="utf-8"),
            ]
        )
        # 重定向标准输出和错误
        sys.stdout = open(log_file_path, "a", encoding="utf-8")
        sys.stderr = open(log_file_path, "a", encoding="utf-8")
    logging.root.info("Log for %s pid=%d version=%s", APP_NAME, os.getpid(), APP_VERSION)
    logging.root.info("Python version: %s", sys.version)
    logging.root.info("Platform: %s", platform.platform())
    logging.root.info("Host uname: %s", platform.uname())
    logging.root.info("Host codepage=%s encoding=%s", locale.getpreferredencoding(), sys.getdefaultencoding())
    logging.root.info("Host offset from UTC is %s", get_timezone_offset())

