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
import re
import sys
import time
from datetime import datetime

import jimuflow

log_file_name = jimuflow.__project_name__.lower() + "_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".log"
log_file_name_pattern = re.compile(r"^" + re.escape(jimuflow.__project_name__.lower()) + r"_\d{8}_\d{6}\.log$")


def get_log_file_path():
    platform_name = platform.system()
    if platform_name == 'Windows':
        local_appdata_dir = os.getenv('LOCALAPPDATA')  # 获取 LocalAppData 路径
        log_dir = os.path.join(local_appdata_dir, jimuflow.__project_name__)
        os.makedirs(log_dir, exist_ok=True)  # 确保目录存在
        return os.path.join(log_dir, log_file_name)
    elif platform_name == 'Linux':
        home_dir = os.path.expanduser("~")
        log_dir = os.path.join(home_dir, ".local", "share", jimuflow.__project_name__, "logs")
        os.makedirs(log_dir, exist_ok=True)  # 确保目录存在
        return os.path.join(log_dir, log_file_name)
    elif platform_name == 'Darwin':
        home_dir = os.path.expanduser("~")
        log_dir = os.path.join(home_dir, "Library", "Logs", jimuflow.__project_name__)
        os.makedirs(log_dir, exist_ok=True)  # 确保目录存在
        return os.path.join(log_dir, log_file_name)


def get_timezone_offset():
    offset_seconds = -time.timezone
    hours, remainder = divmod(offset_seconds, 3600)
    minutes = remainder // 60
    sign = "+" if offset_seconds >= 0 else "-"
    return f"{sign}{int(abs(hours)):02}:{int(abs(minutes)):02}"


LOGGING_FORMAT = "%(asctime)s %(levelname)s %(name)s %(threadName)s %(filename)s:%(lineno)d : %(message)s"


def setup_logging_and_redirect():
    # 获取最新的日志文件
    log_file_path = get_log_file_path()
    if not getattr(sys, 'frozen', False):
        # 开发环境
        logging.basicConfig(
            level=logging.DEBUG,
            format=LOGGING_FORMAT,
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(log_file_path, encoding="utf-8"),
            ]
        )
    else:
        # 打包环境
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
    logging.root.info("Log for %s pid=%d version=%s", jimuflow.__project_name__, os.getpid(),
                      f'{jimuflow.__version__} {jimuflow.__git_tag__} {jimuflow.__git_commit_date__}')
    logging.root.info("Python version: %s", sys.version)
    logging.root.info("Platform: %s", platform.platform())
    uname_res = platform.uname()
    logging.root.info("Host: system=%s, release=%s, version=%s, machine=%s, processor=%s", uname_res.system,
                      uname_res.release, uname_res.version, uname_res.machine, uname_res.processor)
    logging.root.info("Host codepage=%s encoding=%s", locale.getpreferredencoding(), sys.getdefaultencoding())
    logging.root.info("Host offset from UTC is %s", get_timezone_offset())
    # 删除旧的日志文件，只保留最近10个日志文件
    log_dir = os.path.dirname(log_file_path)
    old_log_files = []
    for filename in os.listdir(log_dir):
        if log_file_name_pattern.match(filename):
            old_log_files.append(filename)
    old_log_files.sort(reverse=True)
    for filename in old_log_files[9:]:
        os.remove(os.path.join(log_dir, filename))
        logging.root.info("Delete old log file: %s", filename)
