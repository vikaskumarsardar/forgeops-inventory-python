import unittest
from app import check_inventory

class TestInventoryService(unittest.TestCase):
    def test_valid_inventory(self):
        payload = {"sku": "ITEM-100", "quantity": 2}
        result = check_inventory(payload)
        self.assertEqual(result["status"], "SUCCESS")
        self.assertEqual(result["sku"], "ITEM-100")

    def test_missing_sku_raises_key_error(self):
        payload = {"quantity": 2}
        with self.assertRaises(KeyError):
            check_inventory(payload)

if __name__ == '__main__':
    unittest.main()
