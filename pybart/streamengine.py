import logging
import os;
import mne
import numpy as np
import pytest
import scipy.signal
from pyqtgraph.Qt import QtCore

from pyacq.dsp.sosfilter import SosFilter
from pyacq.viewers.qoscilloscope import QOscilloscope
from pyacq_ext.brainvisionlistener import BrainVisionListener
from pyacq_ext.epochermultilabel import EpocherMultiLabel
from pyacq_ext.rawbufferdevice import RawDeviceBuffer
from pyacq_ext.eventpoller import EventPoller


#try:
    #print("creating !!!!!")
    #os.makedirs(os.environ['USERPROFILE'] + "\AppData\Local\Pybart\log\\")
#except FileExistsError:
    #pass

#logger = logging.getLogger(__name__)
#logger.setLevel(logging.INFO)

#formatter = logging.Formatter('%(asctime)s  %(levelname)s (%(name)s) -> %(message)s')

#file_handler = logging.FileHandler(os.environ['USERPROFILE'] + '\AppData\Local\Pybart\log\.log')
#file_handler.setFormatter(formatter)

#logger.addHandler(file_handler)

class StreamEngine(QtCore.QObject):
    """Proccess EEG data stream and epoch signal when a trigger is received.

    This class hold the pyacq node web, I invite you to read the pyacq
    documentation (https://github.com/pyacq/pyacq).
    
    Five nodes can be instantiated depending on the mode chosen by the user.
    
    - BrainVisionListener: Interface between BrainVision Recorder and pybart.
      Detect also trigger is there are send using parallel port.
    
    - TriggerHunter: This is the second method to detect trigger.
      It use ZMQ push/pull method (default address : tcp://127.0.0.1:5556).

    - RawDeviceBuffer: Use to simulate a stream as it was sended by
      BrainVisionListener. In input take a recorder file from BrainVision
      Recorder as format : .vhdr

    - SosFilter: Apply a passband filter on the data stream.

    - EpocherMultiLabel: Epoch the signal, return a the trigger label and
      a stack of epoch of size (time*channel*stack) depending the configuration 
      parameters.

    """

    def __init__(self, zmq_trig_enable, simulated=False, parent=None, **option):
        """Stream engine initializer
        :param zmq_trig_enable: is triggers send by zmq?
        :type zmq_trig_enable: bool
        :param simulated: is simulated mode enable , default in False
        :type simulated: bool
        
        :param raw_file: path pointing to the ".vhdr" file
        :type raw_file: str

        :param brainamp_host: address where pyacq listen data from BrainVision Recorder, default in localhost(127.0.0.1)
        :type brainamp_host: str
        :param brainamp_port: port where pyacq listen data from BrainVision Recorder, default in localhost(51244)
        :type brainamp_port: int

        """
        QtCore.QObject.__init__(self, parent)

        self.nodes = {}
        self.widget_nodes = []

        self.simulated = simulated
        self.zmq_trig_enable = zmq_trig_enable

        self.running = False
        if self.simulated:
            try:
                self.raw_file = option['raw_file']
            except KeyError:
                raise KeyError('Error: raw_file is waited in argument')
        else:
            try:
                self.brainamp_host = option['brainamp_host']
                self.brainamp_port = option['brainamp_port']
            except KeyError:
                raise KeyError('Error: raw_file is waited in argument')
    def simulated_device(self):
        """This function initialize Simulator EEG data Acquisition Node"""

        dev_sim = RawDeviceBuffer()
        try:
            dev_sim.configure(raw_file=self.raw_file, chunksize=10)
        except ValueError as e:
            raise ValueError('{}'.format(e))

        return dev_sim

    def brain_amp_device(self):
        """This function initialize EEG data Acquisition Node"""
        dev_amp = BrainVisionListener()
        dev_amp.configure(brainamp_host=self.brainamp_host,
                          brainamp_port=self.brainamp_port)

        return dev_amp

    def configuration(self, low_frequency, high_frequency, trig_params):
        """Create, configure and plug all pyacq node

        :param low_frequency: set low frequency of the pass band
        :type low_frequency: float
        :param high_frequency: set high frequency of the pass band
        :type high_frequency: float
        :param trig_params: triggers parameter on a dict format
        :type trig_params: dict

        This function initialize all node depending on the mode selected.
        It storing all node in a dictionary to start them easily.

        """

        #logger.info('Start configuration stream (simulate mode : {}), setup => low freq : {}Hz, high freq : {}Hz)'.format(self.simulated, low_frequency, high_frequency))
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

        if self.zmq_trig_enable:
            # Event Poller
            trig = EventPoller()
            trig.configure()
            trig.inputs['signals'].connect(dev.outputs['signals'])
            trig.outputs['triggers'].configure(protocol='tcp', interface='127.0.0.1',transfermode='plaindata',)
            trig.initialize()
            self.nodes['eventpoller'] = trig

        # Filter Node
        f1, f2 = low_frequency, high_frequency
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
        if self.zmq_trig_enable:
            epocher.inputs['triggers'].connect(trig.outputs['triggers'])
        else:
            epocher.inputs['triggers'].connect(dev.outputs['triggers'])
        epocher.initialize()

        self.nodes['epochermultilabel'] = epocher

        # Oscilloscope Node
        #viewer = QOscilloscope()
        #viewer.configure()
        #viewer.input.connect(filt.output)
        #viewer.initialize()


        #self.nodes['qoscilloscope'] = viewer
        #self.widget_nodes.append('qoscilloscope')

    # def changeTrigParamsAtRuntime(self, params):
    #     self.nodes['epochermultilabel'].stop()
    #     dev = self.nodes['device']
    #     trig = self.nodes['eventpoller']
    #     filt = self.nodes['sosfilter']
    #
    #     epocher = EpocherMultiLabel()
    #     epocher.configure(parameters=params)
    #     epocher.inputs['signals'].connect(filt.output)
    #     if self.zmq_trig_enable:
    #         epocher.inputs['triggers'].connect(trig.outputs['triggers'])
    #     else:
    #         epocher.inputs['triggers'].connect(dev.outputs['triggers'])
    #     epocher.initialize()
    #
    #     self.nodes['epochermultilabel'] = epocher

    def start_nodes(self):
        """Start all nodes and show them"""
        #logger.info('Start stream')
        for node in self.nodes.values():
            node.start()

        for wname in self.widget_nodes:
            widget_node = self.nodes[wname]

            # flags has to be set if not pyacq crash
            widget_node.setWindowFlags(QtCore.Qt.Window)

            # show all widget windows
            widget_node.show()

        self.running = True

    def stop_nodes(self):
        """Stop all nodes and close all widget nodes"""
        #logger.info('Stop stream')
        for node in self.nodes.values():
            if node.running():
                node.stop()

        for widget_node in self.widget_nodes:
            if not self.nodes[widget_node].closed():
                self.nodes[widget_node].close()
        
        self.running = False

    def set_slot_new_epochs(self, slot_on_new_epochs):
        """This function set the output slot for each epoch stack.
        
        :param slot_on_new_epochs: set the output slot for each stack of epochs
        :type slot_on_new_epochs: function

        The output slot has to be of format:

        >>> def on_new_epoch(label, epochs)
        >>>     # epochs processing here
        >>>     pass

        """
        self.nodes['epochermultilabel'].new_chunk.connect(slot_on_new_epochs)

    def isRunning(self):
        return running
