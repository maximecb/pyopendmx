from http.server import BaseHTTPRequestHandler, HTTPServer



# TODO: can we create the handler ourself, so we can pass it a reference
# to our WebServer object?


class HTTPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()

        message = "Hello, World! Here is a GET response"
        self.wfile.write(bytes(message, "utf8"))

    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()

        message = "Hello, World! Here is a POST response"
        self.wfile.write(bytes(message, "utf8"))



class WebServer:
    def __init__(self)
        pass

    def start_server_thread(delf):
        def thread_fn():
            with HTTPServer(('', 8000), HTTPHandler) as server:
                server.serve_forever()

        thread = threading.Thread(target=thread_fn, args=(), daemon=True)
        thread.start()




