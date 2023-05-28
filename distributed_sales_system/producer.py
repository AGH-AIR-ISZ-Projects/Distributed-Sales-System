from typing import List, Dict, Union, Optional, Tuple
from distributed_sales_system.warehouse import Warehouse
from distributed_sales_system import global_user_register, logging, stop_producer
from distributed_sales_system.product_register import product_register
from distributed_sales_system.product_generator import Generator
from threading import Thread, Lock
from queue import Queue
import time


class Producer(Thread):
    '''
    A class to represent producer.

    ...

    Attributes
    ----------
    name (str):
            Name of the producer. Used mostly for communication with global user register
    products (dict):
            Dictionary mapping product name to its price.
    warehouse (Warehouse):
            Warehouse instance for this producer. Manages products. Producer can only have one warehouse.
    product_generator (Generator):
            Generator instance for this producer. Generates products. Producer can only have one generator.
    id (int):
            Id of the producer in global user register.
    customer_register (dict):
            Stores customer id and keeps track of total amount of cash that he spent. Used for discounts.
    defaultPrice (int):
            Class attribute, default price assigned to product in not specified
    '''

    defaultPrice = 1.0
    discountThreshold = 50.0

    def __init__(self, name: str, products: Union[List[str], Dict[str, Dict[str, Union[float, int]]]]) -> None:
        super().__init__()
        self.name = name
        self.products = self.__add_products(products)
        self.warehouse = Warehouse(products)
        self.product_generator = Generator(products)
        self.order_queue = Queue()
        self.request_queue = Queue()
        self.warehouse_lock = Lock()
        self.id = global_user_register.add_producer(
            self.name, list(self.products.keys()), self.request_queue, self.order_queue)
        self.customer_register = {}

    def __repr__(self) -> str:
        return f"{self.products}"

    def run(self) -> None:
        '''
        Method represents producer execution. It includes:
        - starting daemon thread for generation of products. It runs when request and order queues are empty.
        - handling of customers requests for offered products
        - handling of customers orders

        Producer works until global stop_producer event is set. Usually this event is set after customers threads end.
        If stop_producer event is not set then thread won't terminate!

            Returns:
                None

        '''
        generator = Thread(target=self.generate_products, name=self.name + "_generator", daemon=True)
        generator.start()
        while not stop_producer.is_set():
            if not self.order_queue.empty():
                customer_id, order, customer_reply = self.order_queue.get()
                logging.debug(f"order is {order}")
                with self.warehouse_lock:
                    order_completed = self.create_order(order)
                # send back to customer
                customer_reply.put_nowait(order_completed)
                
                if order_completed:
                    customer_name = global_user_register.check_customer_id(customer_id)
                    # sum customer spendings only up to discount threshold, after that we always give him 5% discount
                    if customer_name not in self.customer_register.keys():
                        self.customer_register[customer_name] = sum((order[name] * self.products[name] for name in order))
                    elif self.customer_register[customer_name] <= self.discountThreshold:
                        self.customer_register[customer_name] += sum((order[name] * self.products[name] for name in order))
            if not self.request_queue.empty():
                logging.debug(f"queue: {list(self.request_queue.queue)}")
                customer_id, requested_products, customer_queue = self.request_queue.get()
                customer_name = global_user_register.check_customer_id(customer_id)
                if customer_name:
                    if customer_name in self.customer_register.keys() and self.customer_register[customer_name] > self.discountThreshold:
                        with self.warehouse_lock:
                            products_info = self.display_products(requested_products, discount_multiplier=0.95)
                    else:
                        with self.warehouse_lock:
                            products_info = self.display_products(requested_products)
                            logging.debug(f"{customer_name} got discount!")
                    customer_queue.put_nowait(products_info)
                else:
                    logging.debug("Request not from customer")
                # self.generate_products()
            # logging.debug(f"{self.name} warehouse: {self.warehouse.products}")
            time.sleep(1)

        logging.debug("is done")




    def __add_products(self, products) -> Dict[str, float]:
        '''
        Inner function used for initalization of 'products' field.

            Parameters:
                    products (list | dict): List contatining names of products (str) or dicts with name, price, initial amount
                                    and limit of production. Dict may not have all parameters, in that case they're initalised
                                    with default values.

            Returns:
                    out_dict (dict): Dictionary mapping name to price (name:price).
        '''
        out_dict = {}
        if isinstance(products, List):
            for name in products:
                if name in product_register:
                    out_dict[name] = Producer.defaultPrice
                else:
                    raise ValueError("Producer: Product not possible")
        else:
            for name, params in products.items():
                if name in product_register:
                    if 'price' in params.keys():
                        if not isinstance(params['price'], (float, int)):
                            raise ValueError("Producer: Price has to be either float or int!")
                        if params['price'] < 0:
                            raise ValueError("Producer: Price has to be greater than zero!")
                        out_dict[name] = float(params['price'])
                    else:
                        out_dict[name] = Producer.defaultPrice
                else:
                    raise ValueError("Producer: Product not possible")
        return out_dict

    def add_product(self, name, price=defaultPrice, amount=Warehouse.default_amount, limit=Warehouse.default_limit,
                    create_time=Generator.default_create_time, create_amount=Generator.default_create_amount) -> None:
        '''
        Method for adding new products.

            Parameters:
                    products (list): List contatining names of products (str) or tuples with name, price, initial amount
                                    and limit of production.

            Returns:
                    out_dict (dict): Dictionary mapping name to price (name:price).
        '''
        if name in self.products:
            raise ValueError("Producer: Product already exists!")
        if name not in product_register:
            raise ValueError("Producer: Product not possible")
        self.products[name] = price
        self.warehouse.add_product(name, amount, limit)
        self.product_generator.add_product(name, create_time, create_amount)

    def delete_product(self, name) -> None:
        '''
        Method for deleting product. Takes care of deleting it from warehouse and generator as well.

            Parameters:
                    name (str): Product name to delete

            Returns:
                    None
        '''
        if name in self.products:
            del self.products[name]
            self.warehouse.delete_product(name)
            self.product_generator.delete_product(name)

    def check_warehouse(self, product_name: str) -> Union[int, None]:
        '''
        Method for getting amount of product in warehouse (if it exists):

            Parameters:
                    product_name (str): Product name to check in warehouse.

            Returns:
                    Amount of the item in warehouse if it exists or None if it doess't.
        '''
        return self.warehouse.products[product_name].amount \
            if product_name in self.warehouse.products.keys() else None

    def display_products(self, requested_products: List[str], discount_multiplier: float = 1.0) -> Dict[str, List[Union[int, float]]]:
        '''
        Method used for replying to customer's request.

            Parameters:
                    requested_products (List): List of strings representing products that customer wants to buy.
                    discount_multiplier (float): prices of all products are reduced by this multiplier. Default and max is 1.0 (no discount).
            Returns:
                    response_dict (Dict): Mapped products to their amount or None in case it's not available.
        '''
        response_dict = {}
        for product_name in requested_products:
            if product_name in self.products.keys():
                response_dict[product_name] = [self.check_warehouse(
                    product_name), self.products[product_name]*discount_multiplier]

        return response_dict

    def create_order(self, ordered_product: Dict[str, int]) -> bool:
        '''
        Method used for realizing order. Either order can be realized or not, partial orders not supported.

            Parameters:
                    ordered_products (dict): Dictionary of product names mapped to the amount that customer wants to buy

            Returns:
                    True if whole order is possible to make, False otherwise.
        '''
        for name, amount in ordered_product.items():
            product_status = self.check_warehouse(name)
            if product_status is None:
                return False
            if product_status < amount:
                return False
        
        for name, amount in ordered_product.items():
            self.warehouse.decrease_amount(name, amount)

        return True

    def generate_products(self) -> None:
        '''
        Method used for generating products in Warehouse instance using Generator instance.

            Parameters:
                    None

            Returns
                    None
        '''
        while True:
            with self.warehouse_lock:
                self.product_generator.prepare_generator(self.warehouse)
            self.product_generator.scheduler.run()
            logging.debug(f"warehouse: {self.warehouse}")

    def __del__(self) -> None:
        '''
        Destructor of the object. Also deletes it from global user register as it was assigned there during construction.

            Parameters:
                    None

            Returns:
                    None
        '''
        if hasattr(self, 'self.id'):
            global_user_register.delete_user(self.id)
