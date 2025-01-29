import os

# 双许可文本
DUAL_LICENSE = """\
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
"""

def add_or_update_license(file_path):
    """向文件头部添加或更新双许可文本"""
    with open(file_path, 'r+', encoding='utf-8') as file:
        content = file.read()

        # 如果文件已包含该许可，跳过
        if DUAL_LICENSE in content:
            print(f"Skipping: {file_path} (License already exists)")
            return

        # 查找是否有现有许可头部
        if "# This software is dual-licensed" in content:
            content = content.split("\n", 15)[15][1:]  # 删除旧的头部

        file.seek(0, 0)
        file.write(DUAL_LICENSE + '\n' + content)
        print(f"Updated: {file_path}")

def process_directory(directory):
    """递归处理目录中的所有 Python 文件"""
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                add_or_update_license(file_path)

if __name__ == "__main__":
    target_directory = input("Enter the target directory: ").strip()
    if os.path.isdir(target_directory):
        process_directory(target_directory)
    else:
        print(f"Error: {target_directory} is not a valid directory.")
