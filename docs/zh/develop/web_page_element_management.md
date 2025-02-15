# 网页元素管理

使用网页元素捕获工具捕获元素，捕获的网页元素会以json格式保存在元素库中， 后续可以通过元素ID引用该元素。

元素库文件保存在应用的elements\web_elements\<元素分组>目录下，文件名是元素ID，文件内容是元素信息。

元素库目录结构：

```text
应用目录                                  应用根目录
  elements                               元素库文件夹
    web_elements                         网页元素文件夹
      group_元素分组1                     元素分组文件夹，以元素所在的网页标题命名
        group_icon.png                   元素分组图标文件，以网页图标作为分组图标
        element_id1.jsonl                元素JSON文件，元素ID使用UUID生成
        element_id1.png                  元素截图文件
        element_id2.jsonl
        element_id2.png
```

元素文件JSON格式如下：
```json lines
{"name": "元素名称","iframeXPath": "iframe的xpath表达式","elementXPath": "元素的xpath表达式","createdAt": "创建时间","updatedAt": "修改时间"}
{
  "webPageUrl": "元素所在页面URL，用于重新捕获元素",
  "inIframe": "元素是否在iframe中，默认为false",
  "useCustomIframeXPath": "是否使用自定义的iframeXPath，默认为false",
  "iframePath": [
    {
      "element": "元素名,如div",
      "enabled": "是否启用",
      "predicates": [
        ["attr1","=","value1","是否启用"],
        ["attr2",">","value1","是否启用"],
      ]
    }
  ],
  "customIframeXPath": "自定义的用于定位元素所在iframe的xpath表达式",
  "useCustomElementXPath": "是否使用自定义的elementXPath，默认为false",
  "elementPath": [
    {
      "element": "元素名,如div",
      "enabled": "是否启用",
      "predicates": [
        ["attr1","=","value1","是否启用"],
        ["attr2",">","value1","是否启用"],
      ]
    }
  ],
  "customElementXPath": "自定义的用于定位元素的xpath表达式"
}
```
iframePath保存的是用于定位元素所在iframe的路径中的所有元素。

elementPath保持的是在元素所在的iframe用于定位元素的路径中的所有元素。

元素属性中除了元素本身的属性，还可以添加xpath函数，如position(),text()等。

## 详细设计

### 获取所有网页元素分组

### 添加网页元素分组

根据捕获元素时的网页标题和网页图标，创建网页元素分组。

### 删除网页元素分组

删除网页元素分组，同时删除该分组下的所有元素。

### 获取指定分组下的所有网页元素

### 添加网页元素

根据捕获的网页元素信息创建网页元素。

### 修改网页元素

修改网页元素信息。

### 删除网页元素

删除网页元素。

### 获取网页元素引用情况

获取网页元素在流程中的引用情况，包括流程、行号，以及指令。

### 获取未引用网页元素

获取未引用的网页元素。






