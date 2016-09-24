#!/usr/bin/env python
import re
import webbrowser
import requests
from bs4 import BeautifulSoup
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

PORT = 4000
BASE_URL = 'https://habrahabr.ru'
LOCAL_BASE_URL = 'http://localhost:%s' % PORT

SEARCH_PATTERN = re.compile(r'(^|\W)([\w]{6})($|\W)', re.UNICODE)
REPLACE = u'\g<1>\g<2>\u2122\g<3>'


def process_html(content):
    soup = BeautifulSoup(content, 'lxml')

    # insert trademarks
    for text_node in soup.find_all(text=True):
        if text_node.parent.name not in ['[document]', 'script', 'style']:
            new_text = re.sub(SEARCH_PATTERN, REPLACE, text_node.string)
            text_node.replace_with(type(text_node)(new_text))

    # replace links
    for link in soup.find_all('a', href=True):
        link['href'] = link['href'].replace(BASE_URL, LOCAL_BASE_URL)

    return str(soup)


class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        remote_response = requests.get(BASE_URL + self.path)

        self.send_response(remote_response.status_code)
        self.send_header(
            'content-type',
            remote_response.headers['content-type']
        )
        self.end_headers()

        is_html = 'text/html' in remote_response.headers['content-type']
        self.wfile.write(
            process_html(remote_response.text)
            if is_html
            else remote_response.content
        )

if __name__ == '__main__':
    server = HTTPServer(('', PORT), HttpHandler)
    print 'Started httpserver on port %s' % PORT
    webbrowser.open(LOCAL_BASE_URL)
    server.serve_forever()
