from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtWidgets import QDialog, QApplication, QPushButton, QVBoxLayout
import sys
import numpy as np
import math
import datetime
import time
import os
import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

path = '';

# DESCRIPTION OF GUI FUNCTIONS AND WINDOWS
class Help(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super(Help, self).__init__(parent)

        uic.loadUi('help.ui', self)   # QtDesigner file with design
        self.actionQuit.triggered.connect(self.close_2)

    # Description of functions
    def close_2(self):
        self.close()

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.destroyed.connect(MainWindow.on_destroyed)         # connect some actions to exit

        # Load the UI Page
        uic.loadUi('main_window.ui', self)        # Design file

        # Connection of different action to different Menus and Buttons
        self.actionFile.triggered.connect(self.exit)
        self.actionOpen.triggered.connect(self.open_dialog)
        #self.pushSave.clicked.connect(self.save_dialog)
        self.actionAbout.triggered.connect(self.help_window)

    # Matplotlib plot
    def add_figure_matplotlib(self, fig):
        self.canvas = FigureCanvas(fig)
        # there is a trick with vertical layout
        ###

        self.mpl_layout.addWidget(self.canvas)
        self.canvas.draw()
        self.toolbar = NavigationToolbar(self.canvas, self.mplwindow, coordinates=True)
        self.mpl_layout.addWidget(self.toolbar)

    # New windows for help
    def help_window(self):

        self.dialog = Help(self)
        self.dialog.show()

    # Data plotting
    def plot(self, dataX, dataFrame):

        fig, ax1 = plt.subplots(2,1, sharex=True)
        fig.autofmt_xdate()
        #xfmt = mdates.DateFormatter('%d-%Hh')                                                             # special thing for reformat date; use only hours and minutes
        fig.subplots_adjust(top=0.99, left=0.10, right=0.99, bottom=0.145, hspace=0.0, wspace=0.19)         # spacers for subplots 0.28

        #ax1[0].clear()
        #ax1[1].clear()

        text_pressure = ("Current Pressure [psi]: " + str(dataFrame[2].iloc[-1]))
        text_level = ("Current Heater Power [W]: " + str(dataFrame[3].iloc[-1]))

        ax1[0].plot(dataX[-600:], dataFrame[2][-600:],color="red", alpha=1,label="Pressure")
        ax1[1].plot(dataX[-600:], dataFrame[3][-600:], color="red",alpha=1,label="Heater Power")

        min_p = min(dataFrame[2][-600:])
        max_p = max(dataFrame[2][-600:])
        #ax1[0].text(0.7285, 0.96, text_pressure, transform = ax1[0].transAxes, fontsize=16, fontweight='bold',verticalalignment='top')
        ax1[0].set_xlabel('Date (Auto Format)',weight="bold", fontsize=16)
        ax1[0].tick_params(labelsize=13)
        ax1[0].set_ylabel('Pressure (Psi)',weight="bold", fontsize=16)
        ax1[0].set_ylim(min_p-max_p*0.17, max_p*1.18)
        ax1[0].grid(True,linestyle='--', linewidth=0.4)  
        ax1[0].legend(bbox_to_anchor=(0.01, 0.86, 1., .102), prop=dict(weight='bold',size=15), loc='lower left', ncol=2, borderaxespad=0.) # mode="expand"
        #ax1[0].xaxis.set_major_formatter(xfmt)
        #show all date as coordinate
        ax1[0].fmt_xdata = mdates.DateFormatter('%Y-%m-%d-%H-%M-%s')

        min_h = min(dataFrame[3][-600:])
        max_h = max(dataFrame[3][-600:])   
        #ax1[1].text(0.73, 0.96, text_level, transform = ax1[1].transAxes, fontsize=16, fontweight='bold',verticalalignment='top')
        ax1[1].set_xlabel('Date (Auto Format)',weight="bold", fontsize=16)
        ax1[1].set_ylabel('Heater Power (W)',weight="bold", fontsize=16)
        ax1[1].tick_params(labelsize=13)
        ax1[1].set_ylim(min_h-max_h*0.17, max_h*1.18)
        ax1[1].grid(True,linestyle='--', linewidth=0.4)  
        ax1[1].legend(bbox_to_anchor=(0.01, 0.86, 1., .102), prop=dict(weight='bold',size=15), loc='lower left', ncol=2, borderaxespad=0.)

        ax1[0].fill_between(dataX[-600:], -0.35, dataFrame[2][-600:], where=dataFrame[7][-600:].to_numpy()=="Running", facecolor="green", alpha=0.15)
        ax1[1].fill_between(dataX[-600:], -0.2, dataFrame[3][-600:], where=dataFrame[7][-600:].to_numpy()=="Running", facecolor="green", alpha=0.15)
        #ax1[1].xaxis.set_major_formatter(xfmt)
        #show all date as coordinate
        ax1[1].fmt_xdata = mdates.DateFormatter('%Y-%m-%d-%H-%M-%s')

        fig.align_labels()
        self.add_figure_matplotlib(fig)



    # Function for Open File
    def file_open(self, filename):
        global path
        
        dataframe = pd.read_csv(filename, sep="\t", header=None)
        dataframe[6] = dataframe[6].replace("< 1", 0.1).astype(np.float64)
        #print(datanumpy[:,2])		# get 2nd column
        #date columns       
        date = pd.DatetimeIndex(dataframe[0] + " " + dataframe[1])
        self.plot(date, dataframe)

        #self.plot(timestamps, datanumpy[:,2])
        path = os.path.dirname(filename) # for memorizing the path to the last used folder


    def open_dialog(self):
        global path

        if path == '':
            path = "/home/anatoly/Documents"

        filedialog = QFileDialog(self, 'Open Log File', directory = path, filter ="text (*.txt *.csv *.dat)", options = QFileDialog.DontUseNativeDialog) # use QFileDialog.DontUseNativeDialog to change directory
        filedialog.setStyleSheet("QWidget { background-color : rgb(136, 138, 133) }")  # change background color of the open file window
        filedialog.setFileMode(QtWidgets.QFileDialog.AnyFile)

        filedialog.fileSelected.connect(self.file_open)
        filedialog.show()

    # function for destroying the main window
    def on_destroyed():
    	pass

    def exit(self):
        sys.exit()


# Running of the main window
def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())

if __name__ == '__main__':         
    main()