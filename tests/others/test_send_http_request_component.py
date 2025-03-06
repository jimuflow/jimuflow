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

import json
import os
import tempfile

import pytest
import requests
from requests import ReadTimeout

from jimuflow.components.others import SendHttpRequestComponent
from jimuflow.runtime.execution_engine import ControlFlow
from jimuflow.runtime.expression import escape_string
from tests.utils import create_component_context


@pytest.mark.asyncio
@pytest.mark.parametrize("request_method", ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"])
async def test_request_method(httpbin, request_method):
    async with create_component_context(SendHttpRequestComponent) as component:
        # httpbin api 文档：https://httpbin.org/legacy
        component.node.inputs = {
            "requestUrl": escape_string(httpbin.url + '/anything'),
            "requestMethod": request_method,
            "requestParams": [{"name": escape_string("param1"), "value": escape_string("hello")},
                              {"name": escape_string("param1"), "value": escape_string("你好")},
                              {"name": escape_string("param2"), "value": escape_string("test")}],
            "requestCookies": [{"name": escape_string("cookie1"), "value": escape_string("hello")},
                               {"name": escape_string("cookie2"), "value": escape_string("123")}],
            "requestHeaders": [{"name": escape_string("x-test-1"), "value": escape_string("abc")},
                               {"name": escape_string("x-test-2"), "value": escape_string("456")}],
        }
        component.node.outputs = {
            "response": 'r'
        }
        assert (await component.execute()) == ControlFlow.NEXT
        r: requests.Response = component.process.get_variable('r')
        assert r.status_code == 200
        assert r.reason == 'OK'
        if request_method == 'HEAD' or request_method == 'OPTIONS':
            assert r.text == ''
        else:
            assert r.encoding == 'utf-8'
            assert r.json()['args'] == {'param1': ['hello', '你好'], 'param2': 'test'}
            assert r.json()['headers']['Cookie'] == 'cookie1=hello; cookie2=123'
            assert r.json()['headers']['X-Test-1'] == 'abc'
            assert r.json()['headers']['X-Test-2'] == '456'


@pytest.mark.asyncio
async def test_post_json(httpbin):
    async with create_component_context(SendHttpRequestComponent) as component:
        component.node.inputs = {
            "requestUrl": escape_string(httpbin.url + '/post'),
            "requestMethod": "POST",
            "requestParams": [{"name": escape_string("foo"), "value": escape_string("bar")}],
            "requestBodyType": "json",
            "requestJson": escape_string(json.dumps({"id": 12, "name": "foo"}))
        }
        component.node.outputs = {
            "response": 'r'
        }
        assert (await component.execute()) == ControlFlow.NEXT
        r: requests.Response = component.process.get_variable('r')
        assert r.status_code == 200
        assert r.json()['headers']['Content-Type'] == "application/json"
        assert r.json()['args'] == {'foo': 'bar'}
        assert r.json()['json'] == {"id": 12, "name": "foo"}


@pytest.mark.asyncio
async def test_put_xml(httpbin):
    async with create_component_context(SendHttpRequestComponent) as component:
        xml_data = """
        <a>
            <b id="1">hello</b>
            <b id="2">你好</b>
        </a>
        """
        component.node.inputs = {
            "requestUrl": escape_string(httpbin.url + '/put'),
            "requestMethod": "PUT",
            "requestBodyType": "xml",
            "requestXml": escape_string(xml_data)
        }
        component.node.outputs = {
            "response": 'r'
        }
        assert (await component.execute()) == ControlFlow.NEXT
        r: requests.Response = component.process.get_variable('r')
        assert r.status_code == 200
        assert r.json()['headers']['Content-Type'] == "application/xml"
        assert r.json()['data'] == xml_data


@pytest.mark.asyncio
async def test_patch_raw(httpbin):
    async with create_component_context(SendHttpRequestComponent) as component:
        raw_data = 'hello你好'
        component.node.inputs = {
            "requestUrl": escape_string(httpbin.url + '/patch'),
            "requestMethod": "PATCH",
            "requestBodyType": "raw",
            "requestText": escape_string(raw_data)
        }
        component.node.outputs = {
            "response": 'r'
        }
        assert (await component.execute()) == ControlFlow.NEXT
        r: requests.Response = component.process.get_variable('r')
        assert r.status_code == 200
        assert r.json()['headers']['Content-Type'] == "text/plain"
        assert r.json()['data'] == raw_data


@pytest.mark.asyncio
async def test_post_file(httpbin):
    async with create_component_context(SendHttpRequestComponent) as component:
        raw_data = 'hello你好'
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(raw_data)
            temp_file_name = temp_file.name
        component.node.inputs = {
            "requestUrl": escape_string(httpbin.url + '/post'),
            "requestMethod": "POST",
            "requestBodyType": "binary",
            "requestFile": escape_string(temp_file_name)
        }
        component.node.outputs = {
            "response": 'r'
        }
        assert (await component.execute()) == ControlFlow.NEXT
        r: requests.Response = component.process.get_variable('r')
        assert r.status_code == 200
        assert r.json()['headers']['Content-Type'] == "application/octet-stream"
        assert r.json()['data'] == raw_data


@pytest.mark.asyncio
async def test_post_form(httpbin):
    async with create_component_context(SendHttpRequestComponent) as component:
        component.node.inputs = {
            "requestUrl": escape_string(httpbin.url + '/post'),
            "requestMethod": "POST",
            "requestBodyType": 'x-www-form-urlencoded',
            "requestForm": [{"name": escape_string("param1"), "value": escape_string("hello")},
                            {"name": escape_string("param1"), "value": escape_string("你好")},
                            {"name": escape_string("param2"), "value": escape_string("test")}],
        }
        component.node.outputs = {
            "response": 'r'
        }
        assert (await component.execute()) == ControlFlow.NEXT
        r: requests.Response = component.process.get_variable('r')
        assert r.status_code == 200
        assert r.json()['headers']['Content-Type'] == 'application/x-www-form-urlencoded'
        assert r.json()['form'] == {'param1': ['hello', '你好'], 'param2': 'test'}


@pytest.mark.asyncio
async def test_post_multipart_form(httpbin):
    async with create_component_context(SendHttpRequestComponent) as component:
        raw_data = 'hello你好'
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(raw_data)
            temp_file_name = temp_file.name
        component.node.inputs = {
            "requestUrl": escape_string(httpbin.url + '/post'),
            "requestMethod": "POST",
            "requestBodyType": "form-data",
            "requestMultipartForm": [
                {"name": escape_string("param1"), "type": "text", "value": escape_string("test测试")},
                {"name": escape_string("param2"), "type": "file", "value": escape_string(temp_file_name)}]
        }
        component.node.outputs = {
            "response": 'r'
        }
        assert (await component.execute()) == ControlFlow.NEXT
        r: requests.Response = component.process.get_variable('r')
        assert r.status_code == 200
        assert r.json()['headers']['Content-Type'].startswith('multipart/form-data')
        assert r.json()['form'] == {'param1': 'test测试'}
        assert r.json()['files'] == {'param2': 'hello你好'}


@pytest.mark.asyncio
async def test_basic_auth(httpbin):
    async with create_component_context(SendHttpRequestComponent) as component:
        user = 'testuser'
        passwd = 'testpwd'
        component.node.inputs = {
            "requestUrl": escape_string(f'{httpbin.url}/basic-auth/{user}/{passwd}'),
            "enableAuth": True,
            "authMethod": "http_basic",
            "username": escape_string(user),
            "password": escape_string(passwd)
        }
        component.node.outputs = {
            "response": 'r'
        }
        assert (await component.execute()) == ControlFlow.NEXT
        r: requests.Response = component.process.get_variable('r')
        assert r.status_code == 200
        assert r.json()['authenticated'] is True
        assert r.json()['user'] == user


@pytest.mark.asyncio
async def test_digest_auth(httpbin):
    async with create_component_context(SendHttpRequestComponent) as component:
        user = 'testuser'
        passwd = 'testpwd'
        component.node.inputs = {
            "requestUrl": escape_string(f'{httpbin.url}/digest-auth/auth/{user}/{passwd}'),
            "enableAuth": True,
            "authMethod": "http_digest",
            "username": escape_string(user),
            "password": escape_string(passwd)
        }
        component.node.outputs = {
            "response": 'r'
        }
        assert (await component.execute()) == ControlFlow.NEXT
        r: requests.Response = component.process.get_variable('r')
        assert r.status_code == 200
        assert r.json()['authenticated'] is True
        assert r.json()['user'] == user


@pytest.mark.asyncio
async def test_no_verify(httpbin_secure):
    async with create_component_context(SendHttpRequestComponent) as component:
        component.node.inputs = {
            "requestUrl": escape_string(f'{httpbin_secure.url}/get'),
            "verify": False
        }
        component.node.outputs = {
            "response": 'r'
        }
        assert (await component.execute()) == ControlFlow.NEXT
        r: requests.Response = component.process.get_variable('r')
        assert r.status_code == 200


@pytest.mark.asyncio
async def test_save_to_file(httpbin):
    async with create_component_context(SendHttpRequestComponent) as component:
        with tempfile.TemporaryDirectory() as temp_dir:
            filename = "test.txt"
            component.node.inputs = {
                "requestUrl": escape_string(f'{httpbin.url}/get'),
                "requestParams": [{"name": escape_string("param1"), "value": escape_string("hello")},
                                  {"name": escape_string("param1"), "value": escape_string("你好")},
                                  {"name": escape_string("param2"), "value": escape_string("test")}],
                "saveToFile": True,
                "saveDirectory": escape_string(temp_dir),
                "fileName": escape_string(filename)
            }
            component.node.outputs = {
                "response": 'r'
            }
            assert (await component.execute()) == ControlFlow.NEXT
            r: requests.Response = component.process.get_variable('r')
            assert r.status_code == 200
            assert os.path.exists(os.path.join(temp_dir, filename))
            with open(os.path.join(temp_dir, filename), 'r', encoding='utf-8') as f:
                assert json.loads(f.read())['args'] == {'param1': ['hello', '你好'], 'param2': 'test'}


@pytest.mark.asyncio
async def test_save_to_file_when_directory_not_exists(httpbin):
    async with create_component_context(SendHttpRequestComponent) as component:
        with tempfile.TemporaryDirectory() as temp_dir:
            save_directory = os.path.join(temp_dir, "not_exists")
            filename = "test.txt"
            component.node.inputs = {
                "requestUrl": escape_string(f'{httpbin.url}/get'),
                "requestParams": [{"name": escape_string("param1"), "value": escape_string("hello")},
                                  {"name": escape_string("param1"), "value": escape_string("你好")},
                                  {"name": escape_string("param2"), "value": escape_string("test")}],
                "saveToFile": True,
                "saveDirectory": escape_string(save_directory),
                "fileName": escape_string(filename)
            }
            component.node.outputs = {
                "response": 'r'
            }
            assert (await component.execute()) == ControlFlow.NEXT
            r: requests.Response = component.process.get_variable('r')
            assert r.status_code == 200
            assert os.path.exists(os.path.join(save_directory, filename))
            with open(os.path.join(save_directory, filename), 'r', encoding='utf-8') as f:
                assert json.loads(f.read())['args'] == {'param1': ['hello', '你好'], 'param2': 'test'}


@pytest.mark.asyncio
async def test_save_to_existed_file(httpbin):
    async with create_component_context(SendHttpRequestComponent) as component:
        with tempfile.TemporaryDirectory() as temp_dir:
            filename = "test.txt"
            with open(os.path.join(temp_dir, filename), 'w', encoding='utf-8') as f:
                f.write("some data")
            component.node.inputs = {
                "requestUrl": escape_string(f'{httpbin.url}/get'),
                "saveToFile": True,
                "saveDirectory": escape_string(temp_dir),
                "fileName": escape_string(filename)
            }
            component.node.outputs = {
                "response": 'r'
            }
            with pytest.raises(FileExistsError):
                await component.execute()


@pytest.mark.asyncio
async def test_timeout(httpbin):
    async with create_component_context(SendHttpRequestComponent) as component:
        component.node.inputs = {
            "requestUrl": escape_string(f'{httpbin.url}/delay/2'),
            "timeout": "1",
        }
        component.node.outputs = {
            "response": 'r'
        }
        with pytest.raises(ReadTimeout):
            await component.execute()


@pytest.mark.asyncio
async def test_session_cookies(httpbin):
    async with create_component_context(SendHttpRequestComponent) as component:
        component.node.inputs = {
            "requestUrl": escape_string(f'{httpbin.url}/cookies/set?k1=v1&k2=v2'),
        }
        component.node.outputs = {
            "response": 'r'
        }
        assert (await component.execute()) == ControlFlow.NEXT
        r: requests.Response = component.process.get_variable('r')
        assert r.status_code == 200
        assert r.session_cookies == {'k1': 'v1', 'k2': 'v2'}
