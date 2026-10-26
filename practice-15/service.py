from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
ThreadingHTTPServer(('0.0.0.0',8000),SimpleHTTPRequestHandler).serve_forever()
