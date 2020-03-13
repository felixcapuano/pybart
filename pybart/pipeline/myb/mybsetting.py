import logging
import os
import time

import h5py
from PyQt5 import QtCore, QtWidgets

from .mybtemplatecalibration import generate_template
from .ui_mybsettingdialog import Ui_MybSettingDialog

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s  %(levelname)s (%(name)s) -> %(message)s')

file_handler = logging.FileHandler('log\\pipelinesetting.log')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

class TemplateGenerator(QtCore.QThread):
    """Tread running the calibration function
    
    The calibration estimation time execution is 13000ms, but it can be longer or shorter.
    
    """
    def __init__(self, calib_path, reject_rate, low_freq, high_freq, parent=None):
        super(TemplateGenerator, self).__init__(parent)
        
        self.current_calib_file = calib_path
        self.reject_rate = reject_rate
        self.low_freq = low_freq
        self.high_freq = high_freq

    def run(self):
        generate_template(self.current_calib_file,
                                rejection_rate=self.reject_rate,
                                l_freq=self.low_freq,
                                h_freq=self.high_freq)

class MybSettingDialog(QtWidgets.QDialog, Ui_MybSettingDialog):
    """Dialog window to setup the myb pipeline"""

    def __init__(self, parent):
        super(QtWidgets.QDialog, self).__init__(self)

        # init view from python file generated with Qt Designer
        self.setupUi(self)
        
        # connect all component
        self.connect_ui()

        # init dialog to display error
        self.error_dialog = QtWidgets.QErrorMessage()

        # set default low, high frequency of the calibration
        self.low_freq = 0.5
        self.high_freq = 20
        self.line_low_freq.setText(str(self.low_freq))
        self.line_high_freq.setText(str(self.high_freq))
        
        # set default rejection rate of the calibration
        self.reject_rate = 0.1
        self.line_rejection_rate.setText(str(self.reject_rate))


        # set default template file path
        self.template_riemann = {}
        self.current_template = "TemplateRiemann\\template.h5"
        self.label_filename_template.setText(os.path.basename(self.current_template))
        self.load_template()

        # set default calibration file path
        # empty to avoid calibration to start
        self.current_calib_file = ""

        # init timer to run the progress bar during the calibration
        # using a approximate time of the process
        estimate_time = 13000 # ms
        self.timer_progress_bar = QtCore.QTimer(self)
        self.timer_progress_bar.setInterval(estimate_time/100)
        self.timer_progress_bar.timeout.connect(self.on_step)
        
    def connect_ui(self):
        # connect calibration button
        self.button_file_calibration.clicked.connect(self.on_select_calibration)
        self.button_run_calibration.clicked.connect(self.on_run_calibration)

        # connect template button
        self.button_file_template.clicked.connect(self.on_select_template)

    def load_template(self):
        """Load all template thanks to a .h5 file"""

        extension = os.path.splitext(self.current_template)[1]
        if extension != '.h5':
            raise ValueError("{} file not supported".format(self.current_template))

        self.f = h5py.File(self.current_template, 'r')

        for element in self.f:
            groupe = self.f[element]

            for element in groupe:
                self.template_riemann[element] = groupe[element]

        logger.info("Template loaded : {}".format(self.current_template))

    def on_step(self):
        """Update the calibration progress bar"""
        
        # take current value
        old_value = self.progressBar_calibration.value()
        
        # add 1 step
        self.progressBar_calibration.setValue(old_value + 1)

    def on_select_calibration(self):
        calib_path = QtWidgets.QFileDialog.getOpenFileName(self,
                                                       self.tr("Open Template"),
                                                       "eeg_data_sample/",
                                                       self.tr("VHDR Files (*.vhdr)"))[0]

        if calib_path is not "":
            self.current_calib_file = calib_path

            calibration_name = os.path.basename(self.current_calib_file)
            self.label_filename_calibration.setText(calibration_name)
            
            # reset the progress bar before starting calibration
            self.progressBar_calibration.setValue(0) 

    def on_select_template(self):
        template_path = QtWidgets.QFileDialog.getOpenFileName(self,
                                                       self.tr("Open Template"),
                                                       "TemplateRiemann/",
                                                       self.tr("H5 Files (*.h5)"))[0]
        if template_path is not "":
            self.current_template = template_path

            template_name = os.path.basename(self.current_template)
            self.label_filename_template.setText(template_name)


            self.load_template()

    def on_run_calibration(self):
        if self.current_calib_file is not "":
            try:
                # get the low and high frequency in float
                self.low_freq = float(self.line_low_freq.text())
                self.high_freq = float(self.line_high_freq.text())
                self.reject_rate = float(self.line_rejection_rate.text())
            except ValueError:
                error = "High,low frequency and rejection rate has to be float type."
                self.error_dialog.showMessage(error)
                logger.warning(error)
                return

            if not 0 <= self.reject_rate <= 1:
                error = "Rejection rate has to be between 0 and 1."
                self.error_dialog.showMessage(error)
                logger.warning(error)
                return

            if not 0 < self.low_freq or not self.low_freq < self.high_freq :
                error = "Wrong frequency."
                self.error_dialog.showMessage(error)
                logger.warning(error)
                return
            
            logger.info('Started template generation ({})'.format(self.current_calib_file))
            self.timer_progress_bar.start()
            self.thread_template = TemplateGenerator(self.current_calib_file,
                                                    self.reject_rate,
                                                    self.low_freq,
                                                    self.high_freq)
            self.thread_template.finished.connect(self.on_template_generated)
            self.thread_template.start()
            
            self.setEnabled_groupCalib(False)
            
        else:
            error = "You have to select a file."
            self.error_dialog.showMessage(error)
            logger.warning(error)
            return
    
    def on_template_generated(self):
        logger.info('Finished template generated ({})'.format(self.current_calib_file))
        
        # stop timer and fill the progress bar 
        self.timer_progress_bar.stop()
        self.progressBar_calibration.setValue(100)
        
        self.setEnabled_groupCalib(True)
        
    def setEnabled_groupCalib(self, boolean):
        self.line_high_freq.setEnabled(boolean)
        self.line_low_freq.setEnabled(boolean)
        self.line_rejection_rate.setEnabled(boolean)
        self.button_file_calibration.setEnabled(boolean)
        self.button_run_calibration.setEnabled(boolean)
