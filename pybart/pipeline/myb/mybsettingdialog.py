import os
import time

from PyQt5 import QtCore, QtWidgets 

from .mybtemplatecalibration import generate_template
from .ui_mybsettingdialog import Ui_MybSettingDialog


class MybSettingDialog(QtWidgets.QDialog, Ui_MybSettingDialog):

    def __init__(self, parent):
        super().__init__(parent)

        self.setupUi(self)
        self.connect_ui()

        self.error_dialog = QtWidgets.QErrorMessage()

        self.low_freq = 0.5
        self.line_low_freq.setText(str(self.low_freq))
        self.high_freq = 20
        self.line_high_freq.setText(str(self.high_freq))

        self.reject_rate = 0.1
        self.line_rejection_rate.setText(str(self.reject_rate))

        self.current_template = "TemplateRiemann\\template.h5"
        
        self.label_filename_template.setText(os.path.basename(os.path.basename(self.current_template)))

        self.calib_path = ""

        self.timer_progress_bar = QtCore.QTimer(self)
        self.timer_progress_bar.setInterval(15000/100)
        self.timer_progress_bar.timeout.connect(self.on_step)
        

    def on_step(self):
        print('hey')

    def connect_ui(self):
        # calibration
        self.button_file_calibration.clicked.connect(self.on_calibration_file)
        self.button_run_calibration.clicked.connect(self.on_run_calibration)

        # template
        self.button_file_template.clicked.connect(self.on_template_file)
        
    def on_calibration_file(self):
        self.calib_path = QtWidgets.QFileDialog.getOpenFileName(self,
                                                       self.tr("Open Template"),
                                                       "eeg_data_sample/",
                                                       self.tr("VHDR Files (*.vhdr)"))[0]

        if self.calib_path is not "":
            calibration_name = os.path.basename(self.calib_path)

            self.label_filename_calibration.setText(calibration_name)
        
            

    def on_template_file(self):
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
            
            self.timer_progress_bar.start()
            # TODO use threading
            generate_template(self.calib_path,
                                rejection_rate=self.reject_rate,
                                l_freq=self.low_freq,
                                h_freq=self.high_freq)

            # reset file
            self.calib_path = ""
            self.label_filename_calibration.setText("No File Selected")
        else:
            self.error_dialog.showMessage( "You have to select a file.")

    
