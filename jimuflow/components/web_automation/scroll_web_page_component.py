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

from playwright.async_api import Page

from jimuflow.common.uri_utils import describe_element_uri
from jimuflow.components.web_automation.playwright_utils import get_element_by_uri
from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow


class ScrollWebPageComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        scroll_type = flow_node.input('scrollType')
        if scroll_type == 'top':
            return gettext('Scroll web page ##{webPage}## to top').format(webPage=flow_node.input('webPage'))
        elif scroll_type == 'bottom':
            return gettext('Scroll web page ##{webPage}## to bottom').format(webPage=flow_node.input('webPage'))
        elif scroll_type == 'page':
            return gettext('Scroll web page ##{webPage}## ##{scrollTimes}## pages').format(
                webPage=flow_node.input('webPage'), scrollTimes=flow_node.input('scrollTimes'))
        else:
            return gettext('Scroll web page ##{webPage}## to element ##{scrollToElement}##').format(
                webPage=flow_node.input('webPage'),
                scrollToElement=describe_element_uri(flow_node.process_def.package, flow_node.input('scrollToElement')))

    async def execute(self) -> ControlFlow:
        page: Page = self.read_input('webPage')
        scroll_on_element = self.read_input('scrollOnElement')
        scroll_type = self.read_input('scrollType')
        scroll_times = int(self.read_input('scrollTimes'))
        scroll_interval = float(self.read_input('scrollInterval'))
        wait_time = float(self.read_input('waitTime'))
        if scroll_type == 'element':
            scroll_to_element = await get_element_by_uri(self, page, self.read_input('scrollToElement'), wait_time)
            scroll_to_element_handle = await scroll_to_element.element_handle(
                timeout=wait_time * 1000)
        else:
            scroll_to_element_handle = None
        scroll_behavior = self.read_input('scrollBehavior')
        if scroll_on_element:
            scroll_element_uri = self.read_input('scrollElement')
            scroll_element = await get_element_by_uri(self, page, scroll_element_uri, wait_time)
            find_ancestor = self.read_input('findAncestorWhenElementIsNotScrollable')
            await scroll_element.evaluate("""
            async (scroll_element,[find_ancestor,scroll_type,scroll_times,scroll_interval,scroll_to_element,scroll_behavior])=>{
                function hasVerticalScrollbar(ele){
                    const hasVerticalScrollbar = ele.scrollHeight > ele.clientHeight;
                    const computedStyle = window.getComputedStyle(ele);
                    return hasVerticalScrollbar && (computedStyle.overflowY === 'scroll' || computedStyle.overflowY === 'auto')
                }
                if(!hasVerticalScrollbar(scroll_element)){
                    if(!find_ancestor){
                        return false
                    }
                    let found=false
                    while(scroll_element.parentElement){
                        if(hasVerticalScrollbar(scroll_element.parentElement)){
                            scroll_element=scroll_element.parentElement
                            found=true
                            break
                        }
                    }
                    if(!found){
                        return false
                    }
                }
                if(scroll_type==='top'){
                    scroll_element.scroll({
                      top: 0,
                      left: 0,
                      behavior: scroll_behavior
                    })
                }else if(scroll_type==='bottom'){
                    scroll_element.scroll({
                      top: scroll_element.scrollHeight-scroll_element.clientHeight,
                      left: 0,
                      behavior: scroll_behavior
                    })
                }else if(scroll_type==='page'){
                    const direction=scroll_times>0?1:-1
                    for(let i=0;i<Math.abs(scroll_times);i++){
                        if(i>0){
                            await new Promise(r=>setTimeout(r,scroll_interval*1000))
                        }
                        scroll_element.scrollBy({
                          top: scroll_element.clientHeight*direction,
                          left: 0,
                          behavior: scroll_behavior
                        })
                    }
                }else if(scroll_type==='element'){
                    scroll_to_element.scrollIntoView({ behavior: scroll_behavior});
                }
                return true
            }""", [find_ancestor, scroll_type, scroll_times, scroll_interval, scroll_to_element_handle,
                   scroll_behavior],
                                          timeout=wait_time * 1000)
        else:
            await page.evaluate("""
            async ([scroll_type,scroll_times,scroll_interval,scroll_to_element,scroll_behavior])=>{
                if(scroll_type==='top'){
                    window.scroll({
                      top: 0,
                      left: 0,
                      behavior: scroll_behavior
                    })
                }else if(scroll_type==='bottom'){
                    window.scroll({
                      top: document.body.scrollHeight,
                      left: 0,
                      behavior: scroll_behavior
                    })
                }else if(scroll_type==='page'){
                    const direction=scroll_times>0?1:-1
                    for(let i=0;i<Math.abs(scroll_times);i++){
                        if(i>0){
                            await new Promise(r=>setTimeout(r,scroll_interval*1000))
                        }
                        window.scrollBy({
                          top: window.innerHeight*direction,
                          left: 0,
                          behavior: scroll_behavior
                        })
                    }
                }else if(scroll_type==='element'){
                    scroll_to_element.scrollIntoView({ behavior: scroll_behavior});
                }
                return true
            }""", [scroll_type, scroll_times, scroll_interval, scroll_to_element_handle, scroll_behavior])

        return ControlFlow.NEXT
