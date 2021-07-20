from pybart.configpanel import ConfigPanel
from PyQt5 import QtWidgets
import os
import h5py
from os import path


if __name__ == "__main__":
    import sys

    try:
        os.makedirs(os.environ['USERPROFILE'] + "\Documents\CophyExperimentsData\TemplateRiemann\\")
    except FileExistsError:
        pass
    # try:
    #     os.makedirs(os.environ['USERPROFILE'] + "\Documents\PybartData\Feedback\\")
    # except FileExistsError:
    #     pass
    # try:
    #     os.makedirs(os.environ['USERPROFILE'] + "\Documents\PybartData\RawData\\")
    # except FileExistsError:
    #     pass

    if(not path.exists(os.environ['USERPROFILE'] + "\Documents\CophyExperimentsData\TemplateRiemann\\template.h5")):
        initTemplate = h5py.File(os.environ['USERPROFILE'] + "\Documents\CophyExperimentsData\TemplateRiemann\\template.h5", 'w')
        initTemplate.close()
    # logger.info('Started')
    app = QtWidgets.QApplication(sys.argv)
    ui = ConfigPanel()
    ui.show()
    
    sys.exit(app.exec_())
    # logger.info('Finished')
