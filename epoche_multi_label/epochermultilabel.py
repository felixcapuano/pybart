from pyqtgraph.Qt import QtCore
import pyqtgraph as pg
import numpy as np
from pyqtgraph.util.mutex import Mutex

from pyacq.core import Node, ThreadPollInput

import pdb

class ThreadPollInputUntilPosWaited(ThreadPollInput):
    """
    Thread waiting a futur pos in a stream.
    """

    pos_reached = QtCore.pyqtSignal(int)

    def __init__(self, input_stream,  **kargs):
        ThreadPollInput.__init__(self, input_stream, **kargs)
        
        self.locker = Mutex()
        self.pos_waited = 0

    def set_trigger(self, trigger):
        self.trigger = trigger
        self.pos_waited = trigger['pos_waited']

    def process_data(self, pos, data):
        with self.locker:
            if self.pos_waited == 0: return

            if pos >= self.pos_waited:
                self.pos_reached.emit(self)


class EpocherMultiLabel(Node,  QtCore.QObject):

    _input_specs = {'signals' : dict(streamtype = 'signals'), 
                                'triggers' : dict(streamtype = 'events',  shape = (-1, )), #dtype ='int64',
                                }
    _output_specs = {}

    _params_ex = {
            'left_sweep': -0.2,
            'right_sweep': 0.6,
            'stack_size' : 2,
        }
    _default_params = {
        'S  1' : _params_ex,
        'S  2' : _params_ex,
        'S  3' : _params_ex,
        'S  4' : _params_ex,
        'S  5' : _params_ex,
        'S  6' : _params_ex,
        'S  7' : _params_ex,
    }

    # ?
    new_chunk = QtCore.pyqtSignal(int)

    def __init__(self, parent = None, **kargs):
        QtCore.QObject.__init__(self, parent)
        Node.__init__(self, **kargs)

    def _configure(self, parameters = _default_params):
        self.parameters = parameters

    def after_input_connect(self, inputname):
        if inputname == 'signals':
            self.nb_channel = self.inputs['signals'].params['shape'][1]
            self.sample_rate = self.inputs['signals'].params['sample_rate']
        elif inputname == 'triggers':
            pass

    def _initialize(self):
        self.trig_poller = ThreadPollInput(self.inputs['triggers'], return_data=True)
        self.trig_poller.new_data.connect(self.on_new_trig)

        self.initialize_stack()


    def _start(self):
        self.trig_poller.start()

    def _stop(self):
        self.trig_poller.stop()
        self.trig_poller.wait()
        
    # TODO ValueError: not enough values to unpack (expected 2, got 1). Check logs.txt
    def on_new_trig(self, trig_num, trig_indexes):
        if trig_num != 0:
            for pos, pts, chan, classification, name in trig_indexes:
                
                trig = {}
                trig['pos'] = pos
                trig['name'] = name.decode('ascii')

                trig['pos_waited'] = trig['pos'] + self.parameters[trig['name']]['right_limit']

                thread_waiting = ThreadPollInputUntilPosWaited(self.inputs['signals'])
                thread_waiting.set_trigger(trig)
                thread_waiting.pos_reached.connect(self.on_pos_reached)
                thread_waiting.start()

                self.thread_waiting_list.append(thread_waiting)
                
    def on_pos_reached(self, thread):
        thread.stop()
        thread.wait()
        print('End thread!')
        # print("Trigger named {} over at {}.".format(trig['name'], trig['pos_waited']))

    def initialize_stack(self):
        for trigger_parameter in self.parameters.values():
            trigger_parameter['left_limit'] = int(trigger_parameter['left_sweep']*self.sample_rate)
            trigger_parameter['right_limit'] = int(trigger_parameter['right_sweep']*self.sample_rate)

            trigger_parameter['size'] = trigger_parameter['right_limit'] - trigger_parameter['left_limit']

        self.thread_waiting_list = []
