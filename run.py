from distributed_sales_system.customer import Customer
from distributed_sales_system.producer import Producer
from distributed_sales_system import stop_producer
from distributed_sales_system.product_register import product_register
from random import randint, sample


def BasicCommunicationTest():
    producer1 = Producer('producer_1', products=["apple", "pear", "banana"])
    customer1 = Customer('customer_1', 1, {"apple": 2})

    #flow
    customer1.start()
    producer1.start()

    customer1.join()

    stop_producer.set()

def CustomerPreferenceTest():
    producer1 = Producer('producer_1', products=["apple", "pear", "banana"])
    producer2 = Producer('producer_2', products={"apple": {'price': 0.9}})

    customer1 = Customer('customer_1', 1, {"apple": 2})
    customer2 = Customer('customer_2', 1, {"apple": 3, "pear": 2})

    producer1.start()
    producer2.start()

    # testcase #1: customer prefers lower prices
    customer1.start()
    customer1.join()

    # testcase #2: customer prefers more types of items, even if they're more expensive
    customer2.start()
    customer2.join()

    stop_producer.set()

def AcceptRefuseOrderTest():
    producer1 = Producer('producer_1', products=["apple", "pear", "banana"])

    customer1 = Customer('customer_1', 1, {"apple": 4})
    customer2 = Customer('customer_2', 1, {"apple": 4})

    producer1.start()
    customer1.start()
    customer2.start()

    customer1.join()
    customer2.join()

    stop_producer.set()

def ProducerWithZeroStock():
    producer1 = Producer('producer_1', products={"apple": {'amount': 0, 'create_amount': 0}})
    customer1 = Customer('customer_1', 1, {"apple": 4})

    producer1.start()
    customer1.start()

    customer1.join()

    stop_producer.set()

def PartialOfferTest():
    producer1 = Producer('producer_1',  products=["apple", "pear", "banana"])
    producer2 = Producer('producer_2',  products=["apple", "banana", "x"])
    customer1 = Customer('customer_1', 1, {"apple": 10, "pear":3, "x": 5})

    producer1.start()
    producer2.start()
    customer1.start()

    customer1.join()

    stop_producer.set()


def NonExistentProductOrderTest():
    producer1 = Producer('producer_1',  products=["apple", "pear", "banana"])
    customer1 = Customer('customer_1', 1, {"pjoter": 10})

    producer1.start()
    customer1.start()

    customer1.join()

    stop_producer.set()


def DiscountTest():
    producer1 = Producer('producer_1',  products={"apple": {'price': 10, 'amount': 30}, "pear": {}, "banana": {}, "orange": {}})
    customer1 = Customer('customer_1', 2, {"apple": 10})

    producer1.start()
    customer1.start()

    customer1.join()

    stop_producer.set()

def ProductGeneratorTest():
    import time
    producer1 = Producer('producer_1',  products={"apple": {'create_time': 2, 'create_amount': 10}, 
                                                  "pear": {'create_time': 4, 'create_amount': 20}, 
                                                  "banana": {'create_time': 5, 'create_amount': 30}, 
                                                  "orange": {'create_time': 10, 'create_amount': 40}})
    
    producer1.start()
    time.sleep(20)

    stop_producer.set()
    

def AddNewProductsTest():
    import time
    producer1 = Producer('producer_1',  products={"apple": {'create_time': 2, 'create_amount': 10}})

    producer1.start()
    time.sleep(10)

    with producer1.warehouse_lock:
        producer1.add_product("banana", create_time=1)

    time.sleep(10)

    with producer1.warehouse_lock:
        producer1.delete_product("apple")

    time.sleep(5)

    stop_producer.set()


def EnduranceTest():
    customers = []
    # producers = []

    for i in range(5):
        prod = Producer(f"producer_{i}", products=sample(product_register, randint(1,len(product_register))))
        prod.start()

    for i in range(15):
        cust = Customer(f"customer_{i}", 1)
        customers.append(cust)
        cust.start()

    for cust in customers:
        cust.join()
    
    stop_producer.set()

if __name__ == "__main__":
    # BasicCommunicationTest()
    # CustomerPreferenceTest()
    # AcceptRefuseOrderTest()
    # ProducerWithZeroStock()
    # PartialOfferTest()
    # NonExistentProductOrderTest()
    # DiscountTest()
    # ProductGeneratorTest()
    # AddNewProductsTest()
    EnduranceTest()