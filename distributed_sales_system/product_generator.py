from typing import List, Tuple

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


class Generator:
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
            raise ValueError("Product is already generated!")
        else:
            self.products[product_name] = GeneratorProduct(create_time, create_amount)


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
            raise ValueError("Product is not generated!")
        if (self.products[product_name].create_amount + create_amount) < 50:
            self.products[product_name].create_amount += create_amount
        else:
            raise ValueError(
                "Cannot produce more at a time than 50!")

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
            raise ValueError("Product is not generated!")
        if self.products[product_name].create_amount - create_amount >= 0:
            self.products[product_name].create_amount -= create_amount
        else:
            raise ValueError("Cannot produce less than zero!")

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
            raise ValueError("Product is not generated!")
        if self.products[product_name].create_time < 0:
            raise ValueError("Product creation time cannot be less than zero")
        elif self.products[product_name].create_time > 1000:
            raise ValueError("Product creation time cannot be more than a 1000!")
        else:
            self.products[product_name].create_time = create_time
