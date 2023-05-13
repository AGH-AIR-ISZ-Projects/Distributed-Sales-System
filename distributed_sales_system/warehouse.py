import json
from distributed_sales_system import json_path


class Product:

    def __init__(self, name: str, amount: int, limit: int) -> None:
        self.__name = name
        self.amount = amount
        self.limit = limit

    def __repr__(self) -> str:
        return f"[name: {self.__name}, amount: {self.amount}, limit: {self.limit}]"


class Warehouse:

    def __init__(self) -> None:
        # initialize empty dict
        self.__products = {}

    def __repr__(self) -> str:
        return f"{self.__products}"

    def add_product(self, product_name: str, amount: int = 0, limit: int = 10) -> None:
        with open(json_path) as f:
            json_content = json.load(f)
            if product_name not in json_content:
                raise AttributeError(
                    "Product doesn't exists (not specified in product register)")
            elif product_name in self.__products.keys():
                raise AttributeError("Product already exists in warehouse!")
            elif amount < 0:
                raise ValueError("Amount cannot be less than zero!")
            else:
                self.__products[product_name] = Product(
                    product_name, amount, limit)

    def delete_product(self, product_name: str) -> None:
        if product_name in self.__products:
            del self.__products[product_name]

    def increase_amount(self, product_name: str, amount: int = 1) -> None:
        if product_name not in self.__products:
            raise AttributeError("Product doesn't exists in warehouse!")
        if (self.__products[product_name].amount + amount) < self.__products[product_name].limit:
            self.__products[product_name].amount += amount
        else:
            raise AttributeError(
                f"Cannot have more products than specified limit of {self.__products[product_name].limit}!")

    def decrease_amount(self, product_name: str, amount: int = 1) -> None:
        if product_name not in self.__products:
            raise AttributeError("Product doesn't exists in warehouse!")
        if self.__products[product_name].amount - amount >= 0:
            self.__products[product_name].amount -= amount
        else:
            raise AttributeError("Cannot have less products than zero!")
