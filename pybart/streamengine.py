import logging

import mne
import numpy as np
import pytest
import scipy.signal
from pyqtgraph.Qt import QtCore

from pyacq.dsp.sosfilter import SosFilter
from pyacq.viewers.qoscilloscope import QOscilloscope
from pyacq_ext.brainampsocket import BrainAmpSocket
from pyacq_ext.epochermultilabel import EpocherMultiLabel
from pyacq_ext.rawbufferdevice import RawDeviceBuffer

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s  %(levelname)s (%(name)s) -> %(message)s')

file_handler = logging.FileHandler('log\\.log')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

class StreamEngine(QtCore.QObject):
    """This object emit epoch in real time from a EEG device using BrainVision Recorder."""

    nodes = {}
    widget_nodes = []

    def __init__(self, brainamp_host, brainamp_port, simulated=False, parent=None, **option):
        """Stream handler builder

        :param brainamp_host: address where pyacq listen data from BrainVision Recorder, default in localhost(127.0.0.1)
        :param brainamp_port: port where pyacq listen data from BrainVision Recorder, default in localhost(51244)

        """
        QtCore.QObject.__init__(self, parent)

        self.brainamp_host = brainamp_host
        self.brainamp_port = brainamp_port

        self.simulated = simulated
        if self.simulated:
            try:
                self.raw_file = option['raw_file']
            except KeyError:
                raise KeyError('Error: raw_file is waited in argument')

    def simulated_device(self):
        # Simulator EEG data Acquisition Node

        dev_sim = RawDeviceBuffer()
        try:
            dev_sim.configure(raw_file=self.raw_file, chunksize=10)
        except ValueError as e:
            raise ValueError('{}'.format(e))

        return dev_sim

    def brain_amp_device(self):
        # EEG data Acquisition Node
        dev_amp = BrainAmpSocket()
        dev_amp.configure(brainamp_host=self.brainamp_host,
                          brainamp_port=self.brainamp_port)

        return dev_amp

    def configuration(self, low_fequency, high_frequency, trig_params):
        """Create, configure and plug all pyacq node

        :low_fequency: set low frequency of the pass band
        :high_frequency: set high frequency of the pass band
        :trig_params: triggers parameter on a dict format

        """

        logger.info('Start configuration stream (simulate mode : {}), setup => low freq : {}Hz, high freq : {}Hz)'.format(self.simulated, low_fequency, high_frequency))
        if self.simulated:
            dev = self.simulated_device()
        else:
            dev = self.brain_amp_device()

        dev.outputs['triggers'].configure(protocol='tcp',
                                          interface='127.0.0.1',
                                          transfermode='plaindata',)
        dev.outputs['signals'].configure(protocol='tcp',
                                         interface='127.0.0.1',
                                         transfermode='plaindata',)
        dev.initialize()
        self.nodes['device'] = dev

        # Filter Node
        f1, f2 = low_fequency, high_frequency
        sample_rate = dev.outputs['signals'].spec['sample_rate']

        coefficients = scipy.signal.iirfilter(2, [f1/sample_rate*2, f2/sample_rate*2],
                                              btype='bandpass', ftype='butter', output='sos')

        filt = SosFilter()
        filt.configure(coefficients=coefficients)
        filt.input.connect(dev.outputs['signals'])
        filt.output.configure(
            protocol='tcp', interface='127.0.0.1', transfermode='plaindata',)
        filt.initialize()

        self.nodes['sosfilter'] = filt

        # Epocher Node
        epocher = EpocherMultiLabel()
        epocher.configure(parameters=trig_params)
        epocher.inputs['signals'].connect(filt.output)
        epocher.inputs['triggers'].connect(dev.outputs['triggers'])
        epocher.initialize()

        self.nodes['epochermultilabel'] = epocher

        # Oscilloscope Node
        viewer = QOscilloscope()
        viewer.configure()
        viewer.input.connect(filt.output)
        viewer.initialize()

        self.nodes['qoscilloscope'] = viewer
        self.widget_nodes.append('qoscilloscope')

    def start_node(self):
        """Start all nodes"""
        logger.info('Start stream')
        for node in self.nodes.values():
            node.start()

        for wname in self.widget_nodes:
            widget_node = self.nodes[wname]

            # flags has to be set if not pyacq crash
            widget_node.setWindowFlags(QtCore.Qt.Window)

            # show all widget windows
            widget_node.show()

    def stop_node(self):
        """Stop all nodes and close all widget nodes"""
        logger.info('Stop stream')
        for node in self.nodes.values():
            if node.running():
                node.stop()

        for widget_node in self.widget_nodes:
            if not self.nodes[widget_node].closed():
                self.nodes[widget_node].close()

    def set_slot_new_epochs(self, slot_on_new_chunk):
        """This function set the output slot for each epoch stack """

        self.nodes['epochermultilabel'].new_chunk.connect(slot_on_new_chunk)
