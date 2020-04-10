import zmq

ctx = zmq.Context()
socket = ctx.socket(zmq.PUSH)
socket.connect("tcp://127.0.0.1:5555")

for i in range(21):
   socket.send(b'hey')
