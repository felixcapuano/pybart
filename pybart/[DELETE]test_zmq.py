import time
import zmq
import sys

context = zmq.Context()
socket = context.socket(zmq.REP)
# port = socket.bind_to_random_port("tcp://127.0.0.1", min_port=49152, max_port=65536, max_tries=100)
# print("tcp://127.0.0.1:{}".format(port))
socket.bind("tcp://127.0.0.1:63490")
while True:
    
    try:
        message = socket.recv()
        print("Receivedrequest: %s" % message)
    except Exception as identifier:
        pass

    time.sleep(1)
    
