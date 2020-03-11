from pyacq_ext.triggerhunter import TriggerHunter
from PyQt5 import QtGui

app = QtGui.QApplication([])

th = TriggerHunter()
th.configure()
th.outputs['triggers'].configure(protocol='tcp',
                                          interface='127.0.0.1',
                                          transfermode='plaindata',)
th.initialize()
th.start()

app.exec_()