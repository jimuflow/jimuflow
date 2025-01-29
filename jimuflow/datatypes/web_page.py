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

from playwright.async_api import Page, BrowserContext, ElementHandle, Locator

from jimuflow.locales.i18n import gettext
from .core import DataTypeRegistry, DataTypeDef, DataTypeProperty

web_browser_type = DataTypeDef("WebBrowser", gettext('Web Browser'), [], types=(BrowserContext,))

web_page_type = DataTypeDef("WebPage", gettext('Web Page'), [
    DataTypeProperty("url", "text", gettext("Web page url")),
], types=(Page,))

web_element_type = DataTypeDef("WebElement", gettext('Web Element'), [
], types=(ElementHandle,Locator))


class WebPageRegistrar:
    @staticmethod
    def register(data_type_registry: DataTypeRegistry):
        data_type_registry.register(web_browser_type)
        data_type_registry.register(web_page_type)
        data_type_registry.register(web_element_type)
