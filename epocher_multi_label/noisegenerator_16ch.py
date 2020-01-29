import numpy as np

from pyacq.core import Node
from pyqtgraph.Qt import QtCore, QtGui
from pyacq.viewers.qoscilloscope import QOscilloscope


class NoiseGenerator(Node):
    """A simple example node that generates gaussian noise.
    """
    _output_specs = {'signals': dict(streamtype='analogsignal', dtype='float32',
                                     shape=(-1, 1), compression='')}

    def __init__(self, **kargs):
        Node.__init__(self, **kargs)
        self.timer = QtCore.QTimer(singleShot=False)
        self.timer.timeout.connect(self.send_data)

    def _configure(self, chunksize=100, sample_rate=1000.):
        self.chunksize = chunksize
        self.sample_rate = sample_rate
        
        self.output.spec['shape'] = (-1, 16)
        self.output.spec['sample_rate'] = sample_rate
        self.output.spec['buffer_size'] = 1000

    def _initialize(self):
        self.head = 0
        
    def _start(self):
        self.timer.start(int(1000 * self.chunksize / self.sample_rate))

    def _stop(self):
        self.timer.stop()
    
    def _close(self):
        pass
    
    def send_data(self):
        self.head += self.chunksize
        self.output.send(np.random.normal(size=(self.chunksize, 1)).astype('float32'), index=self.head)

def test_noisegen():
    app = QtGui.QApplication([])

    ng = NoiseGenerator()
    ng.configure()
    ng.output.configure(protocol='inproc', transfermode='plaindata')
    ng.initialize()

    viewer = QOscilloscope()
    viewer.input.connect(ng.output)
    viewer.configure()
    viewer.initialize()
    viewer.show()

    ng.start()
    viewer.start()

    app.exec_()


if __name__ == '__main__':
    test_noisegen()