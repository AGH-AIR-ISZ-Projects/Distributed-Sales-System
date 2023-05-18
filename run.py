from distributed_sales_system.warehouse import Warehouse
from distributed_sales_system.customer import Customer
from distributed_sales_system import global_user_register

if __name__ == "__main__":
    # ware1 = Warehouse()
    # ware1.add_product('apple', 5)
    # print(ware1)
    # ware1.decrease_amount('apple', 2)
    # print(ware1)
    global_user_register.add_producer('p1', ["apple", "pear", "banana"])
    global_user_register.add_producer('p2', ["apple", "banana", "orange"])
    global_user_register.add_producer('p3', ["apple", "watermelon", "x"])
    customer1 = Customer(name='customer1')
    customer1.browsing_producers_offer()




