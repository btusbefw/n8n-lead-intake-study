"""Isolated, in-memory test double. NOT a production CRM or durable database."""
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

records = {}
calls = 0

class Handler(BaseHTTPRequestHandler):
    def reply(self, status, data):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        self.reply(200, {'records': records, 'calls': calls})

    def do_PUT(self):
        global calls
        try:
            value = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
            key = value['externalId']
            if self.path != '/leads/' + key:
                raise ValueError('path mismatch')
            created = key not in records
            records[key] = value
            calls += 1
            self.reply(200, {'id': key, 'created': created, 'status': 'stored'})
        except (KeyError, ValueError, TypeError):
            self.reply(400, {'error': 'invalid_request'})

    def log_message(self, *_):
        pass

HTTPServer(('0.0.0.0', 8080), Handler).serve_forever()
