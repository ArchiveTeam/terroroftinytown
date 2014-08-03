import socketserver
import threading

from terroroftinytown.six.moves.BaseHTTPServer import (HTTPServer,
    BaseHTTPRequestHandler)


class ExampleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        shortcode = self.path.split('/', 1)[-1]

        if shortcode:
            self.send_response(301)
            self.send_header('Location', 'http://www.archiveteam.org/')
            self.end_headers()
        elif self.path == '/':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'Example Server')
        else:
            self.send_response(404)
            self.end_headers()


class ExampleServer(socketserver.ThreadingMixIn, HTTPServer):
    def __init__(self, address):
        HTTPServer.__init__(self, address, ExampleHandler)


class ExampleServerThread(threading.Thread):
    def __init__(self, port=0):
        threading.Thread.__init__(self)
        self.daemon = True
        self._port = port
        self._server = ExampleServer(('localhost', self._port))
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
    server = ExampleServerThread(8060)
    server.start()
    server.join()
