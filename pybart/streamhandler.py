"""
ISSUE : QOscilloscope don't work, need to inherit the MainWindow
WARNING : Simulate mode ON (Marker : TEST offline)
"""

import numpy as np
import pytest
import scipy.signal
from pyacq.devices.brainampsocket import BrainAmpSocket
from pyacq.dsp.sosfilter import SosFilter
from pyacq.viewers.qoscilloscope import QOscilloscope
from pyqtgraph.Qt import QtCore

from pyacq_ext.epochermultilabel import EpocherMultiLabel
from pyacq_ext.noisegenerator import NoiseGenerator
from pyacq_ext.triggeremulator import TriggerEmulator

class StreamHandler(QtCore.QObject):

    _simulation_node = []

    def __init__(self, brainamp_host='127.0.0.1', brainamp_port=51244, parent=None):
        QtCore.QObject.__init__(self, parent)

        self.sample_rate = 0

        self.brainamp_host = brainamp_host
        self.brainamp_port = brainamp_port


    def configuration(self, low_fequency, high_frequency, trig_params, trig_simulate = False, sig_simulate = False):
        
        self.trig_simulate = trig_simulate
        self.sig_simulate = sig_simulate
        
        # Data Acquisition Node
        if not trig_simulate and not sig_simulate: ## TEST offline
            self.dev = BrainAmpSocket()
            self.dev.configure(brainamp_host=self.brainamp_host, brainamp_port=self.brainamp_port)
            self.dev.outputs['signals'].configure(protocol='tcp', interface='127.0.0.1',transfermode='plaindata',)
            self.dev.outputs['triggers'].configure(protocol='tcp', interface='127.0.0.1',transfermode='plaindata',)
            self.dev.initialize() 
        
            # Filter Node
            f1, f2 = low_fequency, high_frequency
            sample_rate = self.dev.outputs['signals'].spec['sample_rate']
            
            coefficients = scipy.signal.iirfilter(2, [f1/sample_rate*2, f2/sample_rate*2],
                        btype = 'bandpass', ftype = 'butter', output = 'sos')
            
            self.filt = SosFilter()
            self.filt.configure(coefficients = coefficients)
            self.filt.input.connect(self.dev.outputs['signals'])
            self.filt.output.configure(protocol='tcp', interface='127.0.0.1',transfermode='plaindata',)
            self.filt.initialize()
        
        # Epocher Node
        self.epocher = EpocherMultiLabel()
        self.epocher.configure(parameters=trig_params)
        if sig_simulate: ## TEST offline
            self.epocher.inputs['signals'].connect(self.noise_generator_node())
        else:
            self.epocher.inputs['signals'].connect(self.filt.output)
        if trig_simulate: ## TEST offline
            self.epocher.inputs['triggers'].connect(self.trigger_emulator_node())
        else:
            self.epocher.inputs['triggers'].connect(self.dev.outputs['triggers'])
        self.epocher.initialize()

        # # Oscilloscope Node
        # self.viewer = QOscilloscope()
        # self.viewer.configure()
        # self.viewer.input.connect(self.filt.output)
        # self.viewer.initialize()

    def start_node(self):
        if not self.trig_simulate and not self.sig_simulate: ## TEST offline
            self.dev.start()
            self.filt.start()
        self.epocher.start()

        # self.viewer.show()
        # self.viewer.start()

        for node in self._simulation_node:
            node.start()

    def stop_node(self):
        if not self.trig_simulate and not self.sig_simulate: ## TEST offline
            self.dev.stop()
            self.filt.stop()
        self.epocher.stop()
        
        # self.viewer.stop()
        
        for node in self._simulation_node:
            node.stop()
        
        # self.viewer.close()

    def set_slot_new_epochs(self, slot_on_new_chunk):
        self.epocher.new_chunk.connect(slot_on_new_chunk)

    def noise_generator_node(self, nbr_channel=1):
        """
        Noise Generator Node
        """
        ng = NoiseGenerator()
        ng.configure()
        ng.output.configure(protocol='tcp', transfermode='plaindata')
        ng.initialize()

        self._simulation_node.append(ng)

        return ng.output

    def trigger_emulator_node(self):
        """
        Triggers Laucher Node
        """
        te = TriggerEmulator()
        te.configure()
        te.outputs['triggers'].configure(protocol='tcp', transfermode='plaindata',)
        te.initialize()
        te.show()
        
        self._simulation_node.append(te)

        return te.output


