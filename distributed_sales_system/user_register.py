from collections import namedtuple
from typing import Set, List, Optional


ProducerData = namedtuple('ProducerData', ['name', 'product_list'])


class UserRegister:

    def __init__(self):
        self.__customer_register = {}
        self.__producer_register = {}
        self.__assigned_ids = set()
        self.__free_ids = set()

    def producer_with_products(self, products_list: List[str]) -> Set[int]:
        possible_producers = set()
        for product in products_list:
            for producer_id, producer_data in self.__producer_register.items():
                if product in producer_data.product_list:
                    possible_producers.add(producer_id)
        return possible_producers

    def add_customer(self, customer_name: str) -> int:
        customer_id = self.__generate_id__()
        self.__customer_register[customer_id] = customer_name
        return customer_id

    def add_producer(self, producer_name: str, producer_product_list: List[str]) -> int:
        producer_id = self.__generate_id__()
        self.__producer_register[producer_id] = ProducerData(producer_name, producer_product_list)
        return producer_id

    def add_producer_product(self, producer_id: int, product: str) -> None:
        if self.__check_producer_id(producer_id):
            current_producer_data = self.__producer_register[producer_id]
            new_product_list = current_producer_data.product_list
            new_product_list.append(product)
            self.__producer_register[producer_id] = current_producer_data._replace(product_list=new_product_list)

    def remove_producer_product(self, producer_id, product) -> None:
        if self.__check_producer_id(producer_id):
            current_producer_data = self.__producer_register[producer_id]
            new_product_list = current_producer_data.product_list
            new_product_list.remove(product)
            self.__producer_register[producer_id] = current_producer_data._replace(product_list=new_product_list)

    def delete_user(self, user_id) -> None:
        if user_id not in self.__assigned_ids:
            raise ValueError("Incorrect ID - No such ID in register")
        if user_id in self.__customer_register.keys():
            del self.__customer_register[user_id]
        if user_id in self.__producer_register.keys():
            del self.__producer_register[user_id]
        self.__delete_id(user_id)

    def __check_producer_id(self, producer_id) -> Optional[bool]:
        if producer_id in self.__producer_register.keys():
            return True
        else:
            if producer_id in self.__customer_register.keys():
                raise ValueError("Incorrect ID - ID belongs to customer")
            else:
                raise ValueError("Incorrect ID - No such ID in register")

    def __generate_id__(self) -> int:
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
        self.__free_ids.add(user_id)
        self.__assigned_ids.remove(user_id)
