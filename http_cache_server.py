# Simple HTTP server with caching using ETag and Last-Modified

import http.server
import socketserver
import hashlib
import os
from datetime import datetime
from email.utils import formatdate, parsedate_to_datetime

PORT = 8000
FILE_PATH = "index.html"

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Only serve index.html
        if self.path == "/":
            self.path = "/" + FILE_PATH
        
        try:
            with open(FILE_PATH, 'rb') as f:
                content = f.read()

            # Create ETag using MD5 hash of content
            etag = hashlib.md5(content).hexdigest()

            # Get last modified time of the file
            last_modified = os.path.getmtime(FILE_PATH)
            last_modified_str = formatdate(last_modified, usegmt=True)

            # Check if-None-Match header from client
            if_none_match = self.headers.get("If-None-Match")
            if_modified_since = self.headers.get("If-Modified-Since")

            # Compare ETag and Last-Modified headers
            is_cached = False

            if if_none_match == etag:
                is_cached = True
            elif if_modified_since:
                client_time = parsedate_to_datetime(if_modified_since)
                file_time = datetime.utcfromtimestamp(last_modified)
                if client_time >= file_time:
                    is_cached = True

            if is_cached:
                # Send 304 Not Modified if file is unchanged
                self.send_response(304)
                self.end_headers()
                return

            # If file is modified or no caching info, send the file
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.send_header("ETag", etag)
            self.send_header("Last-Modified", last_modified_str)
            self.end_headers()
            self.wfile.write(content)

        except FileNotFoundError:
            self.send_error(404, "File Not Found")

# Create the server
with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print(f"Serving on port {PORT}")
    httpd.serve_forever()
