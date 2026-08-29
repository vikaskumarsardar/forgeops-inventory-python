import sys
import json
import os

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

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--metrics":
        print("# HELP http_requests_total Total number of HTTP requests processed by inventory service")
        print("# TYPE http_requests_total counter")
        print('http_requests_total{service="inventory-service",status="500",method="POST"} 1')
        print('http_requests_total{service="inventory-service",status="200",method="POST"} 42')
        sys.exit(0)

    raw_input = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("SANDBOX_PAYLOAD", "{}")
    try:
        data = json.loads(raw_input)
        res = check_inventory(data)
        print(json.dumps(res))
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)
