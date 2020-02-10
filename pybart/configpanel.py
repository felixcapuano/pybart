from PyQt5.QtWidgets import QPushButton
from pyqtgraph.Qt import QtGui

from streamhandler import StreamHandler


class ConfigPanel(QtGui.QWidget):
    def __init__(self):
        super().__init__()
        
        self.init_ui()
        self.init_streaming()
        
    def init_streaming(self):
        self.nw = StreamHandler()
        self.nw.configuration_noamp(self.on_new_chunk)
        

    def init_ui(self):
        
        self.setGeometry(300, 300, 300, 220)
        self.setWindowTitle('Config Panel')

        self.start_button = QPushButton('Start', self)
        self.start_button.move(100,70)
        self.start_button.clicked.connect(self.on_start)

        self.show()


    def on_push_start(self):
        self.nw.start_node()

    def on_new_chunk(self, label, chunk):
        print(label)
        

if __name__ == '__main__':    
    app = QtGui.QApplication([])

    config = ConfigPanel()

    app.exec_()
