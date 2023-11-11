import subprocess
import json
import logging
import time
import errors
from enums import StatusCode
from threading import Thread
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

class BrowserExtractor:

    def __init__(self):
        self.live_url = None

    def get_live_url(self, room_id, browser_exec, timeout=5) -> str:
        """Get the live url by making the request in a web browser which is logged in."""
        handler = self.create_handler()
        server = LiveUrlWaitServer(handler)
        try:
            server.start()
            self.browser_open(room_id, browser_exec)
            start_time = time.time()
            while True:
                if self.live_url:
                    break
                if time.time() - start_time > timeout:
                    raise TimeoutError(f'No valid request received within {timeout} seconds')
        except Exception as ex:
            raise errors.BrowserExtractor(ex)
        finally:
            if server.is_alive(): server.stop()
        return self.live_url

    def browser_open(self, room_id, browser_exec):
        """Open the room info page in the browser"""
        room_info_url = f'https://webcast.tiktok.com/webcast/room/info/?aid=1988&room_id={room_id}'
        proc = subprocess.Popen(f"{browser_exec} '{room_info_url}' 2> /dev/null", shell=True)
        while proc.poll() is None:
            time.sleep(0.1)
        logging.info('browser opened')


    def create_handler(browser_extractor):
        """Wait for the helper extension to extract and send us the live_url"""
        class ExtractorHandler(BaseHTTPRequestHandler):
            def do_POST(self):
                try:
                    content_length = int(self.headers['Content-Length'])
                    body = self.rfile.read(content_length)
                    data = json.loads(body.decode('utf-8'))
                    logging.info('Received json:')
                    logging.info(json.dumps(data, indent=4))
                    if 'live_url' in data:
                        self.send_response(StatusCode.OK)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()
                        browser_extractor.live_url = data['live_url']
                    else:
                        raise ValueError('live_url not in json')
                except Exception as ex:
                    logging.error(ex)
                    self.send_response(StatusCode.BAD_REQUEST)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(b'Invalid request')
        return ExtractorHandler

class LiveUrlWaitServer(Thread):
    def __init__(self, handler):
        super(LiveUrlWaitServer, self).__init__()
        self.server = ThreadingHTTPServer(('localhost', 8000), handler)

    def run(self):
        logging.info('Server starting')
        self.server.serve_forever()

    def stop(self):
        self.server.shutdown()
        logging.info('Server shut down')