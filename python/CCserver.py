import imp
import json
from http.server import HTTPServer, BaseHTTPRequestHandler, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

import econ
import catch_data

HOST = 'localhost'
PORT = 8080

class ChineseChivesHTTP( BaseHTTPRequestHandler ):

    def end_headers(self) -> None:
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', '*')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        return super().end_headers()

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
                # /trade?term=short&symbol=BTC/USDT&init_cash=10000
                data = catch_data.trade( *params['term'], *params['symbol'], int(*params['init_cash']) )

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

    server.server_close()
    print("Server closed")


if __name__ == "__main__":
    run_server( HOST, PORT )
