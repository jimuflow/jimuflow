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
import tempfile

import ddddocr
from playwright.async_api import Page

from jimuflow.common.uri_utils import describe_element_uri
from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow


class RecognizeCharCaptchaComponent(PrimitiveComponent):
    """识别字符验证码组件"""

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        image_source = flow_node.input("imageSource")
        result = flow_node.output("recognitionResult")
        if image_source == 'file':
            return gettext('Recognize character captcha in image file ##{imageFile}##, saving result to ##{result}##').format(
                imageFile=flow_node.input('imageFile'), result=result)
        elif image_source == 'web_element':
            return gettext('Recognize character captcha in web page ##{webPage}## element ##{webElement}##, saving result to ##{result}##').format(
                webPage=flow_node.input('webPage'),
                webElement=describe_element_uri(flow_node.process_def.package, flow_node.input('webElementUri')),
                result=result)
        elif image_source == 'window_element':
            return gettext('Recognize character captcha in window element ##{windowElement}##, saving result to ##{result}##').format(
                windowElement=describe_element_uri(flow_node.process_def.package, flow_node.input('windowElementUri')),
                result=result)
        return gettext('Recognize character captcha, saving result to ##{result}##').format(result=result)

    async def execute(self) -> ControlFlow: 
        # 初始化 OCR 对象
        ocr = ddddocr.DdddOcr(show_ad=False)
        
        # 根据图像来源获取图像数据
        image_source = self.read_input("imageSource")
        img_bytes = None
        
        if image_source == 'file':
            # 从文件读取图像
            image_file = self.read_input("imageFile")
            if not os.path.exists(image_file):
                raise Exception(gettext("File does not exist: {image_file}").format(image_file=image_file))
            with open(image_file, 'rb') as f:
                img_bytes = f.read()
        
        elif image_source == 'web_element':
            # 从网页元素获取图像
            from jimuflow.components.web_automation.playwright_utils import get_element_by_uri
            
            page: Page = self.read_input("webPage")
            element_uri = self.read_input("webElementUri")
            wait_time = int(self.read_input("waitTime"))
            
            element = await get_element_by_uri(self, page, element_uri, wait_time)
            
            # 创建临时文件保存截图
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                temp_path = temp_file.name
            
            try:
                # 截取元素图像
                await element.screenshot(path=temp_path, timeout=wait_time * 1000)
                
                # 读取图像数据
                with open(temp_path, 'rb') as f:
                    img_bytes = f.read()
            finally:
                # 删除临时文件
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        
        elif image_source == 'window_element':
            # 从窗口元素获取图像
            from jimuflow.components.windows_automation.pywinauto_utill import get_element_by_uri
            
            element_uri = self.read_input("windowElementUri")
            wait_time = float(self.read_input("waitTime"))
            
            control_object = get_element_by_uri(self, element_uri, wait_time)
            
            # 创建临时文件保存截图
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                temp_path = temp_file.name
            
            try:
                # 设置焦点并截图
                control_object.set_focus()
                img = control_object.capture_as_image()
                img.save(temp_path)
                
                # 读取图像数据
                with open(temp_path, 'rb') as f:
                    img_bytes = f.read()
            finally:
                # 删除临时文件
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        
        # 识别验证码
        if img_bytes:
            result = ocr.classification(img_bytes)
            await self.write_output('recognitionResult', result)
        else:
            raise Exception(gettext("Failed to get the image data of the captcha"))
        
        return ControlFlow.NEXT
