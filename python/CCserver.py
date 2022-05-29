import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

import econ

HOST = 'localhost'
PORT = 8080

class ChineseChivesHTTP( BaseHTTPRequestHandler ):

    def json_response(self, data):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

        content = json.dumps(data) # Convert to json
        self.wfile.write( bytes(content, 'utf-8') )


    def do_GET(self):
        url = urlparse(self.path)
        params = parse_qs(url.query)
        print("path:   ", url.path)
        print("params: ", params) 

        data = "Default response"

        try:
            if url.path == '/':
                data = { "command": ["klines", 'econ', 'trade'] }

            elif url.path == '/klines':
                # /klines?symbol=ETHUSDT&interval=1m&num=1000
                data = econ.klines( *params['symbol'], *params['interval'], int(*params['num']) )

            elif url.path == '/econ':
                #[TODO]: Economic indicator
                # /econ?symbol=ETHUSDT&interval=1m&num=1000
                data = econ.indicator( *params['symbol'], *params['interval'], int(*params['num']) )
                
            elif url.path == '/trade':
                #[TODO]: Grid Trade bot command
                data = "Not Implemented"

        except Exception as e:
            data = { "Invalid Format": str(e) }
            print(e)
        
        self.json_response(data)

def run_server( HOST: str, PORT: int ):
    server = HTTPServer( (HOST, PORT), ChineseChivesHTTP)
    print("Server running...")
    print("Server started http://%s:%s" % (HOST, PORT))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    
    server.serve_forever()
    server.server_close()
    print("Server closed")


if __name__ == "__main__":
    run_server( HOST, PORT )
