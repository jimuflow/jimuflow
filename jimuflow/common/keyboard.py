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

from jimuflow.components.core.os_utils import is_macos

keyboard_keys = {
    "esc": "Esc",
    "f1": "F1",
    "f2": "F2",
    "f3": "F3",
    "f4": "F4",
    "f5": "F5",
    "f6": "F6",
    "f7": "F7",
    "f8": "F8",
    "f9": "F9",
    "f10": "F10",
    "f11": "F11",
    "f12": "F12",
    "`": "`",
    "1": "1",
    "2": "2",
    "3": "3",
    "4": "4",
    "5": "5",
    "6": "6",
    "7": "7",
    "8": "8",
    "9": "9",
    "0": "0",
    "-": "-",
    "=": "=",
    "backspace": "Backspace",
    "tab": "Tab",
    "q": "Q",
    "w": "W",
    "e": "E",
    "r": "R",
    "t": "T",
    "y": "Y",
    "u": "U",
    "i": "I",
    "o": "O",
    "p": "P",
    "[": "[",
    "]": "]",
    "\\": "\\",
    "capslock": "Caps Lock",
    "a": "A",
    "s": "S",
    "d": "D",
    "f": "F",
    "g": "G",
    "h": "H",
    "j": "J",
    "k": "K",
    "l": "L",
    ";": ";",
    "'": "'",
    "enter": "Enter",
    "shiftleft": "Left Shift",
    "z": "Z",
    "x": "X",
    "c": "C",
    "v": "V",
    "b": "B",
    "n": "N",
    "m": "M",
    ",": ",",
    ".": ".",
    "/": "/",
    "fn": "fn",
    "shiftright": "Right Shift",
    "ctrlleft": "Left Ctrl",
    "winleft": "Left Windows",
    "altleft": "Left Alt",
    "optionleft": "Left Option",
    "ctrlcmd": "Ctrl/Command",
    "command": "Command",
    "space": "Space",
    "altright": "Right Alt",
    "winright": "Right Windows",
    "ctrlright": "Right Ctrl",
    "optionright": "Right Option",
    "printscreen": "Print Screen",
    "scrolllock": "Scroll Lock",
    "pause": "Pause Break",
    "insert": "Insert",
    "home": "Home",
    "pageup": "Page Up",
    "delete": "Delete",
    "end": "End",
    "pagedown": "Page Down",
    "up": "Up",
    "left": "Left",
    "down": "Down",
    "right": "Right",
    "numlock": "Num Lock",
    "divide": "Divide",
    "multiply": "Multiply",
    "subtract": "Subtract",
    "add": "Add",
    "num7": "Num 7",
    "num8": "Num 8",
    "num9": "Num 9",
    "num4": "Num 4",
    "num5": "Num 5",
    "num6": "Num 6",
    "num1": "Num 1",
    "num2": "Num 2",
    "num3": "Num 3",
    "num0": "Num 0",
}
common_hotkeys = {
    "ctrlcmd_c": "Ctrl/Cmd+C",
    "ctrlcmd_v": "Ctrl/Cmd+V",
    "ctrlcmd_x": "Ctrl/Cmd+X",
    "ctrlcmd_z": "Ctrl/Cmd+Z",
    "ctrlcmd_s": "Ctrl/Cmd+S",
    "ctrlcmd_a": "Ctrl/Cmd+A",
    "enter": "Enter"
}


def desc_hotkey(hotkey):
    return "+".join(keyboard_keys.get(k, k) for k in hotkey)


def transform_key(key):
    if key == 'ctrlcmd':
        return 'command' if is_macos() else 'ctrl'
    else:
        return key
