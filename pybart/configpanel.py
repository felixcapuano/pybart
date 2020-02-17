import json
import time

import psutil
from PyQt5 import QtCore, QtGui, QtWidgets

from ui_configpanel import Ui_ConfigPanel
from streamhandler import StreamHandler


class ProcessDetector(QtCore.QThread):

    _process_waited = []
    _process_running = []
    refresh_time = 1

    process_detected = QtCore.pyqtSignal(list)

    def set_process_waited(self, pw):
        self._process_waited = pw

    def run(self):
        while True:
            last_process_running = self._process_running

            self._process_running = []
            for process in psutil.process_iter():
                if process.name() in self._process_waited:
                    self._process_running.append(process.name())

            if last_process_running != self._process_running:
                self.process_detected.emit(self._process_running)
            
            time.sleep(self.refresh_time)

    def stop(self):
        self.terminate()


class ConfigPanel(QtWidgets.QMainWindow, Ui_ConfigPanel):

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)

        self.error_dialog = QtWidgets.QErrorMessage()

        self.setupUi(self)
        self.init_thread()
        self.connect_ui()

    def init_thread(self):
        """This function initialise the process detector

        - load configuration.json file
        - initialise ProcessDetector who checking if programm listed in configuration.json is running

        """
        self.load_configuration()

        self.process_detector = ProcessDetector()
        self.process_detector.set_process_waited(
            self.triggers_parameters.keys())
        self.process_detector.start()

    def connect_ui(self):
        """This function connect UI elements to all respective slot"""

        self.button_start.clicked.connect(self.on_start_running)
        self.button_stop.clicked.connect(self.on_stop_running)

        self.add_trig.clicked.connect(self.on_adding_trigger)
        self.del_trig.clicked.connect(self.on_deleting_trigger)

        self.process_detector.process_detected.connect(self.on_new_process)

        self.combo_program.currentIndexChanged.connect(self.on_program)

        self.button_option.clicked.connect(self.on_select_template)

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
                return 'Left and right sweep has to be Float value.'

            try:
                max_stock = int(t.item(row, 3).text())
            except ValueError:
                return 'Maximum stock has to be Integer value.'

            params[label] = {}
            params[label]['left_sweep'] = float(left_sweep)
            params[label]['right_sweep'] = float(right_sweep)
            params[label]['max_stock'] = int(max_stock)

        return params

    def on_start_running(self):
        """This function is a slot who collect parameter from the
        control panel and initialise the pyacq web(StreamHandler)

        """
        self.process_detector.stop()
        
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
        params = self.get_table_params()
        if type(params) is str:
            self.error_dialog.showMessage(params)
            return

        # setup parmeter in the stream handler
        self.sh = StreamHandler(brainamp_host=host, brainamp_port=port)
        self.sh.configuration(low_frequency,
                              high_frequency,
                              trig_params=params,
                              trig_simulate=self.checkBox_trigEmul.isChecked(),
                              sig_simulate=False)

        # set the emission slot for each new stack of epochs
        self.sh.set_slot_new_epochs(self.on_new_epochs)

        # start the stream handler
        self.sh.start_node()

        self.button_stop.setEnabled(True)
        self.button_start.setEnabled(False)

    def on_stop_running(self):
        """This function is a slot who stop pyacq all pyacq node"""

        self.process_detector.start()
        
        self.sh.stop_node()

        self.button_stop.setEnabled(False)
        self.button_start.setEnabled(True)

    def on_program(self):
        """This function is a slot whaiting for an index change
        from the comboBox.
        -delete all row
        -adding parameter according to the json configuration file

        """
        if self.combo_program.count() > 0:
            self.button_option.setEnabled(True)
        else:
            self.button_option.setEnabled(False)

        # clear table
        self.table_trigs_params.setRowCount(0)

        # fill table with triggers parameters according to the current programm
        program = self.combo_program.currentText()
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

    def on_new_process(self, process_running):
        """This function is a slot who received process running
        from the thead(ProcessDetector)

        """

        self.combo_program.clear()
        self.combo_program.addItems(process_running)

    # TODO set icon add modify method
    def on_adding_trigger(self):
        self.table_trigs_params.insertRow(0)

    # TODO set icon add modify method
    def on_deleting_trigger(self):
        self.table_trigs_params.removeRow(0)

    def on_select_template(self):
        """This function is a slot who open a open file window
        and set the name of the file selected in the label

        """
        self.dialog = QtWidgets.QFileDialog.getOpenFileName(self,
                                                       self.tr("Open Template"),
                                                       "TemplateRiemann/",
                                                       self.tr("Image Files (*.h5)"))

    def on_new_epochs(self, label, epochs):
        """This function is a slot who receive a stack of epochs"""
        print(label)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = ConfigPanel()
    ui.show()
    sys.exit(app.exec_())
