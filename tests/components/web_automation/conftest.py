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

# 创建一个简单的 HTTP 服务器
import os
import threading
import time
from http import HTTPStatus
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

import pytest


class CustomHTTPRequestHandler(SimpleHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.dirname(os.path.abspath(__file__)), **kwargs)

    def do_GET(self):
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        f = self.send_head()
        if f:
            try:
                self.wfile.flush()
                if 'delay' in query_params:
                    time.sleep(float(query_params['delay'][0]))
                self.copyfile(f, self.wfile)
            finally:
                f.close()

    def do_POST(self):
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        expected = query_params['expected'][0]
        content_length = int(self.headers['Content-Length'])
        matched = False
        while content_length > 0:
            line = self.rfile.readline()
            content_length -= len(line)
            if expected in line.decode():
                matched = True
        if matched:
            self.send_response(HTTPStatus.FOUND)
            self.send_header("Location", 'index.html')
            self.send_header("Content-Length", "0")
            self.end_headers()
        else:
            self.send_error(HTTPStatus.BAD_REQUEST, 'NOT MATCHED')


class ThreadedHTTPServer:
    def __init__(self):
        self.server = HTTPServer(('localhost', 0), CustomHTTPRequestHandler)
        self.thread = threading.Thread(target=self.server.serve_forever)

    def start(self):
        self.thread.start()
        time.sleep(1)  # 等待服务器启动

    def stop(self):
        self.server.shutdown()
        self.thread.join()


@pytest.fixture(scope='package')
def http_server():
    server = ThreadedHTTPServer()
    server.start()
    yield f'http://localhost:{server.server.server_port}'
    server.stop()
