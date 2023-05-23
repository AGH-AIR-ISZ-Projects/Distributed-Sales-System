from distributed_sales_system.user_register import UserRegister
import logging
from threading import Event

global_user_register = UserRegister()
logging.basicConfig(level=logging.DEBUG, format='%(relativeCreated)8.6f %(threadName)s %(message)s')

stop_producer = Event()