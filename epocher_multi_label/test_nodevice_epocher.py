# -*- coding: utf-8 -*-
# Copyright (c) 2016, French National Center for Scientific Research (CNRS)
# Distributed under the (new) BSD License. See LICENSE for more info.


import pyacq
import pytest
from pyacq import create_manager
from pyacq.core.node import Node
from pyacq.core.tools import ThreadPollInput
from pyacq.devices.brainampsocket import BrainAmpSocket
from pyacq.viewers.qoscilloscope import QOscilloscope
from pyqtgraph.Qt import QtCore, QtGui
from noisegenerator_16ch import NoiseGenerator

from epochermultilabel import EpocherMultiLabel
from triggeremulator import TriggerEmulator


class StreamMonitor(Node):
    """
    Monitors activity on an input stream and prints details about packets
    received.
    """
    _input_specs = {'signals': {}}
    
    def __init__(self, **kargs):
        Node.__init__(self, **kargs)
    
    def _configure(self):
        pass

    def _initialize(self):
        # There are many ways to poll for data from the input stream. In this
        # case, we will use a background thread to monitor the stream and emit
        # a Qt signal whenever data is available.
        self.poller = ThreadPollInput(self.input, return_data=True)
        self.poller.new_data.connect(self.data_received)
        
    def _start(self):
        self.poller.start()
        
    def data_received(self, ptr, data):
        print(data,ptr)


def test_brainampsocket():
    # in main App
    app = QtGui.QApplication([])    

    """
    Triggers Laucher Node
    """
    te = TriggerEmulator()
    te.configure()
    te.outputs['triggers'].configure(protocol='tcp',transfermode='plaindata',)
    te.initialize()
    te.show()
    
    """
    Stream Monitor Node
    """
    # dv = StreamMonitor()
    # dv.configure()
    # dv.input.connect(te.output)
    # dv.initialize()

    """
    Noise Generator Node
    """
    ng = NoiseGenerator()
    ng.configure()
    ng.output.configure(protocol='tcp', transfermode='plaindata')
    ng.initialize()

    """
    Oscilloscope Node
    """
    viewer = QOscilloscope()
    viewer.configure()
    # viewer.input.connect(filter.output)
    viewer.input.connect(ng.output)
    viewer.initialize()
    viewer.show()
    
    """
    Epocher Node
    """
    epocher = EpocherMultiLabel()
    epocher.configure()
    epocher.inputs['signals'].connect(ng.output)
    epocher.inputs['triggers'].connect(te.output)
    epocher.initialize()


    epocher.start()
    viewer.start()
    te.start()
    # dv.start()
    ng.start()


    app.exec_()

if __name__ == '__main__':
    test_brainampsocket()
