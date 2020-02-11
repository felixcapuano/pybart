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

    node_list = list()

    def __init__(self, brainamp_host='127.0.0.1', brainamp_port=51244, parent=None):
        QtCore.QObject.__init__(self, parent)

        self.sample_rate = 0

        self.brainamp_host = brainamp_host
        self.brainamp_port = brainamp_port

    def configuration(self, low_fequency, high_frequency, trig_simulate = False):
        """
        Data Acquisition Node
        """
        dev = BrainAmpSocket()
        dev.configure(brainamp_host=self.brainamp_host, brainamp_port=self.brainamp_port)
        dev.outputs['signals'].configure(protocol='tcp', interface='127.0.0.1',transfermode='plaindata',)
        dev.outputs['triggers'].configure(protocol='tcp', interface='127.0.0.1',transfermode='plaindata',)
        dev.initialize() 

        self.node_list.append(dev)

        """
        Filter Node
        """
        f1, f2 = low_fequency, high_frequency
        sample_rate = dev.outputs['signals'].spec['sample_rate']
        
        coefficients = scipy.signal.iirfilter(2, [f1/sample_rate*2, f2/sample_rate*2],
                    btype = 'bandpass', ftype = 'butter', output = 'sos')
        
        filt = SosFilter()
        filt.configure(coefficients = coefficients)
        filt.input.connect(dev.outputs['signals'])
        filt.output.configure(protocol='tcp', interface='127.0.0.1',transfermode='plaindata',)
        filt.initialize()

        self.node_list.append(filt)

        """
        Epocher Node
        """
        self.epocher = EpocherMultiLabel()
        self.epocher.configure()
        self.epocher.inputs['signals'].connect(filt.output)
        if trig_simulate:
            self.epocher.inputs['triggers'].connect(self.trigger_emulator_node())
        else:
            self.epocher.inputs['triggers'].connect(dev.outputs['triggers'])
        self.epocher.initialize()

        self.node_list.append(self.epocher)

        """
        Oscilloscope Node
        """
        self.oscilloscope_node(filt.output)

    def set_slot_new(self, slot_on_new_chunk):
        self.epocher.new_chunk.connect(slot_on_new_chunk)

    def configuration_noamp(self, slot_on_new_chunk):
        noise_out = self.noise_generator_node()

        self.oscilloscope_node(noise_out)

        trig_out = self.trigger_emulator_node()
        
        self.epocher_node(noise_out, trig_out, slot_on_new_chunk)

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

    def noise_generator_node(self, nbr_channel=1):
        """
        Noise Generator Node
        """
        ng = NoiseGenerator()
        ng.configure()
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

        return te.output
    
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

    # TODO adding dict parameter in argument
    def epocher_node(self, signal_plug, trigger_plug, slot_on_new_chunk):
        """
        Epocher Node
        """
        epocher = EpocherMultiLabel()
        epocher.configure()
        epocher.inputs['signals'].connect(signal_plug)
        epocher.inputs['triggers'].connect(trigger_plug)
        epocher.initialize()

        self.node_list.append(epocher)

        epocher.new_chunk.connect(slot_on_new_chunk)

    def start_node(self):
        for node in self.node_list:
            node.start()

    def stop_node(self):
        for node in self.node_list:
            node.stop()
            node.close()

