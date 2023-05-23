from typing import List, Tuple, Union
from distributed_sales_system import logging

class WarehouseProduct:

    '''
    Class representing product inside warehouse

    ...

    Attributes
    ----------
    amount (int):
            Amount of this product currently stored in warehouse.
    limit (int):
            Maximum number of this product that warehouse can hold.
    '''

    def __init__(self, amount: int, limit: int) -> None:
        self.amount = amount
        self.limit = limit

    def __repr__(self) -> str:
        return f"[amount: {self.amount}, limit: {self.limit}]"


class Warehouse:
    '''
    A class representing warehouse.

    ...

    Attributes
    ----------
    products (dict):
            Dictionary mapping product name to its amount and limit.
    default_amount (int):
            Default amount of given product in warehouse (used if amount not passed in constructor).
    default_limit (int):
            Default limit of given product in warehouse (used if limit not passed in constructor).
    '''
    default_amount = 5
    default_limit = 100

    def __init__(self, products_list: Union[List[str], List[Tuple[str, float, int, int, int, int]]]) -> None:
        # initialize empty dict
        self.products = {}
        if isinstance(products_list[0], str):
            for name in products_list:
                self.products[name] = WarehouseProduct(Warehouse.default_amount, Warehouse.default_limit)
        else:
            for name, _, amount, limit, _, _ in products_list:
                self.products[name] = WarehouseProduct(amount, limit)



    def __repr__(self) -> str:
        return f"{self.products}"
    
    
    def add_product(self, product_name: str, amount: int = default_amount, limit: int = default_limit) -> None:
        '''
        Method for adding new products to warehouse. Only to be used as part of Producer.add_product method
        (otherwise errors are likely to happen).

            Parameters:
                    product_name (str): Name of the product to be added.
                    amount (int): How much given product add to warehouse.
                    limit (int): Maximum amount of given product in warehouse.
            Returns:
                    None
        '''
        if product_name in self.products:
            raise ValueError("Product already exists in warehouse!")
        else:
            self.products[product_name] = WarehouseProduct(amount, limit)


    def delete_product(self, product_name: str) -> None:
        '''
        Method for removing product from warehouse. Only to be used as part of Producer.delete_product method
        (otherwise errors are likely to happen).

            Parameters:
                    product_name (str): Name of the product to be deleted.

            Returns:
                    None
        '''
        if product_name in self.products:
            del self.products[product_name]


    def increase_amount(self, product_name: str, amount: int = 1) -> None:
        '''
        Method used for increasing amount of given product in the warehouse.
        Used for generating products with Generator class.
        If increasing more than limit then info message will be raised
        and product amount will be set to limit.

            Parameters:
                     product_name (str): Name of the product.
                     amount (int): How much product amount should increase.

            Returns:
                    None
        '''
        if product_name not in self.products:
            raise ValueError("Product doesn't exists in warehouse!")
        if (self.products[product_name].amount + amount) < self.products[product_name].limit:
            self.products[product_name].amount += amount
        else:
            self.products[product_name].amount = self.products[product_name].limit
            # logging.info(f"Reached limit for {product_name}")


    def decrease_amount(self, product_name: str, amount: int = 1) -> None:
        '''
        Method used for decreasing amount of given product in the warehouse.
        Used for updating warehouse state after completing order.
        If decreasing to less than zero ValueError will raise.

            Parameters:
                     product_name (str): Name of the product.
                     amount (int): How much product amount should decrease.

            Returns:
                    None
        '''
        if product_name not in self.products:
            raise ValueError("Product doesn't exists in warehouse!")
        if self.products[product_name].amount - amount >= 0:
            self.products[product_name].amount -= amount
        else:
            raise ValueError("Cannot have less products than zero!")

    def change_limit(self, product_name: str, limit: int = 10) -> None:
        '''
        Method used for changing limit of product in warehouse.
        Upper and lower limit set as 0 and 1000.
        Raising or lowering beyond those will raise an error.

            Parameters:
                     product_name (str): Name of the product.
                     limit (int): New limit for given product.

            Returns:
                    None
        '''
        if product_name not in self.products:
            raise ValueError("Product doesn't exists in warehouse!")
        if self.products[product_name].limit < 0:
            raise ValueError("Limit cannot be less than zero!")
        elif self.products[product_name].limit > 1000:
            raise ValueError("Limit cannot be more than a 1000!")
        else:
            self.products[product_name].limit = limit
