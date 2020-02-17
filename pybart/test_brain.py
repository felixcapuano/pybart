# -*- coding: utf-8 -*-
# Copyright (c) 2016, French National Center for Scientific Research (CNRS)
# Distributed under the (new) BSD License. See LICENSE for more info.

import time

import pytest
from pyqtgraph.Qt import QtCore, QtGui
from streamhandler import StreamHandler

from pyacq import create_manager
from pyacq.viewers import QOscilloscope
from pyacq_ext.brainampsocket import BrainAmpSocket


@pytest.mark.skipif(True, reason='Need brainamp device to test')
def test_brainampsocket():
    # in main App
    app = QtGui.QApplication([])
    
    # dev = BrainAmpSocket()
    # #~ dev.configure(brainamp_host = '194.167.217.129', brainamp_port = 51244)
    # dev.configure(brainamp_host='127.0.0.1', brainamp_port=51244)
    # dev.outputs['signals'].configure(protocol='tcp', interface='127.0.0.1',transfermode='plaindata',)
    # dev.outputs['triggers'].configure(protocol='tcp', interface='127.0.0.1',transfermode='plaindata',)
    # dev.initialize()
    
    # viewer = QOscilloscope()
    # viewer.configure()
    # viewer.input.connect(dev.outputs['signals'])
    # viewer.initialize()
    # viewer.show()
    
    # dev.start()
    # viewer.start()
    
    # def terminate():
    #     viewer.stop()
    #     dev.stop()
    #     viewer.close()
    #     dev.close()
    #     app.quit()
    
    # # start for a while
    # timer = QtCore.QTimer(singleShot=True, interval=5000)
    # timer.timeout.connect(terminate)
    # #~ timer.start()

    sh = StreamHandler()
    params = {
        "S  1":
        { 
            "right_sweep": 0.2,
            "left_sweep": 0.1,
            "max_stock": 1
        }
    }
    sh.configuration(1., 20., params)
    sh.start_node()
    
    app.exec_()

if __name__ == '__main__':
    test_brainampsocket()
