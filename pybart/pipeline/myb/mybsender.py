import logging

import numpy as np
import zmq

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s  %(levelname)s (%(name)s) -> %(message)s')

file_handler = logging.FileHandler('log\\pipeline.log')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

class MybLikelihoodSender:
    """This class manage the communication with Myb game.

    It use a ZMQ server that send at the end of the round the likelihood value.
    """
    def __init__(self):
        """Init the ZMQ Server to send likelihood to the game"""
        self.ctx = zmq.Context()
        self.myb_socket = self.ctx.socket(zmq.REP)
        self.myb_socket.bind("tcp://127.0.0.1:5555")

        self.reset_sender()

    def send_new_likelihood(self, likelihood):
        """Send likelihood to the Myb game
        
        - **Step 1:** For each likelihood calculate pybart add this 2 values to
          a string and try to receive the number of flash from the game.
        - **Step 2:** When the game finish the flashing round. It send multiple times
          the number of flashes it made.
        - **Step 3:** Pybart received this attempt and send him back the likelihood
          string.

        """
        self.tab_lf = self.tab_lf + \
            "{0:.6f}".format(float(likelihood[0])) + ";"
        self.tab_lf = self.tab_lf + \
            "{0:.6f}".format(float(likelihood[1])) + ";"
        self.count_epoch = self.count_epoch + 1

        try:
            self.message = self.myb_socket.recv(flags=zmq.NOBLOCK)

            if (int(self.message) > 0 and int(self.message) < 120):
                self.nb_flash = int(self.message)
                self.message = ""

        except zmq.ZMQError:
            self.message = ""

        if ((self.nb_flash > 0) and (self.count_epoch == self.nb_flash)):

            TabXY = np.ones(self.nb_flash * 24) * 800
            self.tab_gaze = ""
            for i in range(len(TabXY)):
                self.tab_gaze = self.tab_gaze + \
                    "{0:.6f}".format(TabXY[i]) + ";"

            MSGRES = self.myb_socket.send_string(
                self.tab_gaze[0:-1] + '|' + self.tab_lf[0:-1])

            self.reset_sender()

    def reset_sender(self):
        self.tab_gaze = ""
        self.tab_lf = ""
        self.count_epoch = 0
        self.nb_flash = 0

