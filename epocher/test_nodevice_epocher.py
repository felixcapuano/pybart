# -*- coding: utf-8 -*-
# Copyright (c) 2016, French National Center for Scientific Research (CNRS)
# Distributed under the (new) BSD License. See LICENSE for more info.


import pytest
from pyqtgraph.Qt import QtCore, QtGui

import pyacq


from pyacq import create_manager
from pyacq.core.node import Node
from pyacq.core.tools import ThreadPollInput
from pyacq.devices.brainampsocket import BrainAmpSocket
from pyacq.viewers.qoscilloscope import QOscilloscope

from mypyacqextended.triggeremulator import TriggerEmulator
from mypyacqextended.noisegenerator import NoiseGenerator
from mypyacqextended.epochermultilabel import EpocherMultiLabel


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
    Noise Generator Node
    """
    ng = NoiseGenerator()
    ng.configure(number_channel=16)
    ng.output.configure(protocol='tcp', transfermode='plaindata')
    ng.initialize()

    """
    Oscilloscope Node
    """
    viewer = QOscilloscope()
    viewer.configure()
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

    def on_new_chunk(name, new_chunk):
        print('Stack of {name} is full'.format(name = name))
        print(new_chunk)

    epocher.new_chunk.connect(on_new_chunk)

    epocher.start()
    viewer.start()
    te.start()
    ng.start()


    app.exec_()



if __name__ == '__main__':
    test_brainampsocket()
