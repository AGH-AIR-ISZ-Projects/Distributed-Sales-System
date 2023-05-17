from typing import List, Dict, Union, Optional, Tuple
from distributed_sales_system.warehouse import Warehouse
from distributed_sales_system import global_user_register
from distributed_sales_system.product_register import product_register
from distributed_sales_system.product_generator import Generator
from copy import deepcopy
from random import randint

class Producer:
    
    def __init__(self, name: str, products: List[str] | List[Tuple[str, float, int, int, int, int]]) -> None:
        self.name = name
        self.products  = self.__add_products(products)
        self.warehouse = Warehouse(products)
        self.product_generator = Generator(products)
        self.id = global_user_register.add_producer(self.name, self.products.keys())
        self.customer_register = {}


    def __repr__(self) -> str:
        return f"{self.products}"

    def __del__(self) -> None:
        '''
        Destructor of the object. Also deletes it from global user register as it was assigned there during construction.

            Parameters:
                    None

            Returns:
                    None
        '''
        global_user_register.delete_user(self.id)

    
    def __add_products(self, products) -> Dict[str, float]:
        '''
        Inner function used for initalization of 'products' field.

            Parameters:
                    products (list): List contatining names of products (str) or tuples with name, price, initial amount 
                                    and limit of production.
            
            Returns:
                    out_dict (dict): Dictionary mapping name to price (name:price).
        '''
        out_dict = {}
        if isinstance(products[0], str):
            for name in products:
                if name in product_register:
                    out_dict[name] = 1
                else:
                    raise ValueError("Product not possible")
        else:
            for name, price, _, _, _, _ in products:
                if name in product_register:
                    out_dict[name] = price
                else:
                    raise ValueError("Product not possible")
        return out_dict
    
    def add_product(self, name, price, amount = Warehouse.default_amout, limit = Warehouse.default_limit, 
                     create_time = Generator.default_create_time, create_amount = Generator.default_create_amount) -> None:
        '''

        '''
        if name in self.products:
            raise ValueError("Product already exists!")
        elif name not in product_register:
            raise ValueError("Product not possible")
        self.products[name] = price
        self.warehouse.add_product(name, amount, limit)
        self.product_generator.add_product(name, create_time, create_amount)


    def delete_product(self, name) -> None:
        '''

        '''
        if name in self.products:
            del self.products[name]
            self.warehouse.delete_product(name)
            self.product_generator.delete_product(name)


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
    

    def generate_products(self):
        for product in self.products:
            self.warehouse.increase_amount(product, self.product_generator.products[product].create_amount)

