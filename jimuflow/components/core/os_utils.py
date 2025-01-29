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

import asyncio
import os
import platform
import plistlib
import shlex
import shutil
import stat
import time
from pathlib import Path

import psutil

from jimuflow.locales.i18n import gettext


def is_windows():
    return os.name == 'nt'


def is_hidden(filepath: Path):
    if is_windows():
        return filepath.stat().st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN != 0
    else:
        return filepath.name.startswith('.')


def get_file_encoding_title(file_encoding: str):
    if file_encoding == 'system_default':
        return gettext('System default')
    elif file_encoding == 'utf-8':
        return gettext('UTF-8')
    elif file_encoding == 'ascii':
        return gettext('ASCII')
    elif file_encoding == 'latin-1':
        return gettext('Latin-1')
    elif file_encoding == 'utf-8-sig':
        return gettext('UTF-8 with BOM')
    elif file_encoding == 'utf-16':
        return gettext('UTF-16')
    elif file_encoding == 'utf-32':
        return gettext('UTF-32')
    elif file_encoding == 'gbk':
        return gettext('GBK')
    elif file_encoding == 'gb2312':
        return gettext('GB2312')
    elif file_encoding == 'gb18030':
        return gettext('GB18030')
    return file_encoding


def rename_file_if_exists(file_path: str):
    if os.path.exists(file_path):
        # 文件存在，进行重命名
        base, extension = os.path.splitext(file_path)
        counter = 1
        while True:
            new_name = f"{base}_{counter}{extension}"
            if not os.path.exists(new_name):
                return new_name
            counter += 1
    return file_path


def delete_all_in_directory(directory):
    # 确保目录存在
    if not os.path.exists(directory):
        return

    # 遍历目录中的所有文件和子目录
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        # 如果是文件，删除文件
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        # 如果是目录，递归删除目录
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)


def is_macos():
    return platform.system() == 'Darwin'


def is_linux():
    return platform.system() == 'Linux'


def is_ubuntu():
    return is_linux() and 'ubuntu' in platform.version().lower()


async def launch_app(app_path, work_dir=None, args=None):
    if is_macos() and app_path.endswith('.app'):
        app_path = get_macos_app_bin_path(app_path)
    if args:
        args = shlex.split(args)
    else:
        args = []
    return await asyncio.create_subprocess_exec(app_path, *args, cwd=work_dir)


def get_macos_app_bin_path(app_path):
    plist_path = os.path.join(app_path, 'Contents/Info.plist')
    with open(plist_path, 'rb') as f:
        plist_data = plistlib.load(f)
        return os.path.join(app_path, 'Contents/MacOS', plist_data['CFBundleExecutable'])


def is_process_alive(pid):
    try:
        psutil.Process(pid)
        return True
    except psutil.NoSuchProcess:
        return False


async def sleep_at_least(seconds):
    start_time = time.time()
    last_time = start_time
    wait_time = seconds
    while wait_time > 0:
        await asyncio.sleep(wait_time)
        now = time.time()
        real_wait_time = now - start_time
        if real_wait_time >= seconds or now == last_time:
            break
        wait_time = seconds - real_wait_time
        last_time = now
