from typing import List, Dict, Union, Optional, Tuple
from distributed_sales_system.warehouse import Warehouse
from distributed_sales_system import global_user_register
from distributed_sales_system.product_register import product_register
from copy import deepcopy
from random import randint

class Producer:
    
    def __init__(self, name: str, products: List[str] | List[Tuple[str, float, int, int]]) -> None:
        self.name = name
        self.products  = self.__add_products(products)
        self.warehouse = Warehouse(products)
        self.id = global_user_register.add_producer(self.name, self.products.keys())
        self.customer_register = {}


    def __del__(self) -> None:
        global_user_register.delete_user(self.id)

    
    def __add_products(self, products):
        out_dict = {}
        if isinstance(products[0], str):
            for name in products:
                if name in product_register:
                    out_dict[name] = 1
                else:
                    raise ValueError("Product not possible")
        else:
            for name, price, _, _ in products:
                if name in product_register:
                    out_dict[name] = price
                else:
                    raise ValueError("Product not possible")
        return out_dict



    def check_warehouse(self, product_name: str) -> int:
        return self.warehouse.products[product_name].amount \
            if product_name in self.warehouse.products.keys() else None
    

    def display_products(self, requested_products: List[str]) -> Dict[str, List[Union[int, float]]]:
        response_dict = {}
        for product_name in requested_products:
            if product_name in self.products.keys():
                response_dict[product_name] = [self.check_warehouse(product_name), self.products[product_name]]

        return response_dict
    

    def create_order(self, ordered_product: Dict[str,int]) -> bool:
        for name, amount in ordered_product.items():
            if self.check_warehouse(name) < amount:
                return False
        
        return True

