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
import logging
import os.path

import requests
from requests.auth import HTTPDigestAuth, HTTPBasicAuth

from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow

logger = logging.getLogger(__name__)


class SendHttpRequestComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        return gettext('Send ##{method}## request to ##{url}##, and save the response object to ##{response}##').format(
            url=flow_node.input('requestUrl'),
            method=flow_node.input('requestMethod'), response=flow_node.output('response'))

    async def execute(self) -> ControlFlow:
        url = self.read_input('requestUrl')
        method = self.read_input('requestMethod')
        request_kwargs = {
            'verify': self.read_input('verify')
        }
        params = []
        for item in (self.node.input('requestParams') or []):
            name = self.evaluate_expression_in_process(item['name'])
            value = self.evaluate_expression_in_process(item['value'])
            params.append((name, value))
        headers = {}
        for item in (self.read_input('requestHeaders') or []):
            name = self.evaluate_expression_in_process(item['name'])
            value = self.evaluate_expression_in_process(item['value'])
            headers[name] = value

        def set_header_if_absent(name, value):
            for k, v in headers.items():
                if k.lower() == name.lower():
                    return
            headers[name] = value

        body_type = self.read_input('requestBodyType')
        files = []
        data = None
        if body_type == 'form-data':
            data = []
            for item in self.read_input('requestMultipartForm'):
                name = self.evaluate_expression_in_process(item['name'])
                value = self.evaluate_expression_in_process(item['value'])
                if item['type'] == 'file':
                    if value:
                        files.append((name, open(value, 'rb')))
                else:
                    data.append((name, value))
        elif body_type == 'x-www-form-urlencoded':
            data = []
            for item in self.read_input('requestForm'):
                name = self.evaluate_expression_in_process(item['name'])
                value = self.evaluate_expression_in_process(item['value'])
                data.append((name, value))
        elif body_type == 'json':
            data = self.read_input('requestJson')
            set_header_if_absent('Content-Type', 'application/json')
        elif body_type == 'xml':
            data = self.read_input('requestXml')
            set_header_if_absent('Content-Type', 'application/xml')
        elif body_type == 'raw':
            data = self.read_input('requestText')
            set_header_if_absent('Content-Type', 'text/plain')
        elif body_type == 'binary':
            data = open(self.read_input('requestFile'), 'rb')
            set_header_if_absent('Content-Type', 'application/octet-stream')
        if params:
            request_kwargs['params'] = params
        if headers:
            request_kwargs['headers'] = headers
        if data:
            request_kwargs['data'] = data
        if files:
            request_kwargs['files'] = files
        cookies = {}
        for item in (self.read_input('requestCookies') or []):
            name = self.evaluate_expression_in_process(item['name'])
            value = self.evaluate_expression_in_process(item['value'])
            cookies[name] = value
        if cookies:
            request_kwargs['cookies'] = cookies
        if self.read_input('enableAuth'):
            auth_method = self.read_input('authMethod')
            if auth_method == 'http_basic':
                request_kwargs['auth'] = HTTPBasicAuth(self.read_input('username'), self.read_input('password'))
            elif auth_method == 'http_digest':
                request_kwargs['auth'] = HTTPDigestAuth(self.read_input('username'), self.read_input('password'))
        if self.read_input('enableClientCert'):
            client_cert = self.read_input('clientCert')
            client_key = self.read_input('clientKey')
            if client_key:
                request_kwargs['cert'] = (client_cert, client_key)
            else:
                request_kwargs['cert'] = client_cert
        if self.read_input('enableProxy'):
            proxy_config = self.node.input('proxy')
            proxy = proxy_config['type'].lower() + '://'
            proxy_user = self.evaluate_expression_in_process(proxy_config['user']) if proxy_config['user'] else ''
            proxy_password = self.evaluate_expression_in_process(proxy_config['password']) if proxy_config[
                'password'] else ''
            if proxy_user:
                proxy += proxy_user + ':' + proxy_password + '@'
            proxy += self.evaluate_expression_in_process(proxy_config['host'])
            proxy += ':' + self.evaluate_expression_in_process(proxy_config['port'])
            request_kwargs['proxies'] = {'http': proxy, 'https': proxy}
        request_kwargs['timeout'] = float(self.read_input('timeout'))
        save_to_file = self.read_input('saveToFile')
        request_kwargs['stream'] = save_to_file
        with requests.Session() as s:
            response = s.request(method, url, **request_kwargs)
            if save_to_file:
                save_directory = self.read_input('saveDirectory')
                if not os.path.exists(save_directory):
                    os.makedirs(save_directory)
                filename = os.path.join(save_directory, self.read_input('fileName'))
                with open(filename, 'xb') as fd:
                    for chunk in response.iter_content(chunk_size=4096):
                        fd.write(chunk)
            else:
                if self.read_input('setResponseEncoding'):
                    encoding = self.read_input('responseEncoding')
                    if encoding == 'auto':
                        response.encoding = response.apparent_encoding
                    else:
                        response.encoding = encoding
            response.session_cookies = requests.utils.dict_from_cookiejar(s.cookies)
            await self.write_output('response', response)
            return ControlFlow.NEXT
