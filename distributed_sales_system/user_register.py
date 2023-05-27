from collections import namedtuple
from typing import Dict, List, Optional
from copy import deepcopy
from queue import Queue


ProducerData = namedtuple('ProducerData', ['name', 'product_list', 'request_queue', 'order_queue'])


class UserRegister:
    """
    Class representing global user register.

    Attributes
    ----------
    __customer_register (dict):
        Dictionary mapping customer_id to its name.
    __producer_register (dict):
        Dictionary mapping producer_id to its data (namedtuple ProducerData). Producer data contains its name and
        list of products.
    __assigned_ids (set):
        Set of currently assigned IDs. Customers and producers shared IDs.
    __free_ids (set):
        Set of IDs that was freed and can be reused.
    """

    def __init__(self) -> None:
        self.__customer_register = {}
        self.__producer_register = {}
        self.__assigned_ids = set()
        self.__free_ids = set()

    def producer_with_products(self, products_list: List[str]) -> Dict[int, List[Queue]]:
        """
        Interface for customers - function used for finding producers that meet customer requirements (in terms of products).

            Parameters:
                products_list (list): List containing names of products (str) that customer want to buy.

            Returns:
                possible_producers (set): Set containing id of producers, whose have at least one product from product_list.

        """
        possible_producers = dict()
        for product in products_list:
            for producer_id, producer_data in self.__producer_register.items():
                if product in producer_data.product_list:
                    possible_producers[producer_id] = [producer_data.request_queue, producer_data.order_queue]
        return possible_producers

    def add_customer(self, customer_name: str, offer_queue: Queue) -> int:
        """
        Interface for customer - function used for assigning ID and adding new customer to register.

            Parameters:
                customer_name (str): Name of customer.
                offer_queue (Queue): Queue where producers will list their offers

            Returns:
                customer_id (int): ID assigned for new customer.

        """
        customer_id = self.__generate_id__()
        self.__customer_register[customer_id] = [customer_name, offer_queue]
        return customer_id

    def add_producer(self, producer_name: str, producer_product_list: List[str], producer_request_queue: Queue, producer_order_queue: Queue) -> int:
        """
        Interface for producer - function used for assigning ID and adding new customer to register.

            Parameters:
                producer_name (str): Name of producer.

                producer_product_list (list): List containing names (str) of products that producer is selling.

                producer_event

            Returns:
                customer_id (int): ID assigned for new producer.

        """
        producer_id = self.__generate_id__()
        self.__producer_register[producer_id] = ProducerData(producer_name, deepcopy(producer_product_list), producer_request_queue, producer_order_queue)
        return producer_id

    def add_producer_product(self, producer_id: int, product: str) -> None:
        """
        Interface for producer - function used for adding new product into offer.

            Parameters:
                producer_id (int): Producer ID.

                product (str): Product name.

            Returns:
                None

            Raises:
                ValueError - incorrect ID.
        """
        if self.__check_producer_id(producer_id):
            current_producer_data = self.__producer_register[producer_id]
            new_product_list = current_producer_data.product_list
            new_product_list.append(product)
            self.__producer_register[producer_id] = current_producer_data._replace(product_list=new_product_list)

    def remove_producer_product(self, producer_id, product) -> None:
        """
        Interface for producer - function used for removing product from offer.
            Parameters:
                producer_id (int): Producer ID.

                product (str): Product name.

            Returns:
                None

            Raises:
                ValueError - incorrect ID.
        """
        if self.__check_producer_id(producer_id):
            current_producer_data = self.__producer_register[producer_id]
            new_product_list = current_producer_data.product_list
            new_product_list.remove(product)
            self.__producer_register[producer_id] = current_producer_data._replace(product_list=new_product_list)

    def delete_user(self, user_id) -> None:
        """
        Interface for users - function used for removing user from register.

            Parameters:
                user_id (int): User ID.

            Returns:
                None

            Raises:
                ValueError - Incorrect ID.
        """
        if user_id not in self.__assigned_ids:
            raise ValueError("Incorrect ID - No such ID in register")
        if user_id in self.__customer_register.keys():
            del self.__customer_register[user_id]
        if user_id in self.__producer_register.keys():
            del self.__producer_register[user_id]
        self.__delete_id(user_id)

    def check_customer_id(self, customer_id) -> bool:
        """
        Interface for producers - function used for checking if ID belongs to customer.

            Parameters:
                customer_id (int): ID that will be checked.

            Returns:
                True if ID belongs to customer/False if not (producer ID or not in register)

        """
        if customer_id in self.__customer_register.keys():
            return True
        else:
            return False
            # raise ValueError("Incorrect ID")

    def __check_producer_id(self, producer_id) -> Optional[bool]:
        """
        Inner function used for checking if producer ID is correct (is in register and isn't assigned to customer).

            Parameters:
                producer_id (int): Producer ID.

            Returns:
                True if ID is correct.

            Raises:
                ValueError - Incorrect ID.
        """
        if producer_id in self.__producer_register.keys():
            return True
        else:
            if producer_id in self.__customer_register.keys():
                raise ValueError("Incorrect ID - ID belongs to customer")
            else:
                raise ValueError("Incorrect ID - No such ID in register")

    def __generate_id__(self) -> int:
        """
        Inner function used for generating ID for new users. It assigned the smallest possible ID.

            Returns:
                user_id (int): Generated ID.
        """
        if self.__free_ids:
            user_id = min(self.__free_ids)
            self.__free_ids.remove(user_id)
            self.__assigned_ids.add(user_id)
            return user_id
        else:
            user_id = max(self.__assigned_ids, default=-1)+1
            self.__assigned_ids.add(user_id)
            return user_id

    def __delete_id(self, user_id) -> None:
        """
        Inner function used for deleting (freeing) ID.

            Parameters:
                user_id (int): User ID.

            Returns:
                None
        """
        self.__free_ids.add(user_id)
        self.__assigned_ids.remove(user_id)
