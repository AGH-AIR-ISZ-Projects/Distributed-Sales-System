from typing import List, Tuple
from distributed_sales_system import logging

class WarehouseProduct:

    def __init__(self, amount: int, limit: int) -> None:
        self.amount = amount
        self.limit = limit

    def __repr__(self) -> str:
        return f"[amount: {self.amount}, limit: {self.limit}]"


class Warehouse:
    
    default_amout = 5
    default_limit = 10

    def __init__(self, products_list: List[str] |  List[Tuple[str, float, int, int, int, int]]) -> None:
        # initialize empty dict
        self.products = {}
        if isinstance(products_list[0], str):
            for name in products_list:
                self.products[name] = WarehouseProduct(Warehouse.default_amout, Warehouse.default_limit)
        else:
            for name, _, amount, limit, _, _ in products_list:
                self.products[name] = WarehouseProduct(amount, limit)



    def __repr__(self) -> str:
        return f"{self.products}"
    
    
    def add_product(self, product_name: str, amount: int = default_amout, limit: int = default_limit) -> None:
        if product_name in self.products:
            raise ValueError("Product already exists in warehouse!")
        else:
            self.products[product_name] = WarehouseProduct(amount, limit)


    def delete_product(self, product_name: str) -> None:
        if product_name in self.products:
            del self.products[product_name]


    def increase_amount(self, product_name: str, amount: int = 1) -> None:
        if product_name not in self.products:
            raise ValueError("Product doesn't exists in warehouse!")
        if (self.products[product_name].amount + amount) < self.products[product_name].limit:
            self.products[product_name].amount += amount
        else:
            self.products[product_name].amount = self.products[product_name].limit
            logging.info(f"Reached limit for {product_name}")


    def decrease_amount(self, product_name: str, amount: int = 1) -> None:
        if product_name not in self.products:
            raise ValueError("Product doesn't exists in warehouse!")
        if self.products[product_name].amount - amount >= 0:
            self.products[product_name].amount -= amount
        else:
            raise ValueError("Cannot have less products than zero!")

    def change_limit(self, product_name: str, limit: int = 10) -> None:
        if product_name not in self.products:
            raise ValueError("Product doesn't exists in warehouse!")
        if self.products[product_name].limit < 0:
            raise ValueError("Limit cannot be less than zero!")
        elif self.products[product_name].limit > 1000:
            raise ValueError("Limit cannot be more than a 1000!")
        else:
            self.products[product_name].limit = limit
