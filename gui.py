"""
This module contains class responsible for display graphical interface, thread handler class and
function run in new thread
"""

from PyQt5 import QtCore, QtWidgets, QtGui
from processing import CustomWidget, AveragingWidget
from processing import data_loop
from pathlib import Path
import threading
import time
import sys


class Ui_MainWindow(QtWidgets.QDialog):
    """
    This class is responsible for displaying GUI
    """

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1400, 800)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.widget = CustomWidget(self.centralwidget)
        self.widget.setGeometry(QtCore.QRect(700, 200, 680, 380))
        self.widget.setObjectName("widget")
        self.averaging_widget = AveragingWidget(self.centralwidget)
        self.averaging_widget.setGeometry(QtCore.QRect(50, 200, 400, 380))
        self.averaging_widget.setObjectName("averagingwidget")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        MainWindow.setStatusBar(self.statusbar)
        self.buttonN = QtWidgets.QPushButton(self.centralwidget)
        self.buttonN.setGeometry(QtCore.QRect(1000, 100, 150, 50))
        self.buttonA = QtWidgets.QPushButton(self.centralwidget)
        self.buttonA.setGeometry(QtCore.QRect(1200, 100, 150, 50))
        self.start = QtWidgets.QPushButton(self.centralwidget)
        self.start.setGeometry(QtCore.QRect(1000, 20, 150, 50))
        self.stop = QtWidgets.QPushButton(self.centralwidget)
        self.stop.setGeometry(QtCore.QRect(1200, 20, 150, 50))
        self.pathButton = QtWidgets.QPushButton(self.centralwidget)
        self.pathButton.setGeometry(QtCore.QRect(800, 20, 150, 50))
        self.error_dialog = QtWidgets.QErrorMessage()
        self.main_label = QtWidgets.QLabel(self.centralwidget)
        self.main_label.setGeometry(100, 20, 400, 100)
        self.main_label.setText("ECG Processing")
        self.main_label.setFont(QtGui.QFont('Arial', 25))
        self.signal_label = QtWidgets.QLabel(self.centralwidget)
        self.signal_label.setGeometry(550, 250, 100, 50)
        self.signal_label.setText("Raw signal: ")
        self.signal_label.setFont(QtGui.QFont('Arial', 10))
        self.moving_average_label = QtWidgets.QLabel(self.centralwidget)
        self.moving_average_label.setGeometry(550, 360, 100, 50)
        self.moving_average_label.setText("Moving average: ")
        self.moving_average_label.setFont(QtGui.QFont('Arial', 10))
        self.isonotch_label = QtWidgets.QLabel(self.centralwidget)
        self.isonotch_label.setGeometry(550, 475, 100, 50)
        self.isonotch_label.setText("Notch filter: ")
        self.isonotch_label.setFont(QtGui.QFont('Arial', 10))
        self.averaging_label = QtWidgets.QLabel(self.centralwidget)
        self.averaging_label.setGeometry(150, 600, 200, 50)
        self.averaging_label.setText("Removing EMG noise")
        self.averaging_label.setFont(QtGui.QFont('Arial', 15))
        self.N = 7
        self.A = 0.88
        self.N_input_done = False
        self.A_input_done = False
        self.start_program = False
        self.stop_program = False
        self.default_path = '200_bpm_emg_noise_50_percent.txt'
        self.retranslateUi(MainWindow)

    def take_input_n(self):
        parameter, done = QtWidgets.QInputDialog.getInt(
            self, 'Input Dialog', 'Enter parameter N:')
        if done:
            if parameter > 1 and parameter <= 10:
                self.N = parameter
            else:
                self.error_dialog.showMessage("Parameter must be greater than 1 and lower or equal 10")
                self.N = 7
            self.N_input_done = True

    def take_input_a(self):
        parameter, done = QtWidgets.QInputDialog.getDouble(
            self, 'Input Dialog', 'Enter parameter A:')
        if done:
            if parameter > 0 and parameter < 1:
                self.A = parameter
            else:
                self.error_dialog.showMessage("Parameter must be greater than 0 and lower than 1")
                self.A = 0.88
            self.A_input_done = True

    def take_input_path(self):
        parameter, done = QtWidgets.QInputDialog.getText(
            self, 'Input Dialog', 'Enter path to file:')
        if done:
            path = Path(parameter)
            if path.is_file():
                self.default_path = parameter
            else:
                self.error_dialog.showMessage("Enter correct path, now path is set on default file")

    def start_func(self):
        self.start_program = True
        time.sleep(0.1)
        self.widget.start_plotting()
        self.averaging_widget.start_plotting()

    def stop_func(self):
        self.stop_program = True
        self.widget.stop_plotting()
        self.averaging_widget.stop_plotting()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "ECG Processing"))
        MainWindow.setStyleSheet("background-color: white;")
        MainWindow.setFixedSize(1400, 800)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.buttonN.setText(_translate("MainWindow", "Enter parameter N"))
        self.buttonN.clicked.connect(self.take_input_n)
        self.buttonA.setText(_translate("MainWindow", "Enter parameter A"))
        self.buttonA.clicked.connect(self.take_input_a)
        self.start.setText(_translate("MainWindow", "Start"))
        self.start.clicked.connect(self.start_func)
        self.stop.setText(_translate("MainWindow", "Stop"))
        self.stop.clicked.connect(self.stop_func)
        self.pathButton.setText(_translate("MainWindow", "File path"))
        self.pathButton.clicked.connect(self.take_input_path)


class GUIThreadClass(QtWidgets.QMainWindow):
    """
    This class is a thread handler class
    """

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.my_thread = threading.current_thread()
        self.stop_thread = False

    def closeEvent(self, event):
        self.stop_thread = True
        self.my_thread.do_run = False
        try:
            self.my_thread.join()
        except RuntimeError:
            pass
        event.accept()


def data_from_gui(gui_class: Ui_MainWindow, data_loop, gui_thread: GUIThreadClass):
    """
    This function is running in new thread
    :param gui_class: instance of GUI class
    :param data_loop: processing data function
    :param gui_thread: instance of thread handler class
    """
    parameter_list = [7, 0.88]
    while getattr(gui_thread.my_thread, "do_run", True):
        if gui_class.N_input_done:
            parameter_list[0] = gui_class.N
            gui_class.N_input_done = False
        if gui_class.A_input_done:
            parameter_list[1] = gui_class.A
            gui_class.A_input_done = False
        if gui_class.start_program:
            data_loop(parameter_list, gui_class, gui_thread)
            gui_class.start_program = False
        if gui_class.stop_program:
            time.sleep(0.1)
            gui_class.stop_program = False


if __name__ == "__main__":
    parameter_lst = []
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = GUIThreadClass()
    ui_window = Ui_MainWindow()
    ui_window.setupUi(MainWindow)
    threading.Thread(target=data_from_gui,
                     args=(ui_window, data_loop, MainWindow)).start()
    MainWindow.show()
    sys.exit(app.exec_())
