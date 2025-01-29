# 开发一个新指令

本文档描述了开发一个新指令的大致流程。

## 创建指令包

所有指令都定义在包中，每个包对应一个包目录，每个包目录下有一个jimuflow.json文件，该文件定义了包的命名空间、名称、版本等信息。

jimuflow.json文件格式：
```json
{
  "namespace": "命名空间",
  "name": "名称",
  "version": "版本"
}
```

指令包存放在项目根目录下的jimuflow/packages目录下，当前有以下指令包：

- core：核心指令包，包含基础指令、操作系统指令。
- mouse_keyboard：鼠标键盘指令包，包含鼠标键盘指令。
- table：数据表格指令包，包含数据表格指令。
- web_automation：网页自动化指令包，包含网页自动化指令。
- windows_automation：Windows自动化指令包，包含Windows自动化指令。

用户可以根据需要创建新的指令包，并定义新的指令，也可以扩展已有的指令包。

创建新指令包时，只需要在jimuflow/packages目录下创建一个包目录，目录名即为包的名称，目录下创建一个jimuflow.json文件，并填写包信息。

## 定义指令

指令使用一个后缀名为".comp.json"的json文件进行定义，文件名为指令名，文件中定义了指令名称、指令python类、变量等配置信息。
```json
{
  "name": "指令名称",
  "displayName": "指令显示名称",
  "controlFlowType": "指令控制流类型",
  "type": "指令对应python类的完全限定类名",
  "supportsErrorHandling": "是否支持错误处理",
  "primaryCategory": "指令所属一级类",
  "secondaryCategory": "指令所属二级类",
  "sortNo": "界面显示排序号",
  "helpUrl": "在线帮助文档路径",
  "categories": [
    [
      "辅助分类一级类",
      "复制分类二级类"
    ]
  ],
  "platforms": ["指令支持的操作系统"],
  "variables": [
    {
      "name": "变量名",
      "type": "变量类型",
      "elementType": "列表元素的类型",
      "direction": "变量方向",
      "defaultValue": "默认值",
      "uiConfig": {
        "label": "表单上显示的标签名",
        "group": "所属表单分组",
        "required": "是否必填",
        "sortNo": "表单内显示的排序号",
        "inputType": "输入组件的类型",
        "inputEditorType": "自定义输入组件的python类的完全限定类名",
        "inputValueType": "自定义输入组件的值类型",
        "placeholder": "输入组件的提示信息",
        "helpInfo": "输入组件上显示的帮助信息",
        "dependsOn": {
          "variableName": "依赖变量名",
          "operator": "依赖比较操作符",
          "value": "依赖值"
        },
        "options": [
          {
            "value": "下拉选项值",
            "label": "下拉选项标签"
          }
        ]
      }
    }
  ]
}
```

字段说明：
- name：指令名称，必填，作为指令标识，同一个包下的指令不能重名。
- displayName：指令显示名称，必填，用于在界面上显示。
- controlFlowType：指令控制流类型，必填，可取值请参见[jimuflow.definition.component_def.ControlFlowType](../../jimuflow/definition/component_def.py)枚举类。
- type：指令对应python类的完全限定类名，必填，用于在运行时创建指令对象。
- supportsErrorHandling：是否支持错误处理，可选，如果为True，则指令配置表单上将显示错误处理相关配置，并在运行时进行对应错误处理。否则，不显示错误处理相关配置，运行时如果指令出错，应用将直接退出。
- primaryCategory：指令所属一级类，可选，用于在界面上显示。
- secondaryCategory：指令所属二级类，可选，用于在界面上显示。
- sortNo：界面显示排序号，可选，用于在界面上显示。
- helpUrl：在线帮助文档路径，可选，用于在界面上显示。所有指令的帮助文档都存放在docs/commands目录下，以.md结尾的文件。
- categories：辅助分类，可选，用于在界面上显示。一个指令可以有多个辅助分类，辅助分类由一级类和二级类组成，二级类是可选地。
- platforms：指令支持的操作系统，可选，如果不指定，则表示支持所有操作系统，可取值请参见[jimuflow.definition.component_def.Platform](../../jimuflow/definition/component_def.py)枚举类。
- variables：指令的变量配置。
  - name：变量名，必填，作为变量标识，同一个指令下的变量不能重名。
  - type：变量类型，必填，可取值请参见[表达式数据类型说明](../manual/expression.md)。
  - elementType：列表元素的类型，如果变量类型为list列表类型，则需要填写列表元素的类型。
  - direction: 变量方向，可选，默认为LOCAL，表示本地变量，可取值请参见[jimuflow.definition.variable_def.VariableDirection](../../jimuflow/definition/variable_def.py)枚举类。
  - defaultValue：变量的默认值，可选
  - uiConfig：界面显示配置，只有输入变量和输出变量才需要配置。
    - label：表单上显示的标签名，可选，默认为变量名
    - group：所属表单分组，只有输入变量才需要配置，general表示常规配置，advanced表示高级配置，可选，默认为general。
    - required：是否必填，只有输入变量才需要配置，可选，默认为True，表示该变量为必填项。
    - sortNo：表单内显示的排序号，可选，默认为0。
    - inputType：输入组件的类型，可选，只有输入变量才需要配置，默认为line_edit，表示单行文本框，可取值请参见[jimuflow.definition.variable_def.VariableUiInputType](../../jimuflow/definition/variable_def.py)枚举类。
    - inputEditorType：自定义输入组件的python类的完全限定类名，可选，只有inputType为custom时才需要配置。
    - inputValueType：自定义输入组件的值类型，可选，只有inputType为custom时才需要配置，expression表示自定义输入组件的值是一个表达式，literal表示自定义输入组件的值是一个字面值，默认为literal。
    - placeholder：输入组件的提示信息，可选，只有输入变量和输出变量才需要配置，默认为空。
    - helpInfo：输入组件上显示的帮助信息，可选，只有输入变量和输出变量才需要配置，默认为空。
    - dependsOn：输入变量或输出变量的依赖配置，只有依赖满足时，指令配置表单上才会显示该变量配置，可选。
      - variableName：依赖的输入变量名，必填
      - operator：依赖比较操作符，必填，可取值有："=="表示等于，"!="表示不等于，"in"表示在列表中，"not_in"表示不在列表中，"is_empty"表示为空，"not_empty"表示不为空，"is_true"表示为真，"is_false"表示为假。
      - value：依赖的值，如果操作符为"=="、"!="、"in"、"not_in"，则需要配置依赖的值。
    - options：如果inputType为combo_box下拉列表，则需要配置下拉选项。
      - value：下拉选项值，必填
      - label：下拉选项标签，必填

## 实现指令类

在jimuflow.components包下面添加指令类，指令类需要继承jimuflow.runtime.execution_engine.PrimitiveComponent类，然后实现以下两个方法：

- display_description：返回指令的描述信息，用于在界面上显示。
- execute：在该方法中实现指令的功能逻辑，可以调用read_input方法读取输入变量的值，调用write_output将结果保存到输出变量中，PrimitiveComponent类还提供了其他一些接口方法，具体请参见PrimitiveComponent类的代码。
