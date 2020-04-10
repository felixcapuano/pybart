import time
import zmq
import sys

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://127.0.0.1:5555")

QUIT_ZMQ = "0"
START_ZMQ = "1"
EVENT_ZMQ = "2"
RESULT_ZMQ = "4"

isConnected = False
while True:
    msg = socket.recv()
    
    request, content = msg.decode().split("|")
    
    if (request == QUIT_ZMQ):
        socket.send_string(request)
        isConnected = False
        print("quit")
    elif (request == START_ZMQ):
        isConnected = True
        socket.send_string(request)
        print("connected")
    elif (request == EVENT_ZMQ and isConnected):
        socket.send_string("ok")
        eventTime, eventId = content.split("/")
        print("trigger : ", eventTime, " ", eventId)
    elif (request == RESULT_ZMQ and isConnected):
#        time.sleep(0.01)
        socket.send_string("result")
        print("asked for result")
