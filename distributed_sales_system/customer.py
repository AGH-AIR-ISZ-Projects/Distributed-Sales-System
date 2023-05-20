from distributed_sales_system import global_user_register, logging
from .product_register import product_register
from typing import List, Set, Dict, Tuple, Union
from random import sample, randint
from threading import Thread, Event
import time
from queue import Queue


class Customer(Thread):
    """
    Class representing customer.

    Attributes
    ----------
    name (str):
        Name of customer.
    id (int):
        ID of customer in global user register.
    __shopping_list (list):
        Name of products that we want ro buy. It generated automatically based on products available in product register.
    __producers_data (dict):
        Dictionary mapping producer id to offered products. Information about product contain available amount and
        price per unit.
    __preference_list (list):
        List of preference producers, by selection criterion. We prefer producers that can complete most part of order.
    __possible_producers (set):
        Stores ID of producers that have at least one product we want to buy.
    """

    def __init__(self, name: str) -> None:
        """
        Function for initialization of customer. ID is generated automatically by global register.

        Parameters:
            name (str): Name of customer.
        """
        super().__init__()
        self.name = name
        self.offer_queue = Queue()
        self.id = global_user_register.add_customer(name, self.offer_queue)
        self.__shopping_list: Dict[str, int] = {}
        self.__producers_data: Dict[int, Dict[str, List[Union[int, float]]]] = {}
        self.__preference_list: List[Tuple[int, float]] = []
        self.__possible_producers: Dict[int, List] = {}

    def run(self) -> None:
        if randint(0, 1):
            self.browsing_producers_offer()
            time.sleep(1)
            # self.submit_order()
        else:
            print(f"Customer {self.id} nothing to buy")
        print(f"Customer {self.id} is done")


    def browsing_producers_offer(self) -> None:
        """
        Function used for browsing products offers. It includes:
        - generation shopping list,
        - getting information about possible producers,
        - communication with producers,
        - preparation of preference list.

            Returns:
                None
        """
        self.__generate_shopping_list()
        self.__get_producers_from_register()
        for producer_id, producer_queues in self.__possible_producers.copy().items():
            producer_queues[0].put_nowait((self.__shopping_list, self.offer_queue))
            print(f"Customer {self.id} has sent request to {producer_id}")
            producer_data = self.offer_queue.get()
            print(f"Customer {self.id} received data from producer {producer_data}")
            print(f"Customer {self.id} queue {list(self.offer_queue.queue)}")
            self.__remove_product_with_zero_amount(producer_data)
            if producer_data:
                self.__producers_data[producer_id] = producer_data
            else:
                del self.__possible_producers[producer_id]
        self.__create_preference_list()

    def submit_order(self) -> None:
        """
        Function for order realisation. It includes:
        - preparation of order (appropriate amount),
        - communication with producer,
        - update of shopping list,
        - removing data remaining after completing order.

            Returns:
                None
        """
        while self.__shopping_list and self.__producers_data:
            current_producer_id = self.__preference_list.pop(0)[0]
            current_order = self.__prepare_order_for_producer(current_producer_id)
            is_order_completed = True  # wysłanie do producenta i informacja zwrotna czy zrealizowano zamówienie
            if is_order_completed:
                for bought_product in current_order:
                    self.__shopping_list[bought_product] -= current_order[bought_product]
                    if self.__shopping_list[bought_product] == 0:
                        del self.__shopping_list[bought_product]
            self.__possible_producers.remove(current_producer_id)
            self.__create_preference_list()
        self.__remove_shopping_data_finished_order()

    def __remove_product_with_zero_amount(self, products_info: Dict[str, List[Union[int, float]]]) -> None:
        """
        Inner function for checking if producer has a product (zero amount means product is not available
        and should be deleted).

            Parameters:
                products_info (dict): Dictionary mapping product name to two-element list with amount and price
                    (name: [amount, price])

            Returns:
                None
        """
        for product, info in products_info.items():
            if info[0] == 0:
                del products_info[product]

    def __prepare_order_for_producer(self, producer_id) -> Dict[str, int]:
        """
        Inner function for preparing order.

            Parameters:
                producer_id (int): ID of producer that we want to buy from.

            Returns:
                 order (dict): Dictionary mapping product name to amount (name:amount).
        """
        order = {}
        producer_info = self.__producers_data[producer_id]
        for available_product in producer_info:
            product_amount = producer_info[available_product][0]
            product_need = self.__shopping_list[available_product]
            order[available_product] = product_need if product_amount >= product_need else product_amount
        return order

    def __generate_shopping_list(self, max_products_in_list=4, max_product_amount=10) -> None:
        """
        Internal function for generating shopping list. Product are chosen from product register.

            Parameters:
                max_products_in_list (int): Maximum number of products in shopping list.

                max_product_amount (int): Maximum amount of every product in shopping list.

            Returns:
                 None
        """
        number_of_products = randint(1, max_products_in_list)
        products = sample(product_register, number_of_products)
        for product in products:
            amount = randint(1, max_product_amount)
            self.__shopping_list[product] = amount

    def __get_producers_from_register(self) -> None:
        """
        Internal function for contacting global user register for information about possible producers.

            Returns:
                None

        """
        self.__possible_producers = global_user_register.producer_with_products(self.__shopping_list)

    def __cost_function(self, products_data: Dict[str, List[Union[int, float]]]) -> float:
        """
        Internal function for calculating cost function (selection criterion) for producer - gives penalty for missing
        products and too little amount.

            Parameters:
                products_data (dict): Dictionary mapping product name to two-element list with amount and price
                (name: [amount, price])

            Returns:
                cost (float): Value of cost function.
        """
        products_number_coef = len(products_data)/len(self.__shopping_list)
        cost = 0
        for product in products_data:
            product_amount = products_data[product][0]
            product_need = self.__shopping_list[product]
            product_cost = products_data[product][1]
            is_order_satisfied = product_amount >= product_need
            order_amount = product_need if is_order_satisfied else product_amount
            product_amount_coef = 1 if is_order_satisfied else product_amount/product_need
            cost += product_cost*order_amount/product_amount_coef
        return cost/products_number_coef

    def __create_preference_list(self) -> None:
        """
        Internal function for creating preference list. It includes:
        - calculation of cost function per producer
        - sorting results

            Results:
                None
        """
        cost_for_producers = []
        for possible_producer in self.__possible_producers:
            cost_for_producers.append((possible_producer, self.__cost_function(self.__producers_data[possible_producer])))
        self.__preference_list = sorted(cost_for_producers, key=lambda producer_data: producer_data[1])

    def __remove_shopping_data_finished_order(self) -> None:
        """
        Internal method for removing data remaining after completing order.

            Returns:
                None
        """
        self.__shopping_list: Dict[str, int] = {}
        self.__producers_data: Dict[int, Dict[str, List]] = {}
        self.__preference_list: List[Tuple[int, float]] = []
        self.__possible_producers: List[int] = []

    def __del__(self) -> None:
        """
        Deletion of customer object. Automatically calls method form global user register.

            Returns:
                None
        """
        global_user_register.delete_user(self.id)
