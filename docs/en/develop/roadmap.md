# Feature List

1. **[Completed]** Merged input attributes and output attributes into a variable panel, and added process variable display.
2. **[Completed]** Optimized the run log panel by using QLabel to display logs.
3. **[Completed]** Optimized the variable value panel to support viewing the call chain and using QTableView to display the variable list at call locations.
4. **[Completed]** Implemented the error list panel.
5. **[Completed]** Moved the process list to the left and merged it with the component list into a QTabWidget.
6. **[Completed]** Removed the basic attribute panel of the process and replaced it with a dialog for configuration.
7. **[Completed]** Unified input attributes and output attributes into the concept of variables. Variables are divided into three types: in variables, out variables, and local variables.
8. **[Completed]** Modified processes need to be marked with an asterisk, and users should be prompted to save before closing the process or application.
9. **[Completed]** Users should be prompted for confirmation when deleting a process.
10. **[Completed]** Added a close button to the process tab and removed the close process button from the toolbar.
11. **[Completed]** Implemented breakpoint debugging functionality.
12. **[Completed]** Added error handling for components.
13. **[Completed]** Optimized the display of process nodes to make it more intuitive.
14. **[Completed]** Customized the configuration dialog for the If component, implemented internationalization, and changed the condition field to a dropdown.
15. **[Completed]** Implemented expressions similar to Octopus RPA.
16. **[Completed]** Implemented an expression editor similar to Octopus RPA.
17. **[Completed]** Optimized the expression editor: added support for popping up a variable dropdown and expression validation.
18. **[Completed]** Implemented various components required for web automation.
19. **[Completed]** Expressions now support array indexing.
20. **[Completed]** Refactored the process execution using asyncio.
21. **[Completed]** Automatically release resources requested by components.
22. **[Completed]** Configured the component dialog in the component definition file, divided component parameters into general and advanced parameters, and implemented dependencies between parameters, mandatory fields, input component configuration, parameter display order, and internationalization.
23. **[Completed]** Optimized the component list to support two-level categorization.
24. **[Completed]** Implemented a variable name input component for use as an input component for output variables.
25. **[Completed]** Improved the variable type system.
26. **[Completed]** Added data table-related components.
27. **[Completed]** Improved the usability of the variable configuration interface: internationalization and interaction experience.
28. **[Completed]** Added more basic components: condition judgment, loops, data processing, date operations, string operations, and operating system operations.
29. **[Completed]** Added tooltips for each configuration item in the component configuration dialog.
30. **[Completed]** Beautified the component configuration dialog: alignment and layout.
31. **[Completed]** Improved process execution logs: location, component execution logs, and error logs.
32. **[Completed]** Optimized the variable list: displayed variable direction and type.
33. **[v2]** Supported starting processes via the command line.
34. **[Completed]** Optimized the configuration of process input variables to support configuring UI properties such as variable editors.
35. **[Completed]** Optimized the input variable reading interface to automatically distinguish between expressions and literals based on the variable editor type and handle default values.
36. **[Completed]** Added a start process dialog to support the configuration of startup parameters.
37. **[Completed]** Optimized the expression editor to support multi-line text input.
38. **[Completed]** Tested and released the first version: UI testing, cross-platform testing, and packaging.
39. **[Completed]** Added undo and redo functionality.
40. **[v2]** Refactored the code to improve readability and maintainability.
41. **[Completed]** Used PyBabel for internationalization, with some texts still pending internationalization.
42. **[v2]** All component input variables need to support both literal and expression input methods, with the ability to switch between them.
43. **[Completed]** Renamed components to instructions, as "instruction" is more appropriate.
44. **[Completed]** Fixed the issue where process node names were invisible in dark mode.
45. **[Completed]** Added unit tests.
46. Added several classic process examples.
47. **[In Progress]** Writing the user manual.
48. **[Completed]** Displayed the application name in the title bar of the main window after opening the application.
49. **[Completed]** Added an about dialog.
50. Determined the open-source license to be used.
51. **[In Progress]** Added main process settings functionality and the ability to run the application.
52. Windows automation: PyAutoGUI, PyWinAuto, SikuliX1, PyGetWindow.
53. **[Completed]** Developed a tool to obtain XPath expressions for web elements.
54. **[Completed]** Developed a tool to obtain web cookies.
55. **[Completed]** Clicking on an error in the error list will jump to the line where the error occurred.
56. **[Completed]** Prevented running processes with errors.
57. **[Completed]** Optimized the instruction list to support searching and improved the tab display method.
58. Added a plugin mechanism to extend the instruction set.
59. **[Completed]** Optimized the judgment of whether a process has changed in the undo/redo functionality.
60. Changed toolbar buttons to icon buttons.
61. **[Completed]** Optimized the main window layout settings to support resizing various areas.
62. **[Completed]** Instruction definitions now support configuring multiple categories.
63. **[Completed]** Supported copying and pasting instructions between processes.
64. **[Completed]** Supported modifying instruction indentation or dragging instructions.
65. **[Completed]** Developed a relative XPath acquisition tool.
66. **[Completed]** Optimized the dropdown tooltip in the expression editor to display variable types and attributes.
67. **[Completed]** Supported opening sub-processes in a process via the right-click menu.
68. **[Completed]** Added an open browser instruction with proxy support.
69. **[Completed]** Implemented mouse and keyboard control instructions based on PyAutoGUI.
70. **[Completed]** Added process resource management.
71. **[Completed]** Added a search box to the process list.
72. **[v2]** Added a screenshot tool.
73. Fixed the issue where QT windows automatically resize based on content.