from distributed_sales_system.warehouse import Warehouse
from distributed_sales_system.customer import Customer

if __name__ == "__main__":
    # ware1 = Warehouse()
    # ware1.add_product('apple', 5)
    # print(ware1)
    # ware1.decrease_amount('apple', 2)
    # print(ware1)
    customer = Customer(name='customer')
    customer.generate_shopping_list()
    print('x')
