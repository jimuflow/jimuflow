# Developing a New Instruction

This document outlines the general process for developing a new instruction.

## Creating an Instruction Package

All instructions are defined within packages, with each package corresponding to a package directory. Each package directory contains a `jimuflow.json` file, which defines the package's namespace, name, version, and other information.

Format of the `jimuflow.json` file:
```json
{
  "namespace": "Namespace",
  "name": "Name",
  "version": "Version"
}
```

Instruction packages are stored in the `jimuflow/packages` directory under the project root. Currently, the following instruction packages exist:

- `core`: Core instruction package, containing basic instructions and operating system instructions.
- `mouse_keyboard`: Mouse and keyboard instruction package, containing mouse and keyboard instructions.
- `table`: Data table instruction package, containing data table instructions.
- `web_automation`: Web automation instruction package, containing web automation instructions.
- `windows_automation`: Windows automation instruction package, containing Windows automation instructions.

Users can create new instruction packages and define new instructions as needed, or extend existing instruction packages.

To create a new instruction package, simply create a package directory under the `jimuflow/packages` directory. The directory name will be the package name. Inside the directory, create a `jimuflow.json` file and fill in the package information.

## Defining an Instruction

Instructions are defined using a JSON file with a `.comp.json` suffix. The filename is the instruction name, and the file defines the instruction name, the Python class for the instruction, variables, and other configuration information.
```json
{
  "name": "Instruction Name",
  "displayName": "Instruction Display Name",
  "controlFlowType": "Instruction Control Flow Type",
  "type": "Fully qualified class name of the Python class corresponding to the instruction",
  "supportsErrorHandling": "Whether error handling is supported",
  "primaryCategory": "Primary category of the instruction",
  "secondaryCategory": "Secondary category of the instruction",
  "sortNo": "Display order number in the interface",
  "helpUrl": "Online help document path",
  "categories": [
    [
      "Auxiliary category primary class",
      "Auxiliary category secondary class"
    ]
  ],
  "platforms": ["Operating systems supported by the instruction"],
  "variables": [
    {
      "name": "Variable name",
      "type": "Variable type",
      "elementType": "Type of list elements",
      "direction": "Variable direction",
      "defaultValue": "Default value",
      "uiConfig": {
        "label": "Label name displayed on the form",
        "group": "Form group to which it belongs",
        "required": "Whether it is required",
        "sortNo": "Display order number within the form",
        "inputType": "Type of input component",
        "inputEditorType": "Fully qualified class name of the custom input component's Python class",
        "inputValueType": "Value type of the custom input component",
        "placeholder": "Hint information for the input component",
        "helpInfo": "Help information displayed on the input component",
        "dependsOn": {
          "variableName": "Dependent variable name",
          "operator": "Dependency comparison operator",
          "value": "Dependent value"
        },
        "options": [
          {
            "value": "Dropdown option value",
            "label": "Dropdown option label"
          }
        ]
      }
    }
  ]
}
```

Field descriptions:
- `name`: Instruction name, required, serves as the instruction identifier. Instructions within the same package cannot have duplicate names.
- `displayName`: Instruction display name, required, used for display in the interface.
- `controlFlowType`: Instruction control flow type, required. For possible values, refer to the `jimuflow.definition.component_def.ControlFlowType` enumeration class.
- `type`: Fully qualified class name of the Python class corresponding to the instruction, required, used to create the instruction object at runtime.
- `supportsErrorHandling`: Whether error handling is supported, optional. If `True`, the instruction configuration form will display error handling related configurations, and corresponding error handling will be performed at runtime. Otherwise, error handling related configurations will not be displayed, and if the instruction fails at runtime, the application will exit directly.
- `primaryCategory`: Primary category of the instruction, optional, used for display in the interface.
- `secondaryCategory`: Secondary category of the instruction, optional, used for display in the interface.
- `sortNo`: Display order number in the interface, optional, used for display in the interface.
- `helpUrl`: Online help document path, optional, used for display in the interface. All instruction help documents are stored in the `docs/commands` directory as `.md` files.
- `categories`: Auxiliary categories, optional, used for display in the interface. An instruction can have multiple auxiliary categories, each consisting of a primary and an optional secondary class.
- `platforms`: Operating systems supported by the instruction, optional. If not specified, it means all operating systems are supported. For possible values, refer to the `jimuflow.definition.component_def.Platform` enumeration class.
- `variables`: Variable configuration for the instruction.
  - `name`: Variable name, required, serves as the variable identifier. Variables within the same instruction cannot have duplicate names.
  - `type`: Variable type, required. For possible values, refer to the [Expression Data Type Description](../manual/expression.md).
  - `elementType`: Type of list elements, required if the variable type is a list.
  - `direction`: Variable direction, optional, defaults to `LOCAL`, indicating a local variable. For possible values, refer to the `jimuflow.definition.variable_def.VariableDirection` enumeration class.
  - `defaultValue`: Default value of the variable, optional.
  - `uiConfig`: Interface display configuration, only required for input and output variables.
    - `label`: Label name displayed on the form, optional, defaults to the variable name.
    - `group`: Form group to which it belongs, only required for input variables. `general` indicates regular configuration, `advanced` indicates advanced configuration, optional, defaults to `general`.
    - `required`: Whether it is required, only required for input variables, optional, defaults to `True`, indicating the variable is required.
    - `sortNo`: Display order number within the form, optional, defaults to `0`.
    - `inputType`: Type of input component, optional, only required for input variables, defaults to `line_edit`, indicating a single-line text box. For possible values, refer to the `jimuflow.definition.variable_def.VariableUiInputType` enumeration class.
    - `inputEditorType`: Fully qualified class name of the custom input component's Python class, optional, only required if `inputType` is `custom`.
    - `inputValueType`: Value type of the custom input component, optional, only required if `inputType` is `custom`. `expression` indicates the value of the custom input component is an expression, `literal` indicates it is a literal value, defaults to `literal`.
    - `placeholder`: Hint information for the input component, optional, only required for input and output variables, defaults to empty.
    - `helpInfo`: Help information displayed on the input component, optional, only required for input and output variables, defaults to empty.
    - `dependsOn`: Dependency configuration for input or output variables, only displayed on the instruction configuration form if the dependency is met, optional.
      - `variableName`: Dependent input variable name, required.
      - `operator`: Dependency comparison operator, required. Possible values: `"=="` for equal, `"!="` for not equal, `"in"` for in list, `"not_in"` for not in list, `"is_empty"` for empty, `"not_empty"` for not empty, `"is_true"` for true, `"is_false"` for false.
      - `value`: Dependent value, required if the operator is `"=="`, `"!="`, `"in"`, or `"not_in"`.
    - `options`: Required if `inputType` is `combo_box` (dropdown list), to configure dropdown options.
      - `value`: Dropdown option value, required.
      - `label`: Dropdown option label, required.

## Implementing the Instruction Class

Add the instruction class under the `jimuflow.components` package. The instruction class must inherit from `jimuflow.runtime.execution_engine.PrimitiveComponent` and implement the following two methods:

- `display_description`: Returns the description of the instruction, used for display in the interface.
- `execute`: Implements the functional logic of the instruction in this method. You can call `read_input` to read the values of input variables and `write_output` to save results to output variables. The `PrimitiveComponent` class also provides other interface methods; refer to the `PrimitiveComponent` class code for details.