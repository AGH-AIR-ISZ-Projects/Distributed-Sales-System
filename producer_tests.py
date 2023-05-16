import unittest
from distributed_sales_system.warehouse import Warehouse
from distributed_sales_system.producer import Producer
from distributed_sales_system import global_user_register

class TestProducer(unittest.TestCase):


    def test_display(self):
        name_only_ok = ["apple", "banana"]
        name_only_nok = ["apple", "banana1111"]
        all_ok = [("apple", 5.0, 10, 20), ("banana", 2.0, 3, 5)]
        all_nok = [("apple", 5.0, 10, 20), ("banana", 2.0, 3, 5)]
        prod = Producer("Stefan", all_ok)
        # print(prod.check_warehouse('apple'))
        request_dict_ok = {"apple": 5, "banana": 2}
        request_dict_nok = {"apple": 5, "banana": 12}
        # dupa = prod.display_products(["apple1", "banana1"])
        print(prod.create_order(request_dict_ok))
        print(prod.create_order(request_dict_nok))


if __name__ == '__main__':
    unittest.main()