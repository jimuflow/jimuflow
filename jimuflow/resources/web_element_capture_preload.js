(function () {
    if (window.__preload_js_injected__) {
        return
    }
    const iframeToIds = {}
    window.addEventListener("message", (e) => {
        if (e.data['type'] !== '__post_init_js_injected__') {
            return
        }
        const iframes = Array.from(document.querySelectorAll("iframe"));

        const sourceIframe = iframes.find(
            (iframe) => iframe.contentWindow === e.source,
        );

        iframeToIds[sourceIframe] = e.data.data
    });

    function removeCssClass(value) {
        if (!value) {
            return value
        }
        const newValue = value.replace(/(^|\s+)qt-highlight-\w+(?=$|\s+)/g, '')
        if (newValue !== value) {
            return newValue.trim()
        } else {
            return value
        }
    }

    window.getElementPath = function (element, hasIdBefore, penetratIframe) {
        const pathNode = {
            element: element.tagName.toLowerCase(),
            enabled: false,
            predicates: []
        }
        pathNode.enabled = pathNode.element === 'iframe' || !hasIdBefore
        let hasId = false
        for (const name of element.getAttributeNames()) {
            if (name === 'id') {
                hasId = true
            }
            let value = element.getAttribute(name)
            if (name === 'class') {
                const newValue = removeCssClass(value)
                if (!newValue) {
                    continue
                } else {
                    value = newValue
                }
            }
            pathNode.predicates.push([name, '=', value, name === 'id'])
        }
        let count = 0;
        let position = 0;
        let siblings = element.parentNode.childNodes;
        for (let i = 0; i < siblings.length; i++) {
            let sibling = siblings[i];
            if (sibling.nodeType === 1 && sibling.tagName === element.tagName) {
                count++;
            }
            if (sibling === element) {
                position = count
            }
        }
        pathNode.predicates.push(['position()', '=', position + '', !hasId])
        let notHasChildElements = ![...element.childNodes].some(node => node.nodeType === 1)
        if (notHasChildElements) {
            pathNode.predicates.push(['text()', '=', element.innerText, false])
        }
        if (element.parentElement) {
            const path = getElementPath(element.parentElement,
                pathNode.element === 'iframe' ? hasId : (hasIdBefore || hasId))
            path.push(pathNode)
            return path
        } else if (penetratIframe && element.ownerDocument.defaultView.frameElement) {
            const path = getElementPath(element.ownerDocument.defaultView.frameElement, false)
            path.push(pathNode)
            return path
        } else {
            return [pathNode]
        }
    }

    window.escapeXPathString = function (str) {
        const escapedChars = []
        for (let i = 0; i < str.length; i++) {
            const char = str.charAt(i)
            if (char === '"' || char === '\'' || char === '\\') {
                escapedChars.push('\\' + char)
            } else {
                escapedChars.push(char)
            }
        }
        return escapedChars.join('')
    }

    window.buildXPath = function (path, xpathIndices) {
        let xpath = ""
        for (let i = 0; i < xpathIndices.length; i++) {
            const nodeIndex = xpathIndices[i]
            const prevNodeIndex = i > 0 ? xpathIndices[i - 1] : 0
            if (nodeIndex === 0 || nodeIndex - prevNodeIndex === 1) {
                xpath += '/'
            } else {
                xpath += '//'
            }
            const pathNode = path[nodeIndex]
            const enabledPredicate = pathNode.predicates.find(predicate => predicate[3])
            if (enabledPredicate[0] === 'position()') {
                xpath += pathNode.element + '[' + enabledPredicate[2] + ']'
            } else {
                xpath += pathNode.element + '[@' + enabledPredicate[0] + '=\'' + escapeXPathString(enabledPredicate[2]) + '\']'
            }
        }
        return xpath
    }

    function trim(str) {
        return str ? str.trim() : str
    }

    const tagNameToElementType = {
        'A': 'Link',
        'ABBR': 'Abbreviation Text',
        'ADDRESS': 'Address',
        'AREA': 'Image Map Area',
        'ARTICLE': 'Article Contents',
        'ASIDE': 'Aside',
        'AUDIO': 'Audio',
        'B': 'Text',
        'BASE': 'Document Base URL',
        'BDI': 'Text',
        'BDO': 'Text',
        'BLOCKQUOTE': 'Block Quotation',
        'BODY': 'Document Body',
        'BR': 'Line Break',
        'BUTTON': 'Button',
        'CANVAS': 'Canvas',
        'Caption': 'Table Caption',
        'CITE': 'Citation',
        'CODE': 'Code',
        'COL': 'Table Column',
        'COLGROUP': 'Table Column Group',
        'DATA': 'Data',
        'DATALIST': 'Data List',
        'DD': 'Description Details',
        'DEL': 'Deleted Text',
        'DETAILS': 'Details disclosure',
        'DFN': 'Definition',
        'DIALOG': 'Dialog',
        'DIV': 'Block Element',
        'DL': 'Description List',
        'DT': 'Description Term',
        'EM': 'Emphasis',
        'EMBED': 'Embedded Content',
        'FIELDSET': 'Fieldset',
        'FIGCAPTION': 'Figure Caption',
        'FIGURE': 'Figure',
        'FOOTER': 'Footer',
        'FORM': 'Form',
        'H1': 'First-level title',
        'H2': 'Second-level title',
        'H3': 'Third-level title',
        'H4': 'Fourth-level title',
        'H5': 'Fifth-level title',
        'H6': 'Sixth-level title',
        'HEAD': 'Document Head',
        'HEADER': 'Header',
        'HGROUP': 'Heading Group',
        'HR': 'Horizontal Rule',
        'HTML': 'Document',
        'I': 'Text',
        'IFRAME': 'Inline Frame',
        'IMG': 'Image',
        'INS': 'Inserted Text',
        'KBD': 'Keyboard Input',
        'LABEL': 'Label',
        'LEGEND': 'Field Set Legend',
        'LI': 'List Item',
        'LINK': 'External Resource Link',
        'MAIN': 'Main Content',
        'MAP': 'Image Map',
        'MARK': 'Mark Text',
        'MENU': 'Menu',
        'META': 'Metadata',
        'METER': 'Meter',
        'NAV': 'Navigation',
        'OBJECT': 'Embedded Object',
        'OL': 'Ordered List',
        'OPTGROUP': 'Option Group',
        'OPTION': 'Option',
        'OUTPUT': 'Output',
        'P': 'Text',
        'PICTURE': 'Picture',
        'PRE': 'Preformatted Text',
        'PROGRESS': 'Progress Indicator',
        'Q': 'Inline Quotation',
        'S': 'Text',
        'SAMP': 'Sample Output',
        'SCRIPT': 'Script',
        'SEARCH': 'Search',
        'SECTION': 'Section',
        'SELECT': 'Drop-down box',
        'SLOT': 'Web Component Slot',
        'SMALL': 'Side Comment',
        'SOURCE': 'Media Source',
        'SPAN': 'Text',
        'STRONG': 'Text',
        'STYLE': 'Style',
        'SUB': 'Subscript',
        'SUMMARY': 'Summary',
        'SUP': 'Superscript',
        'TABLE': 'Table',
        'TBODY': 'Table Body',
        'TD': 'Table Cell',
        'TEMPLATE': 'Content Template',
        'TEXTAREA': 'Text Area',
        'TFOOT': 'Table Footer',
        'TH': 'Table Header Cell',
        'THEAD': 'Table Header',
        'TIME': 'Time',
        'TITLE': 'Document Title',
        'TR': 'Table Row',
        'TRACK': 'Media Track',
        'U': 'Text',
        'UL': 'Unordered List',
        'VAR': 'Variable',
        'VIDEO': 'Video',
        'WBR': 'Line Break Opportunity',
    }

    function getElementType(element) {
        const tagName = element.tagName
        let elementType = tagNameToElementType[tagName]
        if (elementType) {
            return elementType
        }
        if (tagName === 'INPUT') {
            switch (element.type) {
                case 'password':
                    return 'Password Input'
                case 'checkbox':
                    return 'Checkbox'
                case 'radio':
                    return 'Radio Button'
                case 'file':
                    return 'File Input'
                case 'button':
                case 'submit':
                case 'reset':
                    return 'Button'
                default:
                    return 'Input box'
            }
        }
        return tagName
    }

    window.getElementInfo = function (element) {
        // 按规则生成元素名称：元素类型_元素文本前15个字
        let element_desc = trim(element.innerText)
        if (!element_desc && (element.tagName === 'BUTTON' || (element.tagName === 'INPUT' &&
            (element.type === 'button' || element.type === 'reset' || element.type === 'submit')))) {
            element_desc = trim(element.value)
        }
        if (!element_desc) {
            element_desc = trim(element.getAttribute("title"))
        }
        if (!element_desc) {
            element_desc = trim(element.getAttribute('id'))
        }
        if (!element_desc) {
            element_desc = trim(removeCssClass(element.getAttribute('class')))
        }
        if (element_desc) {
            element_desc = element_desc.substring(0, 15).replace(/\s+/g, '_')
        }
        const name = element_desc
        const elementType = getElementType(element)
        const webPageUrl = window.location.href;
        const path = getElementPath(element)
        let iframeXPathIndices = []
        let elementXPathIndices = []
        let inIframe = false
        let iframeIndex = -1
        for (let i = path.length - 1; i >= 0; i--) {
            const pathNode = path[i]
            if (pathNode.element === 'iframe') {
                if (!inIframe) {
                    iframeIndex = i
                }
                inIframe = true
                iframeXPathIndices.push(i)
            } else if (pathNode.enabled) {
                if (inIframe) {
                    iframeXPathIndices.push(i)
                } else {
                    elementXPathIndices.push(i)
                }
            }
        }
        iframeXPathIndices.reverse()
        elementXPathIndices.reverse()
        const rect = element.getBoundingClientRect();
        return {
            name,
            elementType,
            iframeXPath: buildXPath(path, iframeXPathIndices),
            elementXPath: buildXPath(path, elementXPathIndices),
            webPageUrl,
            inIframe,
            useCustomIframeXPath: false,
            iframePath: iframeIndex === -1 ? [] : path.slice(0, iframeIndex + 1),
            customIframeXPath: '',
            useCustomElementXPath: false,
            elementPath: iframeIndex === -1 ? path : path.slice(iframeIndex + 1),
            customElementXPath: '',
            rect: {x: rect.x, y: rect.y, width: rect.width, height: rect.height}
        }
    }

    window.getElementInfoFromPoint = function (x, y, cssClass) {
        const highlightedElements = document.querySelectorAll('.'+cssClass);
        highlightedElements.forEach(element => {
            element.classList.remove(cssClass);
        });
        const ele = document.elementFromPoint(x, y);
        const elementInfo = getElementInfo(ele)
        elementInfo['point'] = [x, y]
        if (ele.tagName !== 'IFRAME') {
            ele.classList.add(cssClass);
        } else {
            elementInfo['iframeId'] = iframeToIds[ele]
        }
        return JSON.stringify(elementInfo);
    }

    window.highlightElement = function (xpath, cssClass) {
        const result = document.evaluate(xpath, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
        for (let i = 0; i < result.snapshotLength; i++) {
            if (i === 0) {
                result.snapshotItem(i).scrollIntoView();
            }
            result.snapshotItem(i).classList.add(cssClass);
        }
        return result.snapshotLength;
    }

    window.findIframeByXpathSteps = function (xpath_steps,scrollIntoView) {
        let contextNodes = [document]
        while (xpath_steps.length > 0) {
            const step = xpath_steps.shift()
            const nextNodes = []
            for (const node of contextNodes) {
                const nodes = document.evaluate(step, node, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null)
                for (let i = 0; i < nodes.snapshotLength; i++) {
                    nextNodes.push(nodes.snapshotItem(i))
                }
            }
            const iframeEle = nextNodes.find(node => node.tagName === 'IFRAME')
            if (iframeEle) {
                if(scrollIntoView){
                    iframeEle.scrollIntoView();
                }
                return JSON.stringify({
                    iframeId: iframeToIds[iframeEle],
                    xpath_steps: xpath_steps
                })
            }
            contextNodes = nextNodes
        }
        return JSON.stringify({iframeId: null, xpath_steps: []})
    }
    window.__preload_js_injected__ = true
})()
