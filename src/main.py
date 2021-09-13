from PySide2 import QtWidgets, QtCore
import datetime
import traceback
import threading
import random
import sys, math, time
import pathlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure
from matplotlib import transforms
from matplotlib.mlab import psd
from collections import deque

import signal
# handle potential SIGINT from Ctrl+C
signal.signal(signal.SIGINT, signal.SIG_DFL)

def get_newest_file(data_dir):
    try:
        return sorted(pathlib.Path(data_dir).glob('1*.txt'))[-2]
    except IndexError:
        # no files in directory
        return None
#
#   This method pull n channel data from file and returns list of floats
#
def get_single_channel_data(selected_channel, filename):
    data = []
    with open(filename, 'r') as f:
        start = time.time()
        for i, line in enumerate(f.readlines()):
            if time.time()-start >= 1:
                start = time.time()
            channel_data = line.split(',')
            data.append(float(channel_data[selected_channel]))
    return(data)


class SyncedPlots(QtWidgets.QWidget):
    """docstring for SyncedPlots"""
    def __init__(self, widgets, data_dir, t_series_widget, apptick_hz=1, debug=False):
        super(SyncedPlots, self).__init__()
        self.widgets = widgets
        self.data_dir = data_dir
        self.t_series_widget = t_series_widget

        self.layout_h = QtWidgets.QHBoxLayout()
        for widget in self.widgets:
            self.layout_h.addWidget(widget)

        self.setLayout(self.layout_h)

        self.layout_v = QtWidgets.QVBoxLayout()
        self.layout_v.stretch(1)
        self.layout_v.addWidget(self.t_series_widget)

        self.setLayout(self.layout_v)

        self.apptick_hz = apptick_hz
        self.debug = debug

        self.timer = QtCore.QTimer()
        self.apptick_hz = apptick_hz
        self.timer.setInterval((1 / self.apptick_hz) * 1000)
        self.timer.timeout.connect(self.update)
        self.timer.start()

    def update(self):
        current_file = get_newest_file(self.data_dir)
        if current_file:
            for widget in self.widgets:
                widget.update(current_file=current_file)
            self.t_series_widget.update(current_file=current_file)
        else:
            if self.debug: print('No files in data directory....')

class RTPlot(QtWidgets.QWidget):
    """docstring for RTPlot"""
    def __init__(self, nrows=1, ncols=1, apptick_hz=1):
        super().__init__()
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.nrows = nrows
        self.ncols = ncols
        self._init_plot()
        self.setLayout(self.layout)

    def _init_plot(self):
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        self.layout.addWidget(self.canvas)

        self.gs = self.figure.add_gridspec(nrows=self.nrows, ncols=self.ncols)
        self.axes = [[]]

        for col in range(self.ncols):
            for row in range(self.nrows):
                # print(row, col)
                try:
                    self.axes[col].append(self.figure.add_subplot(self.gs[row, col]))
                except IndexError:
                    traceback.print_exc()

        self.ax = self.axes[0][0]

    def clear_axes(self):
        for col in range(self.ncols):
            for row in range(self.nrows):
                self.axes[col][row].clear()

    def get_data(self):
        return [random.random() for i in range(200)]

    def update_axes(self):
        data = self.get_data()

        if data:
            self.ax.clear()
            self.ax.plot(data, '*-')
            # refresh canvas
            self.canvas.draw()

    def update(self, *args, **kwargs):
        self.update_axes(*args, **kwargs)


class MultiChannelVoltageTSeriesPlot(RTPlot):
    """docstring for MultiChannelVoltageTSeriesPlot"""
    def __init__(self, channels, num_samples, nrows=1, ncols=1):
        super(MultiChannelVoltageTSeriesPlot, self).__init__(nrows=nrows, ncols=ncols)
        self.channels = channels
        self.num_samples = num_samples
        self.title = 'Voltage Timeseries for channels: {}'.format(*channels)
        
        # create t_series axis
        self.axMultiTSeries = self.ax

    def get_data(self, current_file):
        data = []
        for i in self.channels:
            data.append(list(get_single_channel_data(filename=current_file, selected_channel=i)[:self.num_samples]))
        return data

    def update_axes(self, current_file):
        data = self.get_data(current_file)

        if data:
            self.clear_axes()
            self.axMultiTSeries.set_title(self.title)

            for ch, t_series in zip(self.channels, data):
                # print(ch, t_series[:5])
                # channel, t_series of first n samples (defined by num_samples)
                self.axMultiTSeries.plot([1.1, 2.2, 3.3])#t_series, label='Channel {}'.format(ch))
            
            # refresh canvas
            self.canvas.draw()


class SingleChannelPlot(RTPlot):
    """docstring for SingleChannelPlot"""
    def __init__(self, title='', channel=0, fs=100000, nfft=1024, duration=1):
        super(SingleChannelPlot, self).__init__(nrows=3, ncols=1)
        self.channel = channel
        if title != '':
            self.title = title
        else:
            self.title = 'Channel {}'.format(self.channel)

        self.fs = fs
        self.nfft = nfft
        self.duration = duration

        # create attrs for each axes
        self.axSpec = self.axes[0][0]
        self.axPSD = self.axes[0][1]
        self.axVT = self.axes[0][2]
    
    def get_data(self, current_file):
        # returns 1D vector of the voltage timeseries for a specific channel
        return get_single_channel_data(filename=current_file, selected_channel=self.channel)

    def update_axes(self, current_file):
        data = self.get_data(current_file)

        if data:
            self.clear_axes()
            self.ax.set_title(self.title)

            Pxx, freqs, bins, im = self.axSpec.specgram(data, NFFT=self.nfft, Fs=self.fs)
            self.axPSD.psd(Pxx, self.nfft, self.fs)
            self.axVT.plot(data)
            # refresh canvas
            self.canvas.draw()


def main(app):
    return app.exec_()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="AQUABAT RT Display")
    parser.add_argument('-t', '--apptick', help='Apptick/Display update rate in Hz', required=False, type=float, default=10)
    parser.add_argument('--data-directory', help='Directory where csv data from DAQ buffer is stored', default='./', required=False)
    parser.add_argument('-c', '--channels', help='Number of channels to display', default=2, required=False, type=int)
    parser.add_argument('--t-series-samples', help='Number of values to overlap in voltage time series (first N samples)', default=1000, required=False, type=int)
    parser.add_argument('-fs', '--sample-rate', help='Sample rate in Hz', default=100000, required=False, type=int)
    parser.add_argument('--nfft', help='NFFT', default=1024, required=False, type=int)
    parser.add_argument('-d', '--debug', action="store_true", help="Print debug messages")
    parser.add_argument('-f', '--fullscreen', action="store_true", help="Print debug messages")
    args = parser.parse_args()

    app = QtWidgets.QApplication([parser.description])

    # create main window widget
    main_window = QtWidgets.QWidget()

    # if fullscreen
    if args.fullscreen:
        geometry = app.desktop().availableGeometry()
        main_window.setGeometry(geometry)

    # create layout for SyncedPlots widget and add all created SingleChannelPlot widgets to it
    layout = QtWidgets.QHBoxLayout()
    plot_widgets = []
    for i in range(args.channels):
        plot_widgets.append(SingleChannelPlot(channel=i, fs=args.fs, nfft=args.nfft))

    # add SyncedPlots widget to main window
    layout.addWidget(SyncedPlots(widgets=plot_widgets, 
                                 data_dir=args.data_directory,
                                 debug=args.debug,
                                 t_series_widget=MultiChannelVoltageTSeriesPlot(channels=list(range(args.channels - 1)),
                                                                                num_samples=args.t_series_samples)))

    main_window.setLayout(layout)
    main_window.show()
    rc = 0
    try:
        rc = main(app)
    except KeyboardInterrupt:
        pass
    finally:
        print('\n\tExiting...\n\n')
        sys.exit(rc)