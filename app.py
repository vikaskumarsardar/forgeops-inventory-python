import sys
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

TOTAL_200_COUNT = 42
TOTAL_500_COUNT = 0

def check_inventory(payload):
    sku = payload.get("sku", "DEFAULT-SKU")
    quantity = payload.get("quantity", 1)

    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero")

    # NEW PRODUCTION BUG #3: Unhandled integer parsing on warehouse_id string!
    # Throws ValueError: invalid literal for int() when warehouse_id is "MAIN" or non-numeric!
    warehouse_str = payload.get("warehouse_id", "MAIN_ZONE_A")
    warehouse_id = int(warehouse_str)

    return {
        "status": "SUCCESS",
        "sku": sku.upper(),
        "warehouse_id": warehouse_id,
        "available": True,
        "stock_count": 42
    }

class InventoryServiceHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/metrics":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4")
            self.end_headers()
            metrics_body = (
                "# HELP http_requests_total Total number of HTTP requests processed by inventory service\n"
                "# TYPE http_requests_total counter\n"
                f'http_requests_total{{service="inventory-service",status="200",method="POST",path="/api/v1/inventory"}} {TOTAL_200_COUNT}\n'
                f'http_requests_total{{service="inventory-service",status="500",method="POST",path="/api/v1/inventory"}} {TOTAL_500_COUNT}\n'
            )
            self.wfile.write(metrics_body.encode('utf-8'))
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        global TOTAL_200_COUNT, TOTAL_500_COUNT
        if self.path == "/api/v1/inventory":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                payload = json.loads(post_data.decode('utf-8'))
                res = check_inventory(payload)
                TOTAL_200_COUNT += 1
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(res).encode('utf-8'))
            except Exception as e:
                TOTAL_500_COUNT += 1
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        else:
            self.send_error(404, "Not Found")

def run_server(port=6000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, InventoryServiceHandler)
    print(f"🚀 Inventory Python Microservice Server listening on http://localhost:{port} (Metrics on /metrics)")
    httpd.serve_forever()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--metrics":
        print("# HELP http_requests_total Total number of HTTP requests processed by inventory service")
        print("# TYPE http_requests_total counter")
        print(f'http_requests_total{{service="inventory-service",status="500",method="POST"}} {TOTAL_500_COUNT}')
        print(f'http_requests_total{{service="inventory-service",status="200",method="POST"}} {TOTAL_200_COUNT}')
        sys.exit(0)

    if len(sys.argv) > 1 and (sys.argv[1].startswith("{") or sys.argv[1] == "{}"):
        raw_input = sys.argv[1]
        try:
            data = json.loads(raw_input)
            res = check_inventory(data)
            print(json.dumps(res))
        except Exception as e:
            print(json.dumps({"error": str(e)}), file=sys.stderr)
            sys.exit(1)
        sys.exit(0)

    port = int(os.environ.get("INVENTORY_SERVICE_PORT", 6000))
    run_server(port)
