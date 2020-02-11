# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'testpanel.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ConfigPanel(object):
    def setupUi(self, ConfigPanel):
        ConfigPanel.setObjectName("ConfigPanel")
        ConfigPanel.resize(452, 492)
        ConfigPanel.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.centralwidget = QtWidgets.QWidget(ConfigPanel)
        self.centralwidget.setObjectName("centralwidget")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(10, 10, 431, 80))
        self.groupBox.setObjectName("groupBox")
        self.label_host = QtWidgets.QLabel(self.groupBox)
        self.label_host.setGeometry(QtCore.QRect(10, 20, 91, 21))
        self.label_host.setObjectName("label_host")
        self.label_port = QtWidgets.QLabel(self.groupBox)
        self.label_port.setGeometry(QtCore.QRect(10, 50, 91, 21))
        self.label_port.setObjectName("label_port")
        self.line_host = QtWidgets.QLineEdit(self.groupBox)
        self.line_host.setGeometry(QtCore.QRect(110, 20, 311, 20))
        self.line_host.setObjectName("line_host")
        self.lin_port = QtWidgets.QLineEdit(self.groupBox)
        self.lin_port.setGeometry(QtCore.QRect(110, 50, 311, 20))
        self.lin_port.setObjectName("lin_port")
        self.groupBox_2 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_2.setGeometry(QtCore.QRect(10, 100, 431, 301))
        self.groupBox_2.setObjectName("groupBox_2")
        self.tableWidget = QtWidgets.QTableWidget(self.groupBox_2)
        self.tableWidget.setGeometry(QtCore.QRect(10, 20, 411, 271))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(3, item)
        self.button_start = QtWidgets.QPushButton(self.centralwidget)
        self.button_start.setGeometry(QtCore.QRect(330, 410, 111, 31))
        self.button_start.setObjectName("button_start")
        ConfigPanel.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(ConfigPanel)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 452, 21))
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
        self.groupBox.setTitle(_translate("ConfigPanel", "Brainamp configuation"))
        self.label_host.setText(_translate("ConfigPanel", "Host"))
        self.label_port.setText(_translate("ConfigPanel", "Port"))
        self.groupBox_2.setTitle(_translate("ConfigPanel", "Trigger configuration"))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("ConfigPanel", "label"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("ConfigPanel", "left sweep"))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("ConfigPanel", "right sweep"))
        item = self.tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("ConfigPanel", "max stack"))
        self.button_start.setText(_translate("ConfigPanel", "Start"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ConfigPanel = QtWidgets.QMainWindow()
    ui = Ui_ConfigPanel()
    ui.setupUi(ConfigPanel)
    ConfigPanel.show()
    sys.exit(app.exec_())
