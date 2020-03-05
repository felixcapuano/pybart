# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pybart\pipeline\myb\ui_mybsettingdialog.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MybSettingDialog(object):
    def setupUi(self, MybSettingDialog):
        MybSettingDialog.setObjectName("MybSettingDialog")
        MybSettingDialog.setWindowModality(QtCore.Qt.WindowModal)
        MybSettingDialog.resize(524, 336)
        MybSettingDialog.setAcceptDrops(False)
        self.groupBox_template = QtWidgets.QGroupBox(MybSettingDialog)
        self.groupBox_template.setGeometry(QtCore.QRect(20, 260, 481, 61))
        self.groupBox_template.setObjectName("groupBox_template")
        self.frame_select_template = QtWidgets.QFrame(self.groupBox_template)
        self.frame_select_template.setEnabled(True)
        self.frame_select_template.setGeometry(QtCore.QRect(10, 20, 461, 21))
        self.frame_select_template.setFrameShape(QtWidgets.QFrame.Panel)
        self.frame_select_template.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_select_template.setObjectName("frame_select_template")
        self.button_file_template = QtWidgets.QPushButton(self.frame_select_template)
        self.button_file_template.setGeometry(QtCore.QRect(0, 0, 75, 21))
        self.button_file_template.setObjectName("button_file_template")
        self.label_filename_template = QtWidgets.QLabel(self.frame_select_template)
        self.label_filename_template.setGeometry(QtCore.QRect(80, 0, 371, 21))
        self.label_filename_template.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.label_filename_template.setFrameShadow(QtWidgets.QFrame.Plain)
        self.label_filename_template.setObjectName("label_filename_template")
        self.groupBox_calibration = QtWidgets.QGroupBox(MybSettingDialog)
        self.groupBox_calibration.setGeometry(QtCore.QRect(20, 80, 481, 171))
        self.groupBox_calibration.setObjectName("groupBox_calibration")
        self.frame_select_calibration = QtWidgets.QFrame(self.groupBox_calibration)
        self.frame_select_calibration.setEnabled(True)
        self.frame_select_calibration.setGeometry(QtCore.QRect(10, 20, 461, 21))
        self.frame_select_calibration.setFrameShape(QtWidgets.QFrame.Panel)
        self.frame_select_calibration.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_select_calibration.setObjectName("frame_select_calibration")
        self.button_file_calibration = QtWidgets.QPushButton(self.frame_select_calibration)
        self.button_file_calibration.setGeometry(QtCore.QRect(0, 0, 75, 21))
        self.button_file_calibration.setObjectName("button_file_calibration")
        self.label_filename_calibration = QtWidgets.QLabel(self.frame_select_calibration)
        self.label_filename_calibration.setGeometry(QtCore.QRect(80, 0, 301, 21))
        self.label_filename_calibration.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.label_filename_calibration.setFrameShadow(QtWidgets.QFrame.Plain)
        self.label_filename_calibration.setObjectName("label_filename_calibration")
        self.button_run_calibration = QtWidgets.QPushButton(self.groupBox_calibration)
        self.button_run_calibration.setGeometry(QtCore.QRect(344, 130, 121, 23))
        self.button_run_calibration.setObjectName("button_run_calibration")
        self.progressBar_calibration = QtWidgets.QProgressBar(self.groupBox_calibration)
        self.progressBar_calibration.setGeometry(QtCore.QRect(20, 130, 311, 23))
        self.progressBar_calibration.setProperty("value", 0)
        self.progressBar_calibration.setObjectName("progressBar_calibration")
        self.line_low_freq = QtWidgets.QLineEdit(self.groupBox_calibration)
        self.line_low_freq.setGeometry(QtCore.QRect(150, 60, 61, 21))
        self.line_low_freq.setText("")
        self.line_low_freq.setObjectName("line_low_freq")
        self.line_high_freq = QtWidgets.QLineEdit(self.groupBox_calibration)
        self.line_high_freq.setGeometry(QtCore.QRect(150, 90, 61, 21))
        self.line_high_freq.setText("")
        self.line_high_freq.setObjectName("line_high_freq")
        self.label_high_freq = QtWidgets.QLabel(self.groupBox_calibration)
        self.label_high_freq.setGeometry(QtCore.QRect(40, 90, 81, 21))
        self.label_high_freq.setObjectName("label_high_freq")
        self.label_low_freq = QtWidgets.QLabel(self.groupBox_calibration)
        self.label_low_freq.setGeometry(QtCore.QRect(40, 60, 81, 21))
        self.label_low_freq.setObjectName("label_low_freq")
        self.label_low_rate = QtWidgets.QLabel(self.groupBox_calibration)
        self.label_low_rate.setGeometry(QtCore.QRect(250, 60, 101, 21))
        self.label_low_rate.setObjectName("label_low_rate")
        self.line_rejection_rate = QtWidgets.QLineEdit(self.groupBox_calibration)
        self.line_rejection_rate.setGeometry(QtCore.QRect(360, 60, 61, 20))
        self.line_rejection_rate.setText("")
        self.line_rejection_rate.setObjectName("line_rejection_rate")
        self.label_3 = QtWidgets.QLabel(MybSettingDialog)
        self.label_3.setGeometry(QtCore.QRect(410, 10, 71, 71))
        self.label_3.setText("")
        self.label_3.setPixmap(QtGui.QPixmap("pybart\\pipeline\\myb\\../../../resources/MYB_logo.PNG"))
        self.label_3.setScaledContents(True)
        self.label_3.setObjectName("label_3")

        self.retranslateUi(MybSettingDialog)
        QtCore.QMetaObject.connectSlotsByName(MybSettingDialog)

    def retranslateUi(self, MybSettingDialog):
        _translate = QtCore.QCoreApplication.translate
        MybSettingDialog.setWindowTitle(_translate("MybSettingDialog", "MYB Setting"))
        self.groupBox_template.setTitle(_translate("MybSettingDialog", "Select Template"))
        self.button_file_template.setText(_translate("MybSettingDialog", "Select File"))
        self.label_filename_template.setText(_translate("MybSettingDialog", "No File Selected"))
        self.groupBox_calibration.setTitle(_translate("MybSettingDialog", "Calibration"))
        self.button_file_calibration.setText(_translate("MybSettingDialog", "Select File"))
        self.label_filename_calibration.setText(_translate("MybSettingDialog", "No File Selected"))
        self.button_run_calibration.setText(_translate("MybSettingDialog", "Run calibration"))
        self.label_high_freq.setText(_translate("MybSettingDialog", "High frequency"))
        self.label_low_freq.setText(_translate("MybSettingDialog", "Low frequency"))
        self.label_low_rate.setText(_translate("MybSettingDialog", "Rejection rate"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MybSettingDialog = QtWidgets.QDialog()
    ui = Ui_MybSettingDialog()
    ui.setupUi(MybSettingDialog)
    MybSettingDialog.show()
    sys.exit(app.exec_())
