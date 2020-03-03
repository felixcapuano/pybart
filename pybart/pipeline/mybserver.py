import zmq

class MybZmqServer:

    def __init__(self, min_port=49152, max_port=65536, max_tries=100):
        self.ctx = zmq.Context()
        self.myb_socket = self.ctx.socket(zmq.REP)
        self.port = self.myb_socket.bind_to_random_port("tcp://127.0.0.1", min_port=min_port, max_port=max_port, max_tries=max_tries)


    def get_port(self):
        return self.port

    def send_likelihood(self):
        pass