from nodeweb import NodeWeb
from pyqtgraph.Qt import QtGui

def on_new_chunk(label, chunk):
    print(chunk)

if __name__ == '__main__':

    app = QtGui.QApplication([])

    ex = NodeWeb()
    ex.configuration_noamp(on_new_chunk)
    
    app.exec_()    
