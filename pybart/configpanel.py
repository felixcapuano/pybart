import json
import time

import psutil
from PyQt5 import QtCore, QtGui, QtWidgets

from ui_configpanelW import Ui_ConfigPanel
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


class ConfigPanel(QtWidgets.QWidget, Ui_ConfigPanel):

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        
        self.setupUi(self)
        self.initThreadUi()
        self.connectUi()
        
    def initThreadUi(self):
        self.read_configuration()

        self.process_detector = ProcessDetector()
        self.process_detector.set_process_waited(self.triggers_parameters.keys())
        self.process_detector.start()

    def connectUi(self):
        self.button_start.clicked.connect(self.on_start_running)
        self.button_stop.clicked.connect(self.on_stop_running)

        self.add_trig.clicked.connect(self.on_adding_trigger)
        self.del_trig.clicked.connect(self.on_deleting_trigger)

        self.process_detector.process_detected.connect(self.on_new_process)

        self.combo_program.currentIndexChanged.connect(self.on_program)

    def read_configuration(self):
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
                params[t.item(row, 0).text()] = {}
                params[t.item(row, 0).text()]['left_sweep'] = float(
                    t.item(row, 1).text())
                params[t.item(row, 0).text()]['right_sweep'] = float(
                    t.item(row, 2).text())
                params[t.item(row, 0).text()]['max_stock'] = int(
                    t.item(row, 3).text())
            except ValueError:
                # TODO popup message
                print(
                    'Left and right sweep has to be Float value, and the maximum stock Integer value.')
                return

        return params

    def on_start_running(self):
        """This function is a slot who collect parameter from the
        control panel and initialise the pyacq web(StreamHandler)

        """

        try:
            lf = float(self.line_low_freq.text())
            hf = float(self.line_high_freq.text())
        except ValueError:
            
            # TODO popup message
            print("High and low frequency has to be float type.")
            return

        host = str(self.line_host.text())
        try:
            port = int(self.line_port.text())
        except ValueError:
            # TODO popup message
            print("The port has to be int type.")
            return

        self.nw = StreamHandler(brainamp_host=host, brainamp_port=port)
        self.nw.configuration(lf, hf, trig_params=self.get_table_params(), trig_simulate=self.checkBox_trigEmul.isChecked())
        self.nw.set_slot_new_epochs(self.on_new_epochs)

        self.nw.start_node()

        self.button_stop.setEnabled(True)
        self.button_start.setEnabled(False)

    def on_stop_running(self):
        """This function is a slot who stop pyacq all pyacq node"""

        self.nw.stop_node()

        self.button_stop.setEnabled(False)
        self.button_start.setEnabled(True)

    def on_program(self):
        """This function is a slot whaiting for an index change
        from the comboBox.
        -delete all row
        -adding parameter according to the json configuration file

        """

        # clear table
        self.table_trigs_params.setRowCount(0)

        program = self.combo_program.currentText()
        if program != "":
            triggers = self.triggers_parameters[program]

            row_count = 0
            for label, params in triggers.items():
                self.table_trigs_params.insertRow(row_count)

                self.table_trigs_params.setItem(
                    row_count, 0, QtGui.QTableWidgetItem(label))
                self.table_trigs_params.setItem(
                    row_count, 1, QtGui.QTableWidgetItem(str(params['left_sweep'])))
                self.table_trigs_params.setItem(
                    row_count, 2, QtGui.QTableWidgetItem(str(params['right_sweep'])))
                self.table_trigs_params.setItem(
                    row_count, 3, QtGui.QTableWidgetItem(str(params['max_stock'])))
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

    def on_new_epochs(self, label, epochs):
        """This function is a slot who receive a stack of epochs"""
        print(label)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = ConfigPanel()
    ui.show()
    sys.exit(app.exec_())