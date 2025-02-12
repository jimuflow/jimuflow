# Web Element Management

Use the web element capture tool to capture elements, and the captured web elements will be saved in the element library in JSON format. These elements can later be referenced by their element ID.

The element library files are saved in the `elements\web_elements\<element group>` directory of the application. The file name is the element ID, and the file content is the element information.

Element library directory structure:

```text
Application Directory                          Application root directory
  elements                                     Element library folder
    web_elements                               Web element folder
      group_element_group1                     Element group folder, named after the webpage title where the element is located
        group_icon.png                         Element group icon file, using the webpage icon as the group icon
        element_id1.jsonl                      Element JSON file, element ID is generated using UUID
        element_id1.png                        Element screenshot file
        element_id2.jsonl
        element_id2.png
```

The JSON format of the element file is as follows:
```json lines
{"name": "Element Name","iframeXPath": "XPath expression of the iframe","elementXPath": "XPath expression of the element","createdAt": "Creation time","updatedAt": "Modification time"}
{
  "webPageUrl": "URL of the page where the element is located, used for re-capturing the element",
  "inIframe": "Whether the element is in an iframe, default is false",
  "useCustomIframeXPath": "Whether to use a custom iframeXPath, default is false",
  "iframePath": [
    {
      "element": "Element name, e.g., div",
      "enabled": "Whether enabled",
      "predicates": [
        ["attr1","=","value1","Whether enabled"],
        ["attr2",">","value1","Whether enabled"],
      ]
    }
  ],
  "customIframeXPath": "Custom XPath expression for locating the iframe where the element is located",
  "useCustomElementXPath": "Whether to use a custom elementXPath, default is false",
  "elementPath": [
    {
      "element": "Element name, e.g., div",
      "enabled": "Whether enabled",
      "predicates": [
        ["attr1","=","value1","Whether enabled"],
        ["attr2",">","value1","Whether enabled"],
      ]
    }
  ],
  "customElementXPath": "Custom XPath expression for locating the element"
}
```
`iframePath` stores all elements in the path used to locate the iframe where the element is located.

`elementPath` stores all elements in the path used to locate the element within the iframe where the element is located.

In addition to the element's own attributes, XPath functions such as `position()`, `text()`, etc., can also be added to the element attributes.

## Detailed Design

### Get All Web Element Groups

### Add Web Element Group

Create a web element group based on the webpage title and icon when capturing elements.

### Delete Web Element Group

Delete the web element group and all elements under this group.

### Get All Web Elements Under a Specified Group

### Add Web Element

Create a web element based on the captured web element information.

### Modify Web Element

Modify web element information.

### Delete Web Element

Delete a web element.

### Get Web Element Reference Status

Get the reference status of the web element in the process, including the process, line number, and instruction.

### Get Unreferenced Web Elements

Get unreferenced web elements.