# Extract Window

Obtain information such as the title of the window and the name of the process it belongs to.

## Instruction Configuration

![General Configuration Dialog Box for Obtaining Window Information](extract_window_general_config.png)

### Window Acquisition Method

Select the method of obtaining the window:

* Window Object: Activate the selected window object.
* Window Title or Class Name: Activate the window with the specified title or class name.
* Capture Window Element: Activate the window where the window element is located.

### Window Object

Select a window object from the process variables.

### Window Title

Enter the window title. You can also click the "Select" button to select the title of a window from all the currently open desktop windows.

### Use Window Class Name

If this option is checked, the window class name will be used as a matching condition simultaneously.

### Window Class Name

Enter the window class name. You can also click the "Select" button to select the class name of a window from all the currently open desktop windows.

### Use Regular Expression Matching

If this option is checked, the window title will be matched as a regular expression.

### Window Element

Select a window element from the element library, or click the "Capture Element" button to obtain it using the tool. For details, please refer to [Window Element Capture Tool](../../../manual/window_element_capture_tool.md).

### Extraction Type

- Window Title: Obtain the title of the window.
- Process Name of the Window: Obtain the name of the process where the window is located.

### Extraction Result

Enter the variable name used to save the extraction result.

### Error Handling

If an error occurs during the execution of the instruction, error handling will be performed. For details, see [Error Handling of Instructions](../../../manual/error_handling.md).