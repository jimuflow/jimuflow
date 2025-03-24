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

from unittest.mock import patch, MagicMock, AsyncMock

import pytest
import platform

from jimuflow.components.ocr import RecognizeCharCaptchaComponent
from jimuflow.runtime.execution_engine import ControlFlow
from tests.utils import create_component_context, add_test_web_element, add_test_window_element
import tempfile
from PIL import Image
import os


@pytest.mark.asyncio
async def test_recognize_from_file():
    """测试从文件识别验证码"""
    # 创建一个临时图片文件
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
        temp_path = temp_file.name
    
    try:
        # 创建一个简单的图片
        img = Image.new('RGB', (100, 30), color=(255, 255, 255))
        img.save(temp_path)
        
        # 模拟 ddddocr 识别结果
        with patch('ddddocr.DdddOcr') as mock_ocr:
            mock_ocr_instance = MagicMock()
            mock_ocr_instance.classification.return_value = "ABC123"
            mock_ocr.return_value = mock_ocr_instance
            
            async with create_component_context(RecognizeCharCaptchaComponent) as component:
                # 设置输入参数
                await component.process.update_variable('image_file', temp_path)
                
                component.node.inputs = {
                    "imageSource": 'file',
                    "imageFile": 'image_file'
                }
                component.node.outputs = {
                    "recognitionResult": 'result'
                }
                
                # 执行组件
                assert (await component.execute()) == ControlFlow.NEXT
                
                # 验证结果
                assert component.process.get_variable('result') == "ABC123"
                
                # 验证 OCR 调用
                mock_ocr_instance.classification.assert_called_once()
    finally:
        # 清理临时文件
        if os.path.exists(temp_path):
            os.remove(temp_path)


@pytest.mark.asyncio
async def test_recognize_from_web_element():
    """测试从网页元素识别验证码"""
    with patch('jimuflow.components.web_automation.playwright_utils.get_element_by_uri') as mock_get_element, \
         patch('ddddocr.DdddOcr') as mock_ocr, \
         patch('builtins.open', new_callable=MagicMock) as mock_open:
        
        # 模拟网页元素
        mock_element = MagicMock()
        mock_element.screenshot = AsyncMock()
        mock_get_element.return_value = mock_element
        
        # 模拟 ddddocr 识别结果
        mock_ocr_instance = MagicMock()
        mock_ocr_instance.classification.return_value = "XYZ789"
        mock_ocr.return_value = mock_ocr_instance
        
        # 模拟文件操作
        mock_file = MagicMock()
        mock_file.__enter__.return_value = mock_file
        mock_file.read.return_value = b'fake_image_data'
        mock_open.return_value = mock_file
        
        async with create_component_context(RecognizeCharCaptchaComponent) as component:
            # 添加测试网页元素
            element_uri = add_test_web_element(component, "//div[@id='captcha']")
            
            # 模拟网页对象
            mock_page = MagicMock()
            
            # 设置输入参数
            await component.process.update_variable('web_page', mock_page)
            await component.process.update_variable('wait_time', 10)
            
            component.node.inputs = {
                "imageSource": 'web_element',
                "webPage": 'web_page',
                "webElementUri": element_uri,
                "waitTime": 'wait_time'
            }
            component.node.outputs = {
                "recognitionResult": 'result'
            }
            
            # 执行组件
            assert (await component.execute()) == ControlFlow.NEXT
            
            # 验证结果
            assert component.process.get_variable('result') == "XYZ789"
            
            # 验证截图调用
            mock_element.screenshot.assert_called_once()
            
            # 验证 OCR 调用
            mock_ocr_instance.classification.assert_called_once_with(b'fake_image_data')


@pytest.mark.asyncio
async def test_recognize_from_window_element():
    """测试从窗口元素识别验证码"""
    # 如果不是Windows系统，则跳过此测试
    if platform.system() != 'Windows':
        pytest.skip("此测试仅在Windows系统上运行，因为它依赖于pywinauto_utill模块")
        
    with patch('jimuflow.components.windows_automation.pywinauto_utill.get_element_by_uri') as mock_get_element, \
         patch('ddddocr.DdddOcr') as mock_ocr:
        
        # 模拟窗口元素
        mock_control = MagicMock()
        mock_control.set_focus = MagicMock()
        mock_control.capture_as_image = MagicMock()
        mock_img = MagicMock()
        mock_control.capture_as_image.return_value = mock_img
        mock_get_element.return_value = mock_control
        
        # 模拟 ddddocr 识别结果
        mock_ocr_instance = MagicMock()
        mock_ocr_instance.classification.return_value = "DEF456"
        mock_ocr.return_value = mock_ocr_instance
        
        async with create_component_context(RecognizeCharCaptchaComponent) as component:
            # 添加测试窗口元素
            element_uri = add_test_window_element(component, "Button", "MainWindow")
            
            # 设置输入参数
            await component.process.update_variable('element_uri', element_uri)
            await component.process.update_variable('wait_time', 5)
            
            component.node.inputs = {
                "imageSource": 'window_element',
                "windowElementUri": 'element_uri',
                "waitTime": 'wait_time'
            }
            component.node.outputs = {
                "recognitionResult": 'result'
            }
            
            # 执行组件
            assert (await component.execute()) == ControlFlow.NEXT
            
            # 验证结果
            assert component.process.get_variable('result') == "DEF456"
            
            # 验证截图调用
            mock_control.set_focus.assert_called_once()
            mock_control.capture_as_image.assert_called_once()
            mock_img.save.assert_called_once()
            
            # 验证 OCR 调用
            mock_ocr_instance.classification.assert_called_once()


@pytest.mark.asyncio
async def test_empty_result():
    """测试空结果情况"""
    async with create_component_context(RecognizeCharCaptchaComponent) as component:
        # 设置输入参数为不存在的文件
        await component.process.update_variable('image_file', '/not/exist/file.png')
        
        component.node.inputs = {
            "imageSource": 'file',
            "imageFile": 'image_file'
        }
        component.node.outputs = {
            "recognitionResult": 'result'
        }
        
        # 执行组件应该抛出异常
        with pytest.raises(Exception):
            await component.execute()