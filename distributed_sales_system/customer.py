from distributed_sales_system import global_user_register, logging
from .product_register import product_register
from typing import List, Dict, Tuple, Union, Optional
from random import sample, randint
from threading import Thread
import time
from queue import Queue, Empty


class Customer(Thread):
    """
    Class representing customer.

    Attributes
    ----------
    name (str):
        Name of customer.
    purchases (int):
        Number of whole ordering routine before customer end shopping.
    id (int):
        ID of customer in global user register.
    __shopping_list (dict):
        Name of products mapped to amount. Represents shopping list. It can be passed as argument or be generated
        automatically based on products available in product register.
    __producers_data (dict):
        Dictionary mapping producer id to offered products. Information about product contain available amount and
        price per unit.
    __preference_list (list):
        List of preference producers, by selection criterion. We prefer producers that can complete most part of order.
    __possible_producers (dict):
        Stores ID and queues (communication) of producers that have at least one product we want to buy.
    """

    def __init__(self, name: str, purchases: int, shopping_list: Optional[Dict[str, int]] = None) -> None:
        """
        Function for initialization of customer. ID is generated automatically by global register.

        Parameters:
            name (str): Name of customer.
            purchases (int): Number of purchases that customer will make
            shopping_list (dict): Dict mapping name of product to it's number
        """
        super().__init__()
        self.name = name
        self.purchases = purchases
        self.offer_queue = Queue()
        self.order_status = Queue(maxsize=1)
        self.id = global_user_register.add_customer(name, self.offer_queue)
        self.__producers_data: Dict[int, Dict[str, List[Union[int, float]]]] = {}
        self.__preference_list: List[Tuple[int, float]] = []
        self.__possible_producers: Dict[int, List] = {}
        if shopping_list is None:
            self.__shopping_list: Dict[str, int] = {}
        else:    
            self.__shopping_list: Dict[str, int] = shopping_list

    def run(self) -> None:
        """
        Function representing customer behaviour. It includes:
        - decision to start shopping,
        - browsing producers offer,
        - submitting orders.
        Customer follow shopping routine as long as he made fix number of purchases.

            Returns:
                None

        """
        number_of_purchases = 0
        while number_of_purchases < self.purchases:
            if randint(0, 1):
                self.browsing_producers_offer()
                # time.sleep(1)
                self.submit_order()
                # time.sleep(1)
                number_of_purchases += 1
        logging.debug("is done")


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
        if not self.__shopping_list:
            self.__generate_shopping_list()
        self.__get_producers_from_register()
        logging.debug(f"wants to get {self.__shopping_list}")
        for producer_id, producer_queues in self.__possible_producers.copy().items():
            producer_queues[0].put_nowait((self.id, list(self.__shopping_list.keys()), self.offer_queue))
            # logging.debug(f"Customer {self.name} has sent request to {producer_id}")
            try:
                producer_data = self.offer_queue.get(timeout=10)
            except Empty:
                del self.__possible_producers[producer_id]
                continue
            # logging.debug(f"Customer {self.name} received data from producer {producer_data}")
            logging.debug(f"queue {producer_data}")
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
        while self.__shopping_list and self.__possible_producers:
            logging.debug(f"shopping list is {self.__shopping_list}")
            current_producer_id = self.__preference_list.pop(0)[0]
            current_order = self.__prepare_order_for_producer(current_producer_id)
            if current_order:
                self.__possible_producers[current_producer_id][1].put_nowait((self.id, current_order, self.order_status)) # wyślij zamówienie
                is_order_completed = self.order_status.get() # odbierz odpowiedź
                logging.debug(f"order is: {is_order_completed}")
                if is_order_completed:
                    for bought_product in current_order:
                        self.__shopping_list[bought_product] -= current_order[bought_product]
                        if self.__shopping_list[bought_product] == 0:
                            del self.__shopping_list[bought_product]
            del self.__possible_producers[current_producer_id]
            if not self.__shopping_list:
                break
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
        for product, info in products_info.copy().items():
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
            if available_product in self.__shopping_list.keys():
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

        products_number_coef = len(set(self.__shopping_list.keys())-(set(products_data.keys())))/len(self.__shopping_list)
        cost = 0
        for product in products_data:
            if product in self.__shopping_list.keys():
                product_amount = products_data[product][0]
                product_need = self.__shopping_list[product]
                product_cost = products_data[product][1]
                is_order_satisfied = product_amount >= product_need
                order_amount = product_need if is_order_satisfied else product_amount
                product_amount_coef = 1 if is_order_satisfied else product_amount/product_need
                cost += product_cost*order_amount/product_amount_coef
        if products_number_coef != 0:
            return cost/products_number_coef
        else:
            return cost


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
        logging.debug(f"{cost_for_producers}")
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
