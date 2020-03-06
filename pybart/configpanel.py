import json
import logging
import os.path
import time

from PyQt5 import QtCore, QtGui, QtWidgets

from .pipeline.myb.mybpipeline import MybPipeline
from .streamhandler import StreamHandler
from .test_epoch import compare_epoch
from .ui_configpanel import Ui_ConfigPanel


class ConfigPanel(QtWidgets.QMainWindow, Ui_ConfigPanel):
    
    config_file = 'configuration.json'
    pipelines = {
        # 'test' : {'pipe': Pipeline},
        'myb default': {'pipe': MybPipeline}
    }

    logger = logging.getLogger('configpanel')

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)

        # init error dialog        
        self.error_dialog = QtWidgets.QErrorMessage()

        # setup UI
        self.setupUi(self)
        self.connect_ui()

        # load UI
        self.load_configuration()
        self.fill_combo_setup()
        self.simul_file = 'No File Selected'

        # epoch counter
        self.counter_epoch = 0

        # init pipeline
        self.combo_pipeline.addItems(self.pipelines.keys())

    def connect_ui(self):
        """This function connect UI elements to all respective slot"""

        self.button_start.clicked.connect(self.on_start_running)
        self.button_stop.clicked.connect(self.on_stop_running)

        self.add_trig.clicked.connect(self.on_adding_trigger)
        self.del_trig.clicked.connect(self.on_deleting_trigger)

        self.combo_setup.currentIndexChanged.connect(self.on_new_setup)

        self.button_settings.clicked.connect(self.on_settings)

        self.combo_pipeline.currentIndexChanged.connect(self.on_pipeline_selected)
        self.button_settings.setEnabled(True)

        self.button_file_simulated.clicked.connect(self.on_simulation_file)

        self.radio_BVRec.toggled.connect(self.on_select_BVRec)
        self.radio_simulate.toggled.connect(self.on_select_simulate)

        self.button_reset_count.clicked.connect(self.on_reset_count)

    def load_configuration(self):
        """This function read all setup parameter from json configuration file"""

        self.logger.info('Read configuration file({})'.format(self.config_file))
        with open(self.config_file) as params:
            self.triggers_parameters = json.load(params)

    def get_table_params(self):
        """This function return current parameter from de table"""

        params = {}
        row = 0
        t = self.table_trigs_params

        self.logger.info('Convert trigger table')
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
        self.logger.info('Update list of triggers')
        self.combo_setup.clear()
        for setup in self.triggers_parameters.keys():
            self.combo_setup.addItem(setup)

    def on_simulation_file(self):
        self.logger.info('Select file used for simulation')
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

    def on_reset_count(self):
        self.logger.info('Reset trigger counter')
        self.lcd_triggers_count.display(0)
    
    def on_select_simulate(self):
        if self.radio_simulate.isChecked():
            self.frame_select_file.setEnabled(True)
        else:
            self.frame_select_file.setEnabled(False)

    def on_pipeline_selected(self):
        """this function is a slot who switch of pipeline"""
        self.current_pipeline_name = self.combo_pipeline.currentText()
        self.current_pipeline = self.pipelines[self.current_pipeline_name]['pipe'](self)

    def on_start_running(self):
        """This function is a slot who collect parameter from the
        control panel and initialise the pyacq web(StreamHandler)

        """
        self.logger.info('Run pipeline')
        try:
            self.logger.info('Set high({}) and low({}) frequency'.format(self.line_high_freq.text(),self.line_low_freq.text()))

            # get the low and high frequency in float
            low_frequency = float(self.line_low_freq.text())
            high_frequency = float(self.line_high_freq.text())
        except ValueError:
            self.error_dialog.showMessage(
                "High and low frequency has to be float type.")
            return

        if not 0 < low_frequency or not low_frequency < high_frequency :
                self.error_dialog.showMessage("Wrong frequency.")
                return

        host = str(self.line_host.text())
        try:
            self.logger.info('Set BrainVision port({})'.format(self.line_port.text()))
            # get the port number in int
            port = int(self.line_port.text())
        except ValueError:
            # TODO popup message
            self.error_dialog.showMessage("The port has to be int type.")
            return

        try:
            self.logger.info('Set trigger parameters')

            # get parameter of the table
            params = self.get_table_params()
        except ValueError as e:
            self.error_dialog.showMessage("{}".format(e))
            return
        

        # setup parmeter in the stream handler
        if self.radio_BVRec.isChecked():
            self.logger.info('Init StreamHandler in BrainVision mode')
            self.sh = StreamHandler(brainamp_host=host, brainamp_port=port)
        else:
            self.logger.info('Init StreamHandler in simulate mode')
            self.sh = StreamHandler(None, None, simulated=True, raw_file=self.simul_file)

        try:
            self.logger.info('Configure Stream Handler')
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
        self.sh.nodes['epochermultilabel'].new_chunk.connect(self.on_new_epochs)

        self.logger.info('Start the stream handler')
        # start the stream handler
        self.sh.start_node()

        self.button_stop.setEnabled(True)
        self.button_start.setEnabled(False)

    def on_stop_running(self):
        """This function is a slot who stop pyacq all pyacq node"""
        self.logger.info('Stop pipeline')
        self.sh.stop_node()

        self.button_stop.setEnabled(False)
        self.button_start.setEnabled(True)

        self.lcd_triggers_count.display(0)

        self.counter_epoch = 0

    def on_new_setup(self):
        """This function is a slot waiting for an index change
        from the comboBox.
        -delete all row
        -adding parameter according to the json configuration file

        """
        self.logger.info('Modify trigger setup')
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


    def on_settings(self):
        """This function is a slot who open a open file window
        and set the name of the file selected in the label

        """
        self.logger.info('Open pipeline Setting')

        self.current_pipeline.setting()
        
    def on_new_epochs(self, label, epochs):
        """This function is a slot who receive a stack of epochs
        
        This is the most important part of the class.
        Each stack of epoch build by the StreamHandler 
        arrives here with his label.

        """
        # TEST Visualize epoch compare to mne
        # print(self.counter_epoch)
        # if self.counter_epoch == 0:
        #     self.sh.nodes['epochermultilabel'].new_chunk.disconnect()
        #     epoch = epochs.reshape((epochs.shape[1], epochs.shape[2]))
            
        #     print(epoch.shape)
        #     compare_epoch(epoch, self.counter_epoch)    
        
        # send epoch(s) and is label to the current pipeline
        self.current_pipeline.new_epochs(label, epochs)
        
        # display count of triggers
        self.counter_epoch += 1
        self.lcd_triggers_count.display(self.counter_epoch)
        

    # TODO set icon add modify method
    def on_adding_trigger(self):
        self.table_trigs_params.insertRow(0)

    # TODO set icon add modify method
    def on_deleting_trigger(self):
        self.table_trigs_params.removeRow(0)

if __name__ == "__main__":
    import sys
    
    app = QtWidgets.QApplication(sys.argv)
    ui = ConfigPanel()
    ui.show()
    sys.exit(app.exec_())
