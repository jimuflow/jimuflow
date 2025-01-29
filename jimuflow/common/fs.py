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

import os
import shutil


def copy_folder_overwrite(src, dest):
    src = str(src)
    dest = str(dest)
    if os.path.isdir(dest):
        for root, dirs, files in os.walk(src):
            for dir in dirs:
                relpath = os.path.relpath(os.path.join(root, dir), src)
                os.mkdir(os.path.join(dest, relpath))
            for file in files:
                relpath = os.path.relpath(os.path.join(root, file), src)
                shutil.copy(os.path.join(root, file), os.path.join(dest, relpath))
    else:
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copytree(src, dest)


def move_folder_overwrite(src, dest):
    src = str(src)
    dest = str(dest)
    if os.path.isdir(dest):
        for root, dirs, files in os.walk(src):
            for dir in dirs:
                dest = os.path.join(dest, os.path.relpath(os.path.join(root, dir), src))
                if not os.path.exists(dest):
                    os.mkdir(dest)
            for file in files:
                dest = os.path.join(dest, os.path.relpath(os.path.join(root, file), src))
                if os.path.exists(dest):
                    os.remove(dest)
                shutil.move(os.path.join(root, file), dest)
        shutil.rmtree(src)
    else:
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.move(src, dest)
