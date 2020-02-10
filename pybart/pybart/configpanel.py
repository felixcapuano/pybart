<<<<<<< HEAD
from pyqtgraph.Qt import QtGui


class ConfigPanel(QtGui.QWidget):
    def __init__(self):
        super().__init__()
        
        self.initUI()
        
        
    def initUI(self):
        
        self.setGeometry(300, 300, 300, 220)
        self.setWindowTitle('Icon')
        self.show()

if __name__ == '__main__':    
    app = QtGui.QApplication([])

    config = ConfigPanel()

    app.exec_()

=======
from nodeweb import NodeWeb
from pyqtgraph.Qt import QtGui

def on_new_chunk(label, chunk):
    print(chunk)

if __name__ == '__main__':

    app = QtGui.QApplication([])

    ex = NodeWeb()
    ex.configuration_noamp(on_new_chunk)
    
    app.exec_()    
>>>>>>> c9d6e69bfa738a65137cf21e53ae20c8933626ea
