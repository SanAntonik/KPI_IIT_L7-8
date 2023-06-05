import logging
from http.server import BaseHTTPRequestHandler, HTTPServer

from prometheus_client import start_http_server, Counter
from fluent import sender

# Prometheus metrics
REQUEST_COUNTER = Counter('http_requests_total', 'Total HTTP Requests')

fluentd_tag = 'my_app.logs'
fluentd_host = '127.0.0.1'
fluentd_port = 24224
sender.setup(fluentd_tag, host=fluentd_host, port=fluentd_port)
logger = sender.FluentSender(fluentd_tag)
logger.emit('log', {'message': 'Log message'})


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            REQUEST_COUNTER.inc()  # Increment the request counter
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'''
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Greetings!</title>
                    <style>
                        body {
                            background-color: #f8f8f8;
                            font-family: Arial, sans-serif;
                            font-size: 16px;
                            color: #333;
                        }
                        h1 {
                            color: #006699;
                            font-size: 36px;
                            margin-top: 50px;
                            margin-bottom: 30px;
                        }
                        p {
                            margin-top: 20px;
                            margin-bottom: 20px;
                        }
                    </style>
                    <link rel="shortcut icon" href="#">
                    <script>
                        function logEvent() {
                            fetch('/log_event', {
                                method: 'POST',
                                body: 'Button clicked',
                            })
                            .then(response => {
                                console.log('Event logged successfully');
                            })
                            .catch(error => {
                                console.error('Error logging event:', error);
                            });
                        }
                    </script>
                </head>
                <body>
                    <h1>Why, Hello There!</h1>
                    <p>From Team-5</p>
                    <button onclick="logEvent()">Click me</button>
                </body>
                </html>
            ''')
        else:
            self.send_response(404)

    def do_POST(self):
        if self.path == '/log_event':
            REQUEST_COUNTER.inc()  # Increment the request counter
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            event_name = post_data.decode('utf-8')
            logger.emit('log', {'event_name': event_name})
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Event logged successfully\n')
        else:
            self.send_response(404)


def run_server():
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print('Server running on http://127.0.0.1:8000')
    # Start Prometheus metrics endpoint
    start_http_server(9090)
    httpd.serve_forever()


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    run_server()
