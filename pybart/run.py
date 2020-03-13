from pybart.configpanel import ConfigPanel
from PyQt5 import QtWidgets
import os


if __name__ == "__main__":
    import sys

    try:
        os.mkdir("log")
    except FileExistsError:
        pass

    # logger.info('Started')
    app = QtWidgets.QApplication(sys.argv)
    ui = ConfigPanel()
    ui.show()
    
    sys.exit(app.exec_())
    # logger.info('Finished')
