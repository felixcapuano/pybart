# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_configpanel.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ConfigPanel(object):
    def setupUi(self, ConfigPanel):
        ConfigPanel.setObjectName("ConfigPanel")
        ConfigPanel.setEnabled(True)
        ConfigPanel.resize(525, 705)
        ConfigPanel.setMinimumSize(QtCore.QSize(525, 0))
        ConfigPanel.setMaximumSize(QtCore.QSize(525, 16777215))
        ConfigPanel.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.centralwidget = QtWidgets.QWidget(ConfigPanel)
        self.centralwidget.setObjectName("centralwidget")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(10, 40, 501, 181))
        self.groupBox.setObjectName("groupBox")
        self.groupBox_4 = QtWidgets.QGroupBox(self.groupBox)
        self.groupBox_4.setGeometry(QtCore.QRect(10, 100, 481, 71))
        self.groupBox_4.setTitle("")
        self.groupBox_4.setObjectName("groupBox_4")
        self.radio_simulate = QtWidgets.QRadioButton(self.groupBox_4)
        self.radio_simulate.setGeometry(QtCore.QRect(10, 10, 82, 17))
        self.radio_simulate.setObjectName("radio_simulate")
        self.radioGroup_source = QtWidgets.QButtonGroup(ConfigPanel)
        self.radioGroup_source.setObjectName("radioGroup_source")
        self.radioGroup_source.addButton(self.radio_simulate)
        self.frame_select_file = QtWidgets.QFrame(self.groupBox_4)
        self.frame_select_file.setEnabled(False)
        self.frame_select_file.setGeometry(QtCore.QRect(10, 40, 461, 21))
        self.frame_select_file.setFrameShape(QtWidgets.QFrame.Panel)
        self.frame_select_file.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_select_file.setObjectName("frame_select_file")
        self.button_file_simulated = QtWidgets.QPushButton(self.frame_select_file)
        self.button_file_simulated.setGeometry(QtCore.QRect(0, 0, 75, 21))
        self.button_file_simulated.setObjectName("button_file_simulated")
        self.label_filename = QtWidgets.QLabel(self.frame_select_file)
        self.label_filename.setGeometry(QtCore.QRect(80, 0, 371, 21))
        self.label_filename.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.label_filename.setFrameShadow(QtWidgets.QFrame.Plain)
        self.label_filename.setObjectName("label_filename")
        self.groupBox_5 = QtWidgets.QGroupBox(self.groupBox)
        self.groupBox_5.setGeometry(QtCore.QRect(10, 20, 481, 71))
        self.groupBox_5.setTitle("")
        self.groupBox_5.setObjectName("groupBox_5")
        self.radio_BVRec = QtWidgets.QRadioButton(self.groupBox_5)
        self.radio_BVRec.setGeometry(QtCore.QRect(10, 10, 121, 17))
        self.radio_BVRec.setChecked(True)
        self.radio_BVRec.setObjectName("radio_BVRec")
        self.radioGroup_source.addButton(self.radio_BVRec)
        self.line_port = QtWidgets.QLineEdit(self.groupBox_5)
        self.line_port.setGeometry(QtCore.QRect(220, 40, 251, 20))
        self.line_port.setObjectName("line_port")
        self.line_host = QtWidgets.QLineEdit(self.groupBox_5)
        self.line_host.setEnabled(True)
        self.line_host.setGeometry(QtCore.QRect(220, 10, 251, 20))
        self.line_host.setObjectName("line_host")
        self.label_port = QtWidgets.QLabel(self.groupBox_5)
        self.label_port.setGeometry(QtCore.QRect(150, 40, 61, 21))
        self.label_port.setObjectName("label_port")
        self.label_host = QtWidgets.QLabel(self.groupBox_5)
        self.label_host.setGeometry(QtCore.QRect(150, 10, 61, 21))
        self.label_host.setObjectName("label_host")
        self.groupBox_2 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_2.setGeometry(QtCore.QRect(10, 230, 501, 371))
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
        icon.addPixmap(QtGui.QPixmap("../resources/iconfinder_Create_132699.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.add_trig.setIcon(icon)
        self.add_trig.setObjectName("add_trig")
        self.del_trig = QtWidgets.QPushButton(self.groupBox_2)
        self.del_trig.setGeometry(QtCore.QRect(440, 340, 21, 23))
        self.del_trig.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("../resources/iconfinder_Cancel_132620.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.del_trig.setIcon(icon1)
        self.del_trig.setObjectName("del_trig")
        self.combo_program = QtWidgets.QComboBox(self.groupBox_2)
        self.combo_program.setGeometry(QtCore.QRect(10, 20, 331, 22))
        self.combo_program.setObjectName("combo_program")
        self.button_option = QtWidgets.QPushButton(self.groupBox_2)
        self.button_option.setEnabled(False)
        self.button_option.setGeometry(QtCore.QRect(350, 20, 141, 23))
        self.button_option.setObjectName("button_option")
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
        self.groupBox_3.setGeometry(QtCore.QRect(10, 610, 231, 51))
        self.groupBox_3.setObjectName("groupBox_3")
        self.line_low_freq = QtWidgets.QLineEdit(self.groupBox_3)
        self.line_low_freq.setGeometry(QtCore.QRect(40, 20, 61, 21))
        self.line_low_freq.setObjectName("line_low_freq")
        self.line_high_freq = QtWidgets.QLineEdit(self.groupBox_3)
        self.line_high_freq.setGeometry(QtCore.QRect(150, 20, 61, 21))
        self.line_high_freq.setObjectName("line_high_freq")
        self.label_low = QtWidgets.QLabel(self.groupBox_3)
        self.label_low.setGeometry(QtCore.QRect(10, 20, 21, 21))
        self.label_low.setObjectName("label_low")
        self.label_high = QtWidgets.QLabel(self.groupBox_3)
        self.label_high.setGeometry(QtCore.QRect(120, 20, 31, 21))
        self.label_high.setObjectName("label_high")
        self.checkBox_trigEmul = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_trigEmul.setGeometry(QtCore.QRect(40, 10, 131, 17))
        self.checkBox_trigEmul.setObjectName("checkBox_trigEmul")
        ConfigPanel.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(ConfigPanel)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 525, 21))
        self.menubar.setObjectName("menubar")
        ConfigPanel.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(ConfigPanel)
        self.statusbar.setObjectName("statusbar")
        ConfigPanel.setStatusBar(self.statusbar)

        self.retranslateUi(ConfigPanel)
        QtCore.QMetaObject.connectSlotsByName(ConfigPanel)

    def retranslateUi(self, ConfigPanel):
        _translate = QtCore.QCoreApplication.translate
        ConfigPanel.setWindowTitle(_translate("ConfigPanel", "Configuration Panel"))
        self.groupBox.setTitle(_translate("ConfigPanel", "Source"))
        self.radio_simulate.setText(_translate("ConfigPanel", "Simulate"))
        self.button_file_simulated.setText(_translate("ConfigPanel", "Select File"))
        self.label_filename.setText(_translate("ConfigPanel", "No File Selected"))
        self.radio_BVRec.setText(_translate("ConfigPanel", "BrainVision Recorder"))
        self.line_port.setText(_translate("ConfigPanel", "51244"))
        self.line_host.setText(_translate("ConfigPanel", "127.0.0.1"))
        self.label_port.setText(_translate("ConfigPanel", "Port"))
        self.label_host.setText(_translate("ConfigPanel", "Host"))
        self.groupBox_2.setTitle(_translate("ConfigPanel", "Trigger configuration"))
        item = self.table_trigs_params.horizontalHeaderItem(0)
        item.setText(_translate("ConfigPanel", "label"))
        item = self.table_trigs_params.horizontalHeaderItem(1)
        item.setText(_translate("ConfigPanel", "left sweep"))
        item = self.table_trigs_params.horizontalHeaderItem(2)
        item.setText(_translate("ConfigPanel", "right sweep"))
        item = self.table_trigs_params.horizontalHeaderItem(3)
        item.setText(_translate("ConfigPanel", "max stack"))
        self.button_option.setText(_translate("ConfigPanel", "Option"))
        self.button_start.setText(_translate("ConfigPanel", "Start"))
        self.button_stop.setText(_translate("ConfigPanel", "Stop"))
        self.groupBox_3.setTitle(_translate("ConfigPanel", "Passband Filter"))
        self.line_low_freq.setText(_translate("ConfigPanel", "1"))
        self.line_high_freq.setText(_translate("ConfigPanel", "20"))
        self.label_low.setText(_translate("ConfigPanel", "Low"))
        self.label_high.setText(_translate("ConfigPanel", "High"))
        self.checkBox_trigEmul.setText(_translate("ConfigPanel", "triggers emulation"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ConfigPanel = QtWidgets.QMainWindow()
    ui = Ui_ConfigPanel()
    ui.setupUi(ConfigPanel)
    ConfigPanel.show()
    sys.exit(app.exec_())
