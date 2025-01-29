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

from ctypes import windll, wintypes

GetCursorPos = windll.user32.GetCursorPos
GetCursorPos.argtypes = [wintypes.LPPOINT]
GetCursorPos.restype = wintypes.BOOL

GetSystemMetrics = windll.user32.GetSystemMetrics
GetSystemMetrics.argtypes = [wintypes.UINT]
GetSystemMetrics.restype = wintypes.INT

GetClassLong = windll.user32.GetClassLongA
GetClassLong.argtypes = [wintypes.HWND, wintypes.INT]
GetClassLong.restype = wintypes.DWORD

InvalidateRect = windll.user32.InvalidateRect
InvalidateRect.argtypes = [wintypes.HWND, wintypes.RECT, wintypes.BOOL]
InvalidateRect.restype = wintypes.BOOL

RedrawWindow = windll.user32.RedrawWindow
RedrawWindow.argtypes = [wintypes.HWND, wintypes.RECT, wintypes.HRGN, wintypes.UINT]
RedrawWindow.restype = wintypes.BOOL

CreateRoundRectRgn = windll.gdi32.CreateRoundRectRgn
CreateRoundRectRgn.argtypes = [wintypes.INT, wintypes.INT, wintypes.INT, wintypes.INT, wintypes.INT, wintypes.INT]
CreateRoundRectRgn.restype = wintypes.HRGN

GetDeviceCaps = windll.gdi32.GetDeviceCaps
GetDeviceCaps.argtypes = [wintypes.HDC, wintypes.INT]
GetDeviceCaps.restype = wintypes.INT

ReleaseDC = windll.user32.ReleaseDC
ReleaseDC.argtypes = [wintypes.HWND, wintypes.HDC]
ReleaseDC.restype = wintypes.INT