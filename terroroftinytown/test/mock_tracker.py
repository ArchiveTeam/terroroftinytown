import socketserver
import threading

from terroroftinytown.six.moves.BaseHTTPServer import (HTTPServer,
    BaseHTTPRequestHandler)


class TrackerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pass


class MockTracker(socketserver.ThreadingMixIn, HTTPServer):
    def __init__(self, address):
        HTTPServer.__init__(self, address, TrackerHandler)


class MockTrackerThread(threading.Thread):
    def __init__(self, port=0):
        threading.Thread.__init__(self)
        self.daemon = True
        self._port = port
        self._server = MockTracker(('localhost', self._port))
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
