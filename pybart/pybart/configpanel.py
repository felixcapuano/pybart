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

