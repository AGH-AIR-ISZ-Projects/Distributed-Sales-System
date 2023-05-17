from typing import List, Tuple

class GeneratorProduct:

    def __init__(self, create_time: int, create_amount: int) -> None:
        self.create_time = create_time
        self.create_amount = create_amount

    def __repr__(self) -> str:
        return f"[create_time: {self.create_time}, create_amount: {self.create_amount}]"


class Generator:

    default_create_time = 5
    default_create_amount = 1

    def __init__(self, products_list: List[str] |  List[Tuple[str, float, int, int, int, int]]) -> None:
        # initialize empty dict
        self.products = {}
        if isinstance(products_list[0], str):
            for name in products_list:
                self.products[name] = GeneratorProduct(Generator.default_create_time, Generator.default_create_amount)
        else:
            for name, _, _, _, create_time, create_amount  in products_list:
                self.products[name] = GeneratorProduct(create_time, create_amount)


    def __repr__(self) -> str:
        return f"{self.products}"


    def add_product(self, product_name: str, create_time: int = default_create_time, create_amount: int = default_create_amount ) -> None:
        if product_name in self.products:
            raise ValueError("Product is already generated!")
        else:
            self.products[product_name] = GeneratorProduct(create_time, create_amount)


    def delete_product(self, product_name: str) -> None:
        if product_name in self.products:
            del self.products[product_name]


    def increase_create_amount(self, product_name: str, create_amount: int = 1) -> None:
        if product_name not in self.products:
            raise ValueError("Product is not generated!")
        if (self.products[product_name].create_amount + create_amount) < 50:
            self.products[product_name].create_amount += create_amount
        else:
            raise ValueError(
                f"Cannot produce more at a time than 50!")

    def decrease_create_amount(self, product_name: str, create_amount: int = 1) -> None:
        if product_name not in self.products:
            raise ValueError("Product is not generated!")
        if self.products[product_name].create_amount - create_amount >= 0:
            self.products[product_name].create_amount -= create_amount
        else:
            raise ValueError("Cannot produce less than zero!")

    def change_create_time(self, product_name: str, create_time: int = 5) -> None:
        if product_name not in self.products:
            raise ValueError("Product is not generated!")
        if self.products[product_name].create_time < 0:
            raise ValueError("Product creation time cannot be less than zero")
        elif self.products[product_name].create_time > 1000:
            raise ValueError("Product creation time cannot be more than a 1000!")
        else:
            self.products[product_name].create_time = create_time
