from typing import List, Tuple

class WarehouseProduct:

    def __init__(self, amount: int, limit: int) -> None:
        self.amount = amount
        self.limit = limit

    def __repr__(self) -> str:
        return f"[amount: {self.amount}, limit: {self.limit}]"


class Warehouse:

    def __init__(self, products_list: List[str] |  List[Tuple[str, float, int, int]]) -> None:
        # initialize empty dict
        self.products = {}
        if isinstance(products_list[0], str):
            for name in products_list:
                    self.products[name] = WarehouseProduct(5, 10)
        else:
            for name, _, amount, limit in products_list:
                    self.products[name] = WarehouseProduct(amount, limit)



    def __repr__(self) -> str:
        return f"{self.products}"


    def delete_product(self, product_name: str) -> None:
        if product_name in self.products:
            del self.products[product_name]

    def increase_amount(self, product_name: str, amount: int = 1) -> None:
        if product_name not in self.products:
            raise AttributeError("Product doesn't exists in warehouse!")
        if (self.products[product_name].amount + amount) < self.products[product_name].limit:
            self.products[product_name].amount += amount
        else:
            raise AttributeError(
                f"Cannot have more products than specified limit of {self.products[product_name].limit}!")

    def decrease_amount(self, product_name: str, amount: int = 1) -> None:
        if product_name not in self.products:
            raise AttributeError("Product doesn't exists in warehouse!")
        if self.products[product_name].amount - amount >= 0:
            self.products[product_name].amount -= amount
        else:
            raise AttributeError("Cannot have less products than zero!")
