# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'cp.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


import json
import time

import psutil
from PyQt5 import QtCore, QtGui, QtWidgets

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


class Ui_ConfigPanel(object):
    def setupUi(self, ConfigPanel):
        ConfigPanel.setObjectName("ConfigPanel")
        ConfigPanel.resize(532, 616)
        ConfigPanel.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.centralwidget = QtWidgets.QWidget(ConfigPanel)
        self.centralwidget.setObjectName("centralwidget")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(10, 40, 501, 80))
        self.groupBox.setObjectName("groupBox")
        self.label_host = QtWidgets.QLabel(self.groupBox)
        self.label_host.setGeometry(QtCore.QRect(10, 20, 91, 21))
        self.label_host.setObjectName("label_host")
        self.label_port = QtWidgets.QLabel(self.groupBox)
        self.label_port.setGeometry(QtCore.QRect(10, 50, 91, 21))
        self.label_port.setObjectName("label_port")
        self.line_host = QtWidgets.QLineEdit(self.groupBox)
        self.line_host.setGeometry(QtCore.QRect(110, 20, 381, 20))
        self.line_host.setObjectName("line_host")
        self.line_port = QtWidgets.QLineEdit(self.groupBox)
        self.line_port.setGeometry(QtCore.QRect(110, 50, 381, 20))
        self.line_port.setObjectName("line_port")
        self.groupBox_2 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_2.setGeometry(QtCore.QRect(10, 130, 501, 371))
        self.groupBox_2.setObjectName("groupBox_2")
        self.table_trigs_params = QtWidgets.QTableWidget(self.groupBox_2)
        self.table_trigs_params.setGeometry(QtCore.QRect(10, 50, 481, 281))
        self.table_trigs_params.setObjectName("table_trigs_params")
        self.table_trigs_params.setColumnCount(4)
        self.table_trigs_params.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.table_trigs_params.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_trigs_params.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_trigs_params.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_trigs_params.setHorizontalHeaderItem(3, item)
        self.add_trig = QtWidgets.QPushButton(self.groupBox_2)
        self.add_trig.setGeometry(QtCore.QRect(470, 340, 21, 23))
        self.add_trig.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(
            "../resources/iconfinder_Create_132699.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.add_trig.setIcon(icon)
        self.add_trig.setObjectName("add_trig")
        self.del_trig = QtWidgets.QPushButton(self.groupBox_2)
        self.del_trig.setGeometry(QtCore.QRect(440, 340, 21, 23))
        self.del_trig.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(
            "../resources/iconfinder_Cancel_132620.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.del_trig.setIcon(icon1)
        self.del_trig.setObjectName("del_trig")
        self.combo_program = QtWidgets.QComboBox(self.groupBox_2)
        self.combo_program.setGeometry(QtCore.QRect(10, 20, 331, 22))
        self.combo_program.setObjectName("combo_programm")
        self.combo_program.addItem("")
        self.label = QtWidgets.QLabel(self.groupBox_2)
        self.label.setGeometry(QtCore.QRect(340, 20, 141, 21))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.button_start = QtWidgets.QPushButton(self.centralwidget)
        self.button_start.setGeometry(QtCore.QRect(400, 10, 111, 31))
        self.button_start.setObjectName("button_start")
        self.button_stop = QtWidgets.QPushButton(self.centralwidget)
        self.button_stop.setEnabled(False)
        self.button_stop.setGeometry(QtCore.QRect(280, 10, 111, 31))
        self.button_stop.setAutoDefault(False)
        self.button_stop.setDefault(False)
        self.button_stop.setFlat(False)
        self.button_stop.setObjectName("button_stop")
        self.groupBox_3 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_3.setGeometry(QtCore.QRect(10, 509, 231, 61))
        self.groupBox_3.setObjectName("groupBox_3")
        self.line_low_freq = QtWidgets.QLineEdit(self.groupBox_3)
        self.line_low_freq.setGeometry(QtCore.QRect(40, 20, 61, 21))
        self.line_low_freq.setObjectName("line_low_freq")
        self.line_high_freq = QtWidgets.QLineEdit(self.groupBox_3)
        self.line_high_freq.setGeometry(QtCore.QRect(150, 20, 61, 21))
        self.line_high_freq.setObjectName("line_high_freq")
        self.label_low = QtWidgets.QLabel(self.groupBox_3)
        self.label_low.setGeometry(QtCore.QRect(20, 20, 21, 21))
        self.label_low.setObjectName("label_low")
        self.label_high = QtWidgets.QLabel(self.groupBox_3)
        self.label_high.setGeometry(QtCore.QRect(120, 20, 31, 21))
        self.label_high.setObjectName("label_high")
        self.checkBox_trigEmul = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_trigEmul.setGeometry(QtCore.QRect(40, 10, 131, 17))
        self.checkBox_trigEmul.setObjectName("checkBox_trigEmul")
        ConfigPanel.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(ConfigPanel)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 532, 21))
        self.menubar.setObjectName("menubar")
        ConfigPanel.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(ConfigPanel)
        self.statusbar.setObjectName("statusbar")
        ConfigPanel.setStatusBar(self.statusbar)

        self.retranslateUi(ConfigPanel)
        self.initThreadUI()
        self.connectUI()

        QtCore.QMetaObject.connectSlotsByName(ConfigPanel)

    def retranslateUi(self, ConfigPanel):
        _translate = QtCore.QCoreApplication.translate
        ConfigPanel.setWindowTitle(_translate(
            "ConfigPanel", "Configuration Panel"))
        self.groupBox.setTitle(_translate(
            "ConfigPanel", "Brainamp configuation"))
        self.label_host.setText(_translate("ConfigPanel", "Host"))
        self.label_port.setText(_translate("ConfigPanel", "Port"))
        self.line_host.setText(_translate("ConfigPanel", "127.0.0.1"))
        self.line_port.setText(_translate("ConfigPanel", "51244"))
        self.groupBox_2.setTitle(_translate(
            "ConfigPanel", "Trigger configuration"))
        item = self.table_trigs_params.horizontalHeaderItem(0)
        item.setText(_translate("ConfigPanel", "label"))
        item = self.table_trigs_params.horizontalHeaderItem(1)
        item.setText(_translate("ConfigPanel", "left sweep"))
        item = self.table_trigs_params.horizontalHeaderItem(2)
        item.setText(_translate("ConfigPanel", "right sweep"))
        item = self.table_trigs_params.horizontalHeaderItem(3)
        item.setText(_translate("ConfigPanel", "max stack"))
        self.label.setText(_translate("ConfigPanel", "Detected"))
        self.button_start.setText(_translate("ConfigPanel", "Start"))
        self.button_stop.setText(_translate("ConfigPanel", "Stop"))
        self.groupBox_3.setTitle(_translate("ConfigPanel", "Passband Filter"))
        self.line_low_freq.setText(_translate("ConfigPanel", "1"))
        self.line_high_freq.setText(_translate("ConfigPanel", "20"))
        self.label_low.setText(_translate("ConfigPanel", "Low"))
        self.label_high.setText(_translate("ConfigPanel", "High"))
        self.checkBox_trigEmul.setText(
            _translate("ConfigPanel", "triggers emulation"))

    def initThreadUI(self):

        self.read_configuration()

        self.thread_detector = ProcessDetector()
        self.thread_detector.set_process_waited(
            self.triggers_parameters.keys())
        self.thread_detector.start()

    def connectUI(self):
        self.button_start.clicked.connect(self.on_start_running)
        self.button_stop.clicked.connect(self.on_stop_running)

        self.add_trig.clicked.connect(self.on_adding_trigger)
        self.del_trig.clicked.connect(self.on_deleting_trigger)

        self.thread_detector.process_detected.connect(self.on_new_process)

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
                print(
                    'Left and right sweep has to be Float value, and the maximum stock Integer value.')
                return

        return params

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

    def on_start_running(self):
        """This function is a slot who collect parameter from the
        control panel and initialise the pyacq web(StreamHandler)

        """

        try:
            lf = float(self.line_low_freq.text())
            hf = float(self.line_high_freq.text())
        except ValueError:
            print("High and low frequency has to be float type.")
            return

        host = str(self.line_host.text())
        try:
            port = int(self.line_port.text())
        except ValueError:
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

    def on_new_epochs(self, label, epochs):
        """This function is a slot who receive a stack of epochs"""
        print(label)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ConfigPanel = QtWidgets.QMainWindow()
    ui = Ui_ConfigPanel()
    ui.setupUi(ConfigPanel)
    ConfigPanel.show()
    sys.exit(app.exec_())
