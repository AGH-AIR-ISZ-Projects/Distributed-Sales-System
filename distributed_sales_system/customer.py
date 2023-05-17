from distributed_sales_system import global_user_register
from .product_register import product_register
from typing import List, Set, Dict, Tuple
from random import sample, randint


class Customer:

    def __init__(self, name: str):
        self.name = name
        self.id = global_user_register.add_customer(customer_name=name)
        self.shopping_list: Dict[str, int] = {}
        self.producers_data: Dict[int, Dict[str, Tuple[int, float]]] = {}
        self.preference_list: List[Tuple[int, float]] = []
        self.__possible_producers: List[int] = []

    def browsing_producers_offer(self) -> None:
        self.__generate_shopping_list() # generowanie listy zakupów
        possible_producers = self.__get_producers_from_register()  # uzyskanie informacji o producentach sprzedających towary
        for producer_id in possible_producers:
            producer_data = {"apple": (20, 2.79)}  # informacje od producentów o typie ilości i cenie
            self.__remove_product_with_zero_amount(producer_data)
            self.producers_data[producer_id] = producer_data
        self.__create_preference_list(possible_producers)

    def __remove_product_with_zero_amount(self, products_info) -> None:
        for product, info in products_info:
            if info[0] == 0:
                del products_info[product]


    def submit_order(self) -> None:
        while self.shopping_list and self.producers_data:
            current_producer_id = self.preference_list.pop(0)[0]
            current_order = self.__prepare_order_for_producer(current_producer_id)
            is_order_completed = True # wysłanie do producenta i informacja zwrotna czy zrealizowano zamówienie
            if is_order_completed:
                for bought_product in current_order:
                    self.shopping_list[bought_product] -= current_order[bought_product]
                    if self.shopping_list[bought_product] == 0:
                        del self.shopping_list[bought_product]
            self.__possible_producers.remove(current_producer_id)
            self.__create_preference_list(self.__possible_producers)
        self.__remove_shopping_data_finished_order()

    def __prepare_order_for_producer(self, producer_id) -> Dict[str, int]:
        order = {}
        producer_info = self.producers_data[producer_id]
        for available_product in producer_info:
            product_amount = producer_info[available_product][0]
            product_need = self.shopping_list[available_product]
            order[available_product] = product_need if product_amount >= product_need else product_amount
        return order

    def __generate_shopping_list(self, max_products_in_list=4, max_product_amount=10) -> None:
        number_of_products = randint(1, max_products_in_list)
        products = sample(product_register, number_of_products)
        for product in products:
            amount = randint(1, max_product_amount)
            self.shopping_list[product] = amount

    def __get_producers_from_register(self) -> Set[int]:
        possible_producers = global_user_register.producer_with_products(self.shopping_list)
        return possible_producers

    def __cost_function(self, products_data) -> float:
        products_number_coef = len(products_data)/len(self.shopping_list)
        cost = 0
        for product in products_data:
            product_amount = products_data[product][0]
            product_need = self.shopping_list[product]
            product_cost = products_data[product][1]
            is_order_satisfied = product_amount >= product_need
            order_amount = product_need if is_order_satisfied else product_amount
            product_amount_coef = 1 if is_order_satisfied else product_amount/product_need
            cost += product_cost*order_amount/product_amount_coef
        return cost/products_number_coef

    def __create_preference_list(self, possible_producers) -> None:
        cost_for_producers = []
        for possible_producer in possible_producers:
            cost_for_producers.append((possible_producer, self.__cost_function(self.producers_data[possible_producer]))) # wyznaczyć funkcję kosztu dla każdego producent
        self.preference_list = sorted(cost_for_producers, key=lambda producer_data: producer_data[1]) # posortować listę względem funkcji kosztu

    def __remove_shopping_data_finished_order(self) -> None:
        self.shopping_list: Dict[str, int] = {}
        self.producers_data: Dict[int, Dict[str, List]] = {}
        self.preference_list: List[Tuple[int, float]] = []
        self.__possible_producers: List[int] = []

    def __del__(self):
        global_user_register.delete_user(self.id)
