import json
import os.path
import time

from PyQt5 import QtCore, QtGui, QtWidgets

from pipeline.mybpipeline import MybPipeline
from streamhandler import StreamHandler
from ui_configpanel import Ui_ConfigPanel
from pipeline.mybtemplatecalibration import generate_template


class ConfigPanel(QtWidgets.QMainWindow, Ui_ConfigPanel):

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        
        self.error_dialog = QtWidgets.QErrorMessage()

        self.setupUi(self)
        self.connect_ui()

        self.load_configuration()
        self.fill_combo_setup()

        self.simul_file = 'No File Selected'

        self.pipeline = MybPipeline()

        # TODO Improve
        self.line_zmq_address.setText("tcp://127.0.0.1:{}".format(self.pipeline.port))

    def connect_ui(self):
        """This function connect UI elements to all respective slot"""

        self.button_start.clicked.connect(self.on_start_running)
        self.button_stop.clicked.connect(self.on_stop_running)

        self.add_trig.clicked.connect(self.on_adding_trigger)
        self.del_trig.clicked.connect(self.on_deleting_trigger)

        self.combo_setup.currentIndexChanged.connect(self.on_new_setup)

        self.button_settings.clicked.connect(self.on_settings)

        # # TODO Improve pipeline selection
        # self.combo_pipeline.currentIndexChanged.connect(self.on_select_pipeline)
        self.button_settings.setEnabled(True)
        # # End TODO

        self.button_file_simulated.clicked.connect(self.on_simulation_file)

        self.radio_BVRec.toggled.connect(self.on_select_BVRec)
        self.radio_simulate.toggled.connect(self.on_select_simulate)

        self.action_MYBcalibration.triggered.connect(self.on_myb_calibration)

    def load_configuration(self):
        """This function read all setup parameter from json configuration file"""

        with open('pybart\\configuration.json') as params:
            self.triggers_parameters = json.load(params)

    def get_table_params(self):
        """This function return current parameter from de table"""

        params = {}
        row = 0
        t = self.table_trigs_params

        for row in range(t.rowCount()):
            try:
                label = str(t.item(row, 0).text())
                left_sweep = float(t.item(row, 1).text())
                right_sweep = float(t.item(row, 2).text())
            except ValueError:
                raise ValueError('Left and right sweep has to be Float value.')

            try:
                max_stock = int(t.item(row, 3).text())
            except ValueError:
                raise ValueError('Left and right sweep has to be Float value.')

            params[label] = {}
            params[label]['left_sweep'] = float(left_sweep)
            params[label]['right_sweep'] = float(right_sweep)
            params[label]['max_stock'] = int(max_stock)

        return params
        
    def fill_combo_setup(self):
        self.combo_setup.clear()
        for setup in self.triggers_parameters.keys():
            self.combo_setup.addItem(setup)

    def on_simulation_file(self):
        self.dialog_simul = QtWidgets.QFileDialog.getOpenFileName(self,
                                                       self.tr("Open Template"),
                                                       "eeg_data_sample/",
                                                       self.tr("Image Files (*.vhdr)"))
        if self.dialog_simul[0] is not '':
            self.simul_file = str(self.dialog_simul[0])
            
        self.label_filename.setText(os.path.basename(self.simul_file))

    def on_select_BVRec(self):
        if self.radio_BVRec.isChecked():
            self.line_host.setEnabled(True)
            self.line_port.setEnabled(True)
        else:
            self.line_host.setEnabled(False)
            self.line_port.setEnabled(False)
    
    def on_select_simulate(self):
        if self.radio_simulate.isChecked():
            self.frame_select_file.setEnabled(True)
        else:
            self.frame_select_file.setEnabled(False)

    def on_myb_calibration(self):

        self.dialog_simul = QtWidgets.QFileDialog.getOpenFileName(self,
                                                       self.tr("Open Template"),
                                                       "eeg_data_sample/",
                                                       self.tr("Image Files (*.vhdr)"))
        if self.dialog_simul[0] is not '':
            try:
                generate_template(self.dialog_simul[0])
            except ValueError as e:
                self.error_dialog.showMessage(e)

    def on_start_running(self):
        """This function is a slot who collect parameter from the
        control panel and initialise the pyacq web(StreamHandler)

        """

        try:
            # get the low and high frequency in float
            low_frequency = float(self.line_low_freq.text())
            high_frequency = float(self.line_high_freq.text())
        except ValueError:
            self.error_dialog.showMessage(
                "High and low frequency has to be float type.")
            return

        host = str(self.line_host.text())
        try:
            # get the port number in int
            port = int(self.line_port.text())
        except ValueError:
            # TODO popup message
            self.error_dialog.showMessage("The port has to be int type.")
            return

        # get parameter of the table
        try:
            params = self.get_table_params()
        except ValueError as e:
            self.error_dialog.showMessage("{}".format(e))
            return
        

        # setup parmeter in the stream handler
        if self.radio_BVRec.isChecked():
            self.sh = StreamHandler(brainamp_host=host, brainamp_port=port)
        else:
            self.sh = StreamHandler(None, None, simulated=True, raw_file=self.simul_file)

        try:
            self.sh.configuration(low_frequency,
                                high_frequency,
                                trig_params=params)
        except ConnectionRefusedError as e:
            self.error_dialog.showMessage("BrainVision Recorder not recording: {}".format(e))
            return
        except ValueError as e:
            self.error_dialog.showMessage("{}".format(e))
            return
            

        # set the emission slot for each new stack of epochs
        # self.sh.set_slot_new_epochs(self.on_new_epochs)
        self.sh.nodes['epochermultilabel'].new_chunk.connect(self.on_new_epochs)

        # start the stream handler
        self.sh.start_node()

        self.button_stop.setEnabled(True)
        self.button_start.setEnabled(False)


    def on_stop_running(self):
        """This function is a slot who stop pyacq all pyacq node"""
        
        self.sh.stop_node()

        self.button_stop.setEnabled(False)
        self.button_start.setEnabled(True)

        self.pipeline.reset()

        self.lcd_triggers_count.display(0)

    def on_new_setup(self):
        """This function is a slot whaiting for an index change
        from the comboBox.
        -delete all row
        -adding parameter according to the json configuration file

        """

        # clear table
        self.table_trigs_params.setRowCount(0)

        # fill table with triggers parameters according to the current programm
        program = self.combo_setup.currentText()
        if program != "":
            triggers = self.triggers_parameters[program]

            row_count = 0
            for label, params in triggers.items():
                self.table_trigs_params.insertRow(row_count)

                self.table_trigs_params.setItem(row_count,
                                                0,
                                                QtGui.QTableWidgetItem(label))

                self.table_trigs_params.setItem(row_count,
                                                1,
                                                QtGui.QTableWidgetItem(str(params['left_sweep'])))

                self.table_trigs_params.setItem(row_count,
                                                2,
                                                QtGui.QTableWidgetItem(str(params['right_sweep'])))

                self.table_trigs_params.setItem(row_count,
                                                3,
                                                QtGui.QTableWidgetItem(str(params['max_stock'])))

                row_count = +1

    # # TODO add validate button
    # def on_select_pipeline(self):
    #     """This function is a slot modifying the pipeline"""

    #     self.pipeline = self._pipeline[self.combo_pipeline.currentText()]
        
    #     if self.combo_pipeline.count() == 0:
    #         self.button_settings.setEnabled(False)
    #     else:
    #         self.button_settings.setEnabled(True)
        

    # TODO set icon add modify method
    def on_adding_trigger(self):
        self.table_trigs_params.insertRow(0)

    # TODO set icon add modify method
    def on_deleting_trigger(self):
        self.table_trigs_params.removeRow(0)

    def on_settings(self):
        """This function is a slot who open a open file window
        and set the name of the file selected in the label

        """
        self.dialog_template = QtWidgets.QFileDialog.getOpenFileName(self,
                                                       self.tr("Open Template"),
                                                       "TemplateRiemann/",
                                                       self.tr("Image Files (*.h5)"))
        if self.dialog_template[0] is not '':
            self.pipeline.set_template_name(self.dialog_template[0])     

    def on_new_epochs(self, label, epochs):
        """This function is a slot who receive a stack of epochs"""
        self.pipeline.new_epochs(label, epochs)

        # display count of triggers
        nb_triggers = self.lcd_triggers_count.intValue()
        self.lcd_triggers_count.display(nb_triggers+1)
        

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = ConfigPanel()
    ui.show()
    sys.exit(app.exec_())
