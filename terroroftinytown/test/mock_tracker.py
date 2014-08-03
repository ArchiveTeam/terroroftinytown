import json
import socketserver
import threading

from terroroftinytown.six.moves.BaseHTTPServer import (HTTPServer,
    BaseHTTPRequestHandler)


class TrackerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'Mock Tracker')
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/api/get':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps({
                'tamper_key': '1FECB1D2DC40CF446700B875B1E738A6',
                'ip_address': None,
                'id': 7,
                'username': 'SMAUG',
                'datetime_claimed': 1407026018,
                'lower_sequence_num': 0,
                'upper_sequence_num': 20,
                'project': {
                    'url_template': 'http://chfoo-d1.mooo.com:8060/{shortcode}',
                    'request_delay': 1.0,
                    'min_version': '',
                    'custom_code_required': False,
                    'body_regex': '<a id="redir_link" href="[^"]+">',
                    'method': 'get',
                    'redirect_codes': [301, 302],
                    'alphabet':  'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
                    'no_redirect_codes': [404],
                    'name': 'test_project',
                    'banned_codes': [420],
                    'unavailable_codes': [200]
                }
            }).encode('ascii'))
        elif self.path == '/api/done':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps(
                {'status': 'OK'}
            ).encode('ascii'))
        else:
            self.send_response(404)
            self.end_headers()


class MockTracker(socketserver.ThreadingMixIn, HTTPServer):
    def __init__(self, address):
        HTTPServer.__init__(self, address, TrackerHandler)


class MockTrackerThread(threading.Thread):
    def __init__(self, port=0):
        threading.Thread.__init__(self)
        self.daemon = True
        self._port = port
        self._server = MockTracker(('0.0.0.0', self._port))
        self._port = self._server.server_address[1]
        self.started_event = threading.Event()

    def run(self):
        self.started_event.set()
        self._server.serve_forever()

    def stop(self):
        self._server.shutdown()

    @property
    def port(self):
        return self._port


if __name__ == '__main__':
    server = MockTrackerThread(8059)
    server.start()
    server.join()
