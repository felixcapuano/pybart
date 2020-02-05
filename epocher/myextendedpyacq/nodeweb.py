import numpy as np
import pytest
import scipy.signal
from pyqtgraph.Qt import QtCore, QtGui

from epochermultilabel import EpocherMultiLabel
from noisegenerator import NoiseGenerator
from triggeremulator import TriggerEmulator
from pyacq.devices.brainampsocket import BrainAmpSocket
from pyacq.dsp.sosfilter import SosFilter
from pyacq.viewers.qoscilloscope import QOscilloscope


class NodeWeb(QtCore.QObject):

    node_list = list()
    new_chunk = QtCore.pyqtSignal(str, np.ndarray)

    def __init__(self, brainamp_host = '127.0.0.1', brainamp_port = 51244, parent=None):
        QtCore.QObject.__init__(self, parent)

        self.sample_rate = 0

        self.brainamp_host = brainamp_host
        self.brainamp_port = brainamp_port

        self.configuration_amp()

    def configuration_amp(self):
        app = QtGui.QApplication([])
        
        amp_out = self.brain_amp_socket_node()

        filt_out = self.filter_node(amp_out, 1., 20.)
        
        self.oscilloscope_node(filt_out)
        
        trig_out = self.trigger_emulator_node()
        
        self.epocher_node(filt_out, trig_out)

        self.start_node()

        app.exec_() 

    def brain_amp_socket_node(self):
        """
        Data Acquisition Node
        """
        dev = BrainAmpSocket()
        dev.configure(brainamp_host=self.brainamp_host, brainamp_port=self.brainamp_port)
        dev.outputs['signals'].configure(protocol='tcp', interface='127.0.0.1',transfermode='plaindata',)
        dev.outputs['triggers'].configure(protocol='tcp', interface='127.0.0.1',transfermode='plaindata',)
        dev.initialize() 

        self.node_list.append(dev)

        return dev.outputs

    def noise_generator_node(self, nbr_channel = 1):
        """
        Noise Generator Node
        """
        ng = NoiseGenerator()
        ng.configure(number_channel=nbr_channel)
        ng.output.configure(protocol='tcp', transfermode='plaindata')
        ng.initialize()

        self.node_list.append(ng)

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
        
        self.node_list.append(te)

        return te.output # ???
    
    def filter_node(self, plug, lf, hf):
        """
        Filter Node initialisation
        """
        f1, f2 = lf, hf
        sample_rate = plug['signals'].spec['sample_rate']
        
        coefficients = scipy.signal.iirfilter(2, [f1/sample_rate*2, f2/sample_rate*2],
                    btype = 'bandpass', ftype = 'butter', output = 'sos')
        
        filt = SosFilter()
        filt.configure(coefficients = coefficients)
        filt.input.connect(plug['signals'])
        filt.output.configure(protocol='tcp', interface='127.0.0.1',transfermode='plaindata',)
        filt.initialize()

        self.node_list.append(filt)

        return filt.output

    def oscilloscope_node(self, plug):
        """
        Oscilloscope Node
        """
        viewer = QOscilloscope()
        viewer.configure()
        viewer.input.connect(plug)
        viewer.initialize()
        viewer.show()

        self.node_list.append(viewer)

    def epocher_node(self, signal_plug, trigger_plug):
        """
        Epocher Node
        """
        epocher = EpocherMultiLabel()
        epocher.configure()
        epocher.inputs['signals'].connect(signal_plug)
        epocher.inputs['triggers'].connect(trigger_plug)
        epocher.initialize()

        self.node_list.append(epocher)

        epocher.new_chunk.connect(self.on_new_chunk)

    def on_new_chunk(self, label, chunk):
        self.new_chunk.emit(label, chunk)
        print('Just got : {}'.format(label))

    def start_node(self):
        for node in self.node_list:
            node.start()

ex = NodeWeb()