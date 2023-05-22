# from distributed_sales_system.warehouse import Warehouse
from distributed_sales_system.customer import Customer
from distributed_sales_system.producer import Producer
from distributed_sales_system import global_user_register


if __name__ == "__main__":
    # ware1 = Warehouse()
    # ware1.add_product('apple', 5)
    # print(ware1)
    # ware1.decrease_amount('apple', 2)
    # print(ware1)
    producer1 = Producer(name='producer1', products=["apple", "pear", "banana"])
    producer2 = Producer(name='producer2', products=["apple", "pear", "banana"])
    producer3 = Producer(name='producer3', products=["apple", "pear", "banana"])
    customer1 = Customer(name='customer1')
    customer2 = Customer(name='customer2')
    customer3 = Customer(name='customer3')
    customer4 = Customer(name='customer4')
    customer5 = Customer(name='customer5')
    customer6 = Customer(name='customer6')

    customer1.start()
    customer2.start()
    customer3.start()
    customer4.start()
    customer5.start()
    customer6.start()
    producer1.start()
    producer2.start()
    producer3.start()

    # for x in range(60):
    #     Customer(name=f'customer_{x}').start()

    # for x in range(17):
    #     Producer(name=f'producer_{x}', products=["apple", "pear", "banana"]).start()


