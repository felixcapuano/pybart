import logging
import time 

from PyQt5 import QtCore, QtWidgets
import numpy as np
import zmq

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s  %(levelname)s (%(name)s) -> %(message)s')

file_handler = logging.FileHandler('log\\pipeline.log')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

class EventPoller(QtCore.QThread):
    """This class manage the communication with Myb game.

    It use a ZMQ server that send at the end of the round the likelihood value.
    """
    QUIT_ZMQ = "0"
    START_ZMQ = "1"
    EVENT_ZMQ = "2"
    RESULT_ZMQ = "4"

    def __init__(self):
        QtCore.QThread.__init__(self)

        self.ctx = zmq.Context()
        self.socket = self.ctx.socket(zmq.REP)
        self.socket.bind("tcp://127.0.0.1:5555")

        self.reset()
        self.isConnected = False
        self.mutex = QtCore.QMutex()
        self.running = True
        self.readyToSend = False
        
        # building fake gaze result
        TabXY = np.ones(self.nb_flash * 24) * 800
        self.tab_gaze = ""
        for i in range(len(TabXY)):
            self.tab_gaze += "{0:.6f}".format(TabXY[i]) + ";"

    def run(self):
        while True:
            self.mutex.lock()
            if not self.running:
                break
            self.mutex.unlock()

            try:
                msg = self.socket.recv(zmq.NOBLOCK)
                
                request, content = msg.decode().split("|")
                
                if (request == self.QUIT_ZMQ):
                    self.socket.send_string(request)
                    self.isConnected = False
                    print("quit")

                elif (request == self.START_ZMQ):
                    self.isConnected = True
                    self.socket.send_string(request)
                    print("connected")

                elif (request == self.EVENT_ZMQ and self.isConnected):
                    self.socket.send_string("ok")
                    eventTime, eventId = content.split("/")
                    print("trigger : ", eventTime, " ", eventId)

                elif (request == self.RESULT_ZMQ and self.isConnected):
                    nb_flash = (int)content
                    while (nb_flash != self.count_epoch):
                        time.sleep(0.01)
                    print("send result")
                    self.socket.send_string(self.tab_gaze[0:-1] + '|' + self.tab_lf[0:-1])

                    self.reset()
                    
            except zmq.ZMQError:
                pass

    def stop(self):
            self.mutex.lock()
            self.running = False
            self.mutex.unlock()

    def reset(self):
        self.tab_lf = ""
        self.count_epoch = 0
        self.nb_flash = 0

    def set_likelihood(self, likelihood):
        self.tab_lf += "{0:.6f}".format(float(likelihood[0])) + ";"
        self.tab_lf += "{0:.6f}".format(float(likelihood[1])) + ";"
        self.count_epoch += 1

        

#        try:
#            self.message = self.myb_socket.recv(flags=zmq.NOBLOCK)
#
#            if (int(self.message) > 0 and int(self.message) < 120):
#                self.nb_flash = int(self.message)
#                self.message = ""
#
#        except zmq.ZMQError:
#            self.message = ""
#
#        if ((self.nb_flash > 0) and (self.count_epoch == self.nb_flash)):
#
#            TabXY = np.ones(self.nb_flash * 24) * 800
#            self.tab_gaze = ""
#            for i in range(len(TabXY)):
#                self.tab_gaze = self.tab_gaze + \
#                    "{0:.6f}".format(TabXY[i]) + ";"
#
#            MSGRES = self.myb_socket.send_string(
#                self.tab_gaze[0:-1] + '|' + self.tab_lf[0:-1])

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    
    thread = EventPoller()
    thread.start()
    
    app.exec_()
