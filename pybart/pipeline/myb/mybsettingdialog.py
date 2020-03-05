import os
import time

from PyQt5 import QtCore, QtWidgets 

from .mybtemplatecalibration import generate_template
from .ui_mybsettingdialog import Ui_MybSettingDialog

class TemplateGenerator(QtCore.QThread):
    """Tread running the calibration function
    
    (estimate execution time : 13000ms)
    
    """
    
    def __init__(self, calib_path, reject_rate, low_freq, high_freq, parent=None):
        super(TemplateGenerator, self).__init__(parent)
        
        self.calib_path = calib_path
        self.reject_rate = reject_rate
        self.low_freq = low_freq
        self.high_freq = high_freq
        

    def run(self):
        generate_template(self.calib_path,
                                rejection_rate=self.reject_rate,
                                l_freq=self.low_freq,
                                h_freq=self.high_freq)

class MybSettingDialog(QtWidgets.QDialog, Ui_MybSettingDialog):
    """Dialog window to setup the myb pipeline"""

    def __init__(self, parent):
        super().__init__(parent)

        # use view from python file generated with Qt Designer
        self.setupUi(self)
        
        # connect all component
        self.connect_ui()

        # display error in a dialog
        self.error_dialog = QtWidgets.QErrorMessage()

        # set default low, high frequency of the calibration
        self.low_freq = 0.5
        self.line_low_freq.setText(str(self.low_freq))
        self.high_freq = 20
        self.line_high_freq.setText(str(self.high_freq))
        
        # set default rejection rate of the calibration
        self.reject_rate = 0.1
        self.line_rejection_rate.setText(str(self.reject_rate))

        # set default template file path
        self.current_template = "TemplateRiemann\\template.h5"
        self.label_filename_template.setText(os.path.basename(os.path.basename(self.current_template)))
        
        # set default calibration file path
        self.calib_path = ""

        # init timer to run the progress bar during the calibration
        # using a approximate time of the process
        estimate_time = 13000 # ms
        self.timer_progress_bar = QtCore.QTimer(self)
        self.timer_progress_bar.setInterval(estimate_time/100)
        self.timer_progress_bar.timeout.connect(self.on_step)
        
    def connect_ui(self):
        # calibration
        self.button_file_calibration.clicked.connect(self.on_select_calibration)
        self.button_run_calibration.clicked.connect(self.on_run_calibration)

        # template
        self.button_file_template.clicked.connect(self.on_select_template)

    def on_step(self):
        """Update the calibration progress bar"""
        
        # take current value
        old_value = self.progressBar_calibration.value()
        
        # add 1 step
        self.progressBar_calibration.setValue(old_value + 1)

    def on_select_calibration(self):
        self.calib_path = QtWidgets.QFileDialog.getOpenFileName(self,
                                                       self.tr("Open Template"),
                                                       "eeg_data_sample/",
                                                       self.tr("VHDR Files (*.vhdr)"))[0]

        if self.calib_path is not "":
            calibration_name = os.path.basename(self.calib_path)
            self.label_filename_calibration.setText(calibration_name)
            
            # reset the progresse bar
            self.progressBar_calibration.setValue(0)
        
            

    def on_select_template(self):
        self.template_path = QtWidgets.QFileDialog.getOpenFileName(self,
                                                       self.tr("Open Template"),
                                                       "TemplateRiemann/",
                                                       self.tr("H5 Files (*.h5)"))[0]
        if self.template_path is not "":
            template_name = os.path.basename(self.template_path)
            self.current_template = self.template_path
            self.label_filename_template.setText(template_name)

        #     self.pipeline.set_template_name(self.dialog_template[0])

    def on_run_calibration(self):
        if self.calib_path is not "":

            try:
                # get the low and high frequency in float
                self.low_freq = float(self.line_low_freq.text())
                self.high_freq = float(self.line_high_freq.text())
                self.reject_rate = float(self.line_rejection_rate.text())
            except ValueError:
                self.error_dialog.showMessage(
                    "High,low frequency and rejection rate has to be float type.")
                return

            if not 0 <= self.reject_rate <= 1:
                self.error_dialog.showMessage(
                    "Rejection rate has to be between 0 and 1.")
                return

            if not 0 < self.low_freq or not self.low_freq < self.high_freq :
                self.error_dialog.showMessage("Wrong frequency.")
                return
            
            # TODO use threading
            self.timer_progress_bar.start()
            self.thread_template = TemplateGenerator(self.calib_path,
                                                    self.reject_rate,
                                                    self.low_freq,
                                                    self.high_freq)
            self.thread_template.finished.connect(self.on_template_generated)
            self.thread_template.start()
            
            self.setEnabled_groupCalib(False)
            
        else:
            self.error_dialog.showMessage( "You have to select a file.")
    
    def on_template_generated(self):
        print('template generated')
        
        # stop timer
        self.timer_progress_bar.stop()
        self.progressBar_calibration.setValue(100)
        
        self.setEnabled_groupCalib(True)
        
    def setEnabled_groupCalib(self, boolean):
        self.line_high_freq.setEnabled(boolean)
        self.line_low_freq.setEnabled(boolean)
        self.line_rejection_rate.setEnabled(boolean)
        self.button_file_calibration.setEnabled(boolean)
        self.button_run_calibration.setEnabled(boolean)

    
