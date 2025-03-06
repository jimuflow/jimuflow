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

import requests

from jimuflow.datatypes.core import DataTypeDef, DataTypeRegistry, DataTypeProperty
from jimuflow.locales.i18n import gettext

http_response_type = DataTypeDef("HttpResponse", gettext('HTTP Response'), [
    DataTypeProperty("status_code", "number", gettext('Status Code'), lambda x: x.status_code),
    DataTypeProperty("reason", "text", gettext('Reason'), lambda x: x.reason),
    DataTypeProperty("headers", "dict", gettext('Response Headers'), lambda x: x.headers),
    DataTypeProperty("cookies", "dict", gettext('Response Cookies'),
                     lambda x: requests.utils.dict_from_cookiejar(x.cookies)),
    DataTypeProperty("sessionCookies", "dict", gettext('All cookies set on this session'),
                     lambda x: x.session_cookies),
    DataTypeProperty("text", "text", gettext('Text Response Content'), lambda x: x.text),
    DataTypeProperty("json", "dict", gettext('JSON Response Content'), lambda x: x.json()),
    DataTypeProperty("content", "bytes", gettext('Binary Response Content'), lambda x: x.content),
    DataTypeProperty("encoding", "text", gettext('Response Encoding'), lambda x: x.encoding),
], types=(requests.Response,))


class HttpTypesRegistrar:
    @staticmethod
    def register(data_type_registry: DataTypeRegistry):
        data_type_registry.register(http_response_type)
