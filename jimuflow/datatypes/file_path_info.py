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

from pathlib import Path

from jimuflow.locales.i18n import gettext
from .core import DataTypeDef, DataTypeProperty


class FilePathInfo:
    def __init__(self, file_path: str):
        self._path = Path(file_path)

    @property
    def root(self) -> str:
        return str(self._path.anchor)

    @property
    def parent(self) -> str:
        return str(self._path.parent)

    @property
    def name(self) -> str:
        return self._path.name

    @property
    def nameWithoutExtension(self) -> str:
        return self._path.name.rsplit(".", 1)[0]

    @property
    def extension(self) -> str:
        return self._path.suffix

    @property
    def exists(self) -> bool:
        return self._path.exists()

    @property
    def isDirectory(self):
        return self._path.is_dir()

    @property
    def isFile(self):
        return self._path.is_file()

    @property
    def size(self):
        return self._path.stat().st_size

    @property
    def ctime(self):
        return self._path.stat().st_ctime

    @property
    def mtime(self):
        return self._path.stat().st_mtime


file_path_info_type = DataTypeDef("FilePathInfo", gettext("File Path Info"), [
    DataTypeProperty("root", "text", gettext("root directory")),
    DataTypeProperty("parent", "text", gettext("parent directory")),
    DataTypeProperty("name", "text", gettext("file name")),
    DataTypeProperty("nameWithoutExtension", "text", gettext("file name without extension")),
    DataTypeProperty("extension", "text", gettext("file extension")),
    DataTypeProperty("exists", "bool", gettext("file exists")),
    DataTypeProperty("isDirectory", "bool", gettext("is directory")),
    DataTypeProperty("isFile", "bool", gettext("is file")),
    DataTypeProperty("size", "number", gettext("file size")),
    DataTypeProperty("ctime", "number", gettext("creation time(timestamp)")),
    DataTypeProperty("mtime", "number", gettext("modification time(timestamp)")),
], types=(FilePathInfo,))
