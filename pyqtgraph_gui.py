from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys
import numpy as np
import math
from pyqtgraph.Qt import QtGui, QtCore
import datetime;
import time
import os
import pandas as pd
import timeaxis as ta

path = '';

# DESCRIPTION OF GUI FUNCTIONS AND WINDOWS
class Help(QtGui.QMainWindow):

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
        uic.loadUi('main_window_pyqt.ui', self)        # Design file

        # Connection of different action to different Menus and Buttons
        self.actionFile.triggered.connect(self.exit)
        self.actionOpen.triggered.connect(self.open_dialog)
        #self.pushSave.clicked.connect(self.save_dialog)
        self.actionAbout.triggered.connect(self.help_window)

    # New windows for help
    def help_window(self):

        self.dialog = Help(self)
        self.dialog.show()

    # Data plotting
    def plot(self, dataX, dataY, dataY2):
        global p1, p2

        axis = ta.DateAxisItem(orientation = 'bottom')
        axis.attachToPlotItem(self.graphicsView.getPlotItem())
        
        p1 = self.graphicsView.plotItem
        p1.setLabels(left = 'Pressure (psi)')
        p1.showGrid(x=True, y=False) # Grid        
        p2 = pg.ViewBox()
        p1.showAxis('right')
        p1.scene().addItem(p2)
        p1.getAxis('right').linkToView(p2)
        p2.setXLink(p1)
        p1.getAxis('left').setLabel('Pressure (psi)', color='#ffff00')
        p1.getAxis('right').setLabel('Heater (W)', color='#0000ff')


        self.updateViews()
        p1.vb.sigResized.connect(self.updateViews)

        pen = pg.mkPen(color = (255, 255, 0, 200), width = 2) # pen for plotting slightly transparent yellow line; the last argument is opacity; 255 - no transparancy; 0 - full transparancy
        pen2 = pg.mkPen(color = (0, 0, 255, 200), width = 2) # pen for plotting slightly transparent yellow line; the last argument is opacity; 255 - no transparancy; 0 - full transparancy
        p1.plot(x = dataX, y = dataY , pen = pen)
        p2.addItem(pg.PlotCurveItem(x = dataX, y = dataY2 , pen = pen2))
        p1.setXRange(dataX[-600], dataX[-1]) # x axis range

    ## Handle view resizing 
    def updateViews(self):
        global p1, p2
        ## view has resized; update auxiliary views to match
        p2.setGeometry(p1.vb.sceneBoundingRect())
    
        ## need to re-update linked axes since this was called
        ## incorrectly while views had different shapes.
        ## (probably this should be handled in ViewBox.resizeEvent)
        p2.linkedViewChanged(p1.vb, p2.XAxis)

    def plot_2(self, dataX, dataY, dataY2):
        global p3, p4

        axis = ta.DateAxisItem(orientation = 'bottom')
        axis.attachToPlotItem(self.graphicsView_2.getPlotItem())

        p3 = self.graphicsView_2.plotItem
        p3.setLabels(left = 'Pressure (psi)')        
        p4 = pg.ViewBox()
        p3.showAxis('right')
        p3.scene().addItem(p4)
        p3.getAxis('right').linkToView(p4)
        p4.setXLink(p3)
        p3.getAxis('left').setLabel('Temparature In (Deg)', color='#ffff00')
        p3.getAxis('right').setLabel('Temparature Out (Deg)', color='#0000ff')
        p3.showGrid(x=True, y=False) # Grid

        self.updateViews_2()
        p3.vb.sigResized.connect(self.updateViews_2)

        pen = pg.mkPen(color = (255, 255, 0, 200), width = 2) # pen for plotting slightly transparent yellow line; the last argument is opacity; 255 - no transparancy; 0 - full transparancy
        pen2 = pg.mkPen(color = (0, 0, 255, 200), width = 2) # pen for plotting slightly transparent yellow line; the last argument is opacity; 255 - no transparancy; 0 - full transparancy
        p3.plot(x = dataX, y = dataY , pen = pen)
        p4.addItem(pg.PlotCurveItem(x = dataX, y = dataY2 , pen = pen2))
        p3.setXRange(dataX[-600], dataX[-1]) # x axis range

    ## Handle view resizing 
    def updateViews_2(self):
        global p3, p4
        ## view has resized; update auxiliary views to match
        p4.setGeometry(p3.vb.sceneBoundingRect())
        p4.linkedViewChanged(p3.vb, p4.XAxis)

    # Function for Open File
    def file_open(self, filename):
        global path
        
        dataframe = pd.read_csv(filename, sep="\t", header=None)
        dataframe[6] = dataframe[6].replace("< 1", 0.1).astype(np.float64)
        datanumpy = dataframe.to_numpy()
        #print(datanumpy[:,2])		# get 2nd column

        #date columns       
        date = pd.DatetimeIndex(dataframe[0] + " " + dataframe[1])
        date = pd.DataFrame(index = date).reset_index().rename(columns={'index':'datetime'})
        date['ts'] = date.datetime.values.astype(np.int64) // 10 ** 9   # convert to timestamp
        timestamps = date['ts'].to_numpy() # to numpy

        self.plot(timestamps, datanumpy[:,2], datanumpy[:,3])
        self.plot_2(timestamps, datanumpy[:,9], datanumpy[:,10])
        path = os.path.dirname(filename) # for memorizing the path to the last used folder

    def open_dialog(self):
        global path

        if path == '':
            path = "/home/anatoly/Documents"

        filedialog = QFileDialog(self, 'Open Log File', directory = path, filter ="text (*.txt *.csv *.dat)", options = QFileDialog.DontUseNativeDialog) # use QFileDialog.DontUseNativeDialog to change directory
        filedialog.setStyleSheet("QWidget { background-color : rgb(136, 138, 133) }")  # change background color of the open file window
        filedialog.setFileMode(QtGui.QFileDialog.AnyFile)

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