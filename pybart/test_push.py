import zmq
import time

addr = "tcp://127.0.0.1:5556"



try:
    ctx = zmq.Context()
    sock = ctx.socket(zmq.PUSH)
    sock.bind(addr)
except zmq.ZMQError as e:
        print(e)

while True:
    try:
        sock.send(b'salut')
        print("send")
    except zmq.ZMQError as e:
        print(e)
    time.sleep(1)