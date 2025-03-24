# 识别字符验证码

## 功能

识别图片、网页或窗口中的字符验证码。

## 指令配置

### 输入参数

- **图像来源**：选择验证码图片的来源，可选值：文件、网页元素、窗口元素，常规配置，必填项，使用下拉框输入组件，默认值为文件。
- **图片文件**：如果图像来源为文件，则需要指定图片文件，常规配置，必填项，使用自定义输入组件`jimuflow.gui.components.file_path_editor.OpenFilePathEdit`。
- **网页对象**：如果图像来源为网页元素，则需要指定网页对象，常规配置，必填项，使用表达式输入组件。
- **网页元素**：如果图像来源为网页元素，则需要指定网页元素，常规配置，必填项，使用自定义输入组件`jimuflow.gui.components.web_element_selector.WebElementEdit`。
- **窗口元素**：如果图像来源为窗口元素，则需要指定窗口元素，常规配置，必填项，使用自定义输入组件`jimuflow.gui.components.window_element_selector.WindowElementEdit`。
- **等待时间**：等待网页元素或窗口元素出现的时间，单位为秒，高级配置，选填项，默认为30秒，使用表达式输入组件。

### 输出参数

- **识别结果**：识别出的字符验证码。

### 错误处理

支持。

## 实现

验证码的识别使用ddddocr。

获取网页元素的图像请参考ScreenshotWebElementComponent的实现。

获取窗口元素的图像请参考ScreenshotWindowElementComponent的实现。