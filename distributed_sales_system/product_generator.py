from typing import List, Tuple, Union, Dict
from sched import scheduler
import time
from distributed_sales_system.warehouse import Warehouse
from distributed_sales_system import logging

class GeneratorProduct:
    '''
    Class representing product inside generator

    ...

    Attributes
    ----------
    create_time (int):
            Time that it takes to create product.
    create_amount (int):
            How much product is created in one period.
    '''

    def __init__(self, create_time: int, create_amount: int) -> None:
        self.create_time = create_time
        self.create_amount = create_amount

    def __repr__(self) -> str:
        return f"[create_time: {self.create_time}, create_amount: {self.create_amount}]"


class Generator():
    '''
    A class representing product generator.

    ...

    Attributes
    ----------
    products (dict):
            Dictionary mapping product name to its create time and create amount.
    default_create_time (int):
            Default create time of given product (used if create time not passed in constructor).
    default_create_amount (int):
            Default create amount of given product (used if limit not passed in constructor).
    '''
    default_create_time = 5
    default_create_amount = 1

    def __init__(self, products_list: Union[List[str], Dict[str, Dict[str, Union[float, int]]]]) -> None:
        self.scheduler = scheduler(time.monotonic, time.sleep)  # start scheduler
        self.products = {}
        if isinstance(products_list, List):
            for name in products_list:
                self.products[name] = GeneratorProduct(Generator.default_create_time, Generator.default_create_amount)
        else:
            for name, params in products_list.items():
                product_init_list = [Generator.default_create_time, Generator.default_create_amount]
                if 'create_time' in params.keys():
                    if not isinstance(params['create_time'], int):
                        raise ValueError("Generator: Product creation time has to be integer!")
                    if params['create_time'] < 0:
                        raise ValueError("Generator: Product creation time cannot be less than zero!")
                    if params['create_time'] > 1000:
                        raise ValueError("Generator: Product creation time cannot be more than 1000!")
                    product_init_list[0] = params['create_time']
                if 'create_amount' in params.keys():
                    if not isinstance(params['create_amount'], int):
                        raise ValueError("Generator: Product create amount has to be integer!")
                    if params['create_amount'] < 0:
                        raise ValueError("Generator: Cannot produce less than zero!")
                    if params['create_amount'] > 50:
                        raise ValueError("Generator: Cannot produce more at a time than 50!")
                    product_init_list[1] = params['create_amount']
                
                self.products[name] = GeneratorProduct(product_init_list[0], product_init_list[1])


    def __repr__(self) -> str:
        return f"{self.products}"
    

    def prepare_generator(self, warehouse: Warehouse) -> None:
        '''
        Method that schedules every product incrementation. 
        Used within daemon thread so no need to reschedule on 'enter'.

            Parameters:
                    warehouse (Warehouse): warehouse instance from producer, 
                    as we need to schedule warehouse increase amount method.
            Returns:
                    None
        '''
        if not isinstance(warehouse, Warehouse):
            raise ValueError("Generator: Cannot schedule generation without access to proper warehouse!")
        for name, product in self.products.items():
            self.scheduler.enter(product.create_time, 1, self.__increase_amount_wrapper, argument=(warehouse, name, product.create_amount, product.create_time))

    
    def __increase_amount_wrapper(self, warehouse, name, create_amount, create_time, stop=False):
        if not stop:
            self.scheduler.enter(create_time, 1, self.__increase_amount_wrapper, argument=(warehouse, name, create_amount, create_time,))
            warehouse.increase_amount(name, create_amount)
            logging.debug(f"warehouse: {warehouse}")


    def add_product(self, product_name: str, warehouse: Warehouse, create_time: int = default_create_time, create_amount: int = default_create_amount) -> None:
        '''
        Method for adding new products to generator. Only to be used as part of Producer.add_product method
        (otherwise errors are likely to happen).

            Parameters:
                    product_name (str): Name of the product to be added.
                    create_time (int): Time it takes to create given product.
                    create_amount (int): How much given product is created in one period.
            Returns:
                    None
        '''
        if product_name in self.products:
            raise ValueError("Generator: Product is already generated!")
        else:
            self.products[product_name] = GeneratorProduct(create_time, create_amount)
            self.scheduler.enter(create_time, 1, self.__increase_amount_wrapper, argument=(warehouse, product_name, create_amount, create_time))

    def delete_product(self, product_name: str) -> None:
        '''
        Method for removing product from generator. Only to be used as part of Producer.delete_product method
        (otherwise errors are likely to happen).

            Parameters:
                    product_name (str): Name of the product to be deleted.

            Returns:
                    None
        '''
        if product_name in self.products:
            del self.products[product_name]
            for event in self.scheduler.queue:
                if event.argument[1] == product_name:
                    self.scheduler.cancel(event)



    def increase_create_amount(self, product_name: str, create_amount: int = 1) -> None:
        '''
        Method used for increasing created amount of given product in the generator.
        If increasing more than 50 then info error will be raised.

            Parameters:
                     product_name (str): Name of the product.
                     create_amount (int): How much created amount of product should increase.

            Returns:
                    None
        '''
        if product_name not in self.products:
            raise ValueError("Generator: Product is not generated!")
        if (self.products[product_name].create_amount + create_amount) < 50:
            self.products[product_name].create_amount += create_amount
        else:
            raise ValueError(
                "Generator: Cannot produce more at a time than 50!")

    def decrease_create_amount(self, product_name: str, create_amount: int = 1) -> None:
        '''
        Method used for decreasing created amount of given product in the generator.
        If decreasing to less than zero ValueError will raise.

            Parameters:
                     product_name (str): Name of the product.
                     create_amount (int): How much created amount of product should decrease.

            Returns:
                    None
        '''
        if product_name not in self.products:
            raise ValueError("Generator: Product is not generated!")
        if self.products[product_name].create_amount - create_amount >= 0:
            self.products[product_name].create_amount -= create_amount
        else:
            raise ValueError("Generator: Cannot produce less than zero!")

    def change_create_time(self, product_name: str, create_time: int = 5) -> None:
        '''
        Method used for changing creation time of product in generator.
        Upper and lower limit set as 0 and 1000.
        Raising or lowering beyond those will raise an error.

            Parameters:
                     product_name (str): Name of the product.
                     create_time (int): New creation time for given product.

            Returns:
                    None
        '''
        if product_name not in self.products:
            raise ValueError("Generator: Product is not generated!")
        if self.products[product_name].create_time < 0:
            raise ValueError("Generator: Product creation time cannot be less than zero")
        elif self.products[product_name].create_time > 1000:
            raise ValueError("Generator: Product creation time cannot be more than a 1000!")
        else:
            self.products[product_name].create_time = create_time