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

import subprocess
import sys
import time

import pytest


@pytest.fixture(scope="function")
def start_python_process():
    started_processes = []

    def _start_python_process(script_name, *args, wait_time=2):
        # 获取当前运行测试代码的 Python 路径
        python_path = sys.executable

        # 构建命令
        command = [python_path, script_name] + list(args)

        # 启动子进程
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        started_processes.append(process)

        if wait_time > 0:
            # 等待脚本启动，确保它已经在运行
            time.sleep(wait_time)

        return process

    yield _start_python_process

    for process in started_processes:
        process.terminate()
        process.wait()
