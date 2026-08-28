import sys
import json
import os

def check_inventory(payload):
    # INTENTIONAL PRODUCTION BUG: Throws KeyError when 'sku' is missing!
    sku = payload["sku"]
    quantity = payload.get("quantity", 1)

    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero")

    return {
        "status": "SUCCESS",
        "sku": sku.upper(),
        "available": True,
        "stock_count": 42
    }

if __name__ == "__main__":
    raw_input = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("SANDBOX_PAYLOAD", "{}")
    try:
        data = json.loads(raw_input)
        res = check_inventory(data)
        print(json.dumps(res))
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)
