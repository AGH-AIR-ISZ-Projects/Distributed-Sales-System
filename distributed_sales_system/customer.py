from distributed_sales_system import global_user_register
from .product_register import product_register
from typing import List
from random import sample, randint


class Customer:

    def __init__(self, name: str):
        self.name = name
        self.id = global_user_register.add_customer(customer_name=name)
        self.shopping_list = None
        self.preference_list = None

    def generate_shopping_list(self, max_number_of_products=4) -> None:
        number_of_products = randint(1, max_number_of_products)
        self.shopping_list = sample(product_register, number_of_products)

    def get_producers_from_register(self) -> None:
        possible_producers = global_user_register.producer_with_products(self.shopping_list)


    def __sort_producers(self, possible_producers: List[int]) -> List[int]:
        pass