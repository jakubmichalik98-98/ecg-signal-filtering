"""
This module contains classes and function responsible for processing and plot data
"""

import time
from copy import deepcopy
from typing import List

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore


class CustomWidget(pg.GraphicsWindow):
    """
    This class is responsible for plot three real time plots
    """

    pg.setConfigOption('background', 'w')
    pg.setConfigOption('foreground', 'k')
    ptr1 = 0

    def __init__(self, parent=None, **kwargs):
        pg.GraphicsWindow.__init__(self, **kwargs)
        self.setParent(parent)
        self.setWindowTitle('pyqtgraph example: Scrolling Plots')
        self.x = list(range(-500, 0))
        self.y = [0 for _ in range(500)]
        self.y2 = [0 for _ in range(500)]
        self.y3 = [0 for _ in range(500)]
        self.update_x = 0
        self.sample = 0
        self.isonotch = 0
        self.moving_average = 0

        self.p1 = self.addPlot(row=0, col=0)
        self.p2 = self.addPlot(row=1, col=0)
        self.p3 = self.addPlot(row=2, col=0)

        pen = pg.mkPen(color=(255, 0, 0))

        self.data_line = self.p1.plot(self.x, self.y, pen=pen)
        self.second_data_line = self.p2.plot(self.x, self.y2, pen=pen)
        self.third_data_line = self.p3.plot(self.x, self.y3, pen=pen)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(4)
        self.timer.timeout.connect(self.update)

    def start_plotting(self):
        self.timer.start()

    def stop_plotting(self):
        self.x = list(range(-500, 0))
        self.y = [0 for _ in range(500)]
        self.y2 = [0 for _ in range(500)]
        self.y3 = [0 for _ in range(500)]
        self.moving_average = 0
        self.sample = 0
        self.isonotch = 0
        self.timer.stop()

    def update(self):
        self.x = self.x[1:]
        self.x.append(self.update_x)
        self.y = self.y[1:]
        self.y.append(self.sample)
        self.y2 = self.y2[1:]
        self.y2.append(self.moving_average)
        self.y3 = self.y3[1:]
        self.y3.append(self.isonotch)
        self.data_line.setData(self.x, self.y)
        self.second_data_line.setData(self.x, self.y2)
        self.third_data_line.setData(self.x, self.y3)


class AveragingWidget(pg.GraphicsWindow):
    pg.setConfigOption('background', 'w')
    pg.setConfigOption('foreground', 'k')
    ptr1 = 0

    '''
    This class is responsible for plot changing in emg noise reduction
    '''

    def __init__(self, parent=None, **kwargs):
        pg.GraphicsWindow.__init__(self, **kwargs)
        self.setParent(parent)
        self.x = list(range(-500, 0))
        self.y = [0 for _ in range(500)]
        self.p1 = self.addPlot(row=0, col=0)
        pen = pg.mkPen(color=(255, 0, 0))
        self.data_line = self.p1.plot(self.x, self.y, pen=pen)
        self.timer = QtCore.QTimer()
        self.timer.setInterval(10)
        self.timer.timeout.connect(self.update)

    def start_plotting(self):
        self.timer.start()

    def stop_plotting(self):
        self.x = list(range(-500, 0))
        self.y = [0 for _ in range(500)]
        self.timer.stop()

    def update(self):
        self.data_line.setData(self.x, self.y)


def data_loop(parameter_lst: List, gui_class, thread_handler):
    """
    This function is responsible for processing data and pass it to plots
    :param parameter_lst: list of parameters
    :param gui_class: instance of GUI class
    :param thread_handler: instance of thread handler class
    :return: None
    """
    sample_buffer = []
    lowpass_filter = []
    comb_filter = []
    moving_average = []
    sample_counter = 0
    added_value = 0
    detection_threshold = 0.00007
    last_detection_threshold = 0
    n1 = []
    n2 = []
    qrs_buffer = []
    samples_between_n = []
    current_qrs = 0
    average_buffer = []
    average_buffer_index = 1
    detected_qrs = False
    sum_of_average_samples = []
    isonotch_buffer = []
    samples_delay_buffer = []
    actual_samples_averaging = []
    qrs_memory = []
    averaging_lst_x = []
    averaging_lst_y = []
    qrs_counter = 0
    qrs_divider = 2
    actual_qrs = 0

    with open(gui_class.default_path, "r") as file:
        for line in file:
            line = line.strip()
            line = float(line)
            time.sleep(0.008)
            gui_class.widget.sample = line
            gui_class.widget.update_x = sample_counter

            if len(moving_average) == 0:
                gui_class.widget.moving_average = 0
            if len(qrs_buffer) < 1:
                gui_class.widget.averaging = 0
            if len(isonotch_buffer) < 5:
                isonotch_buffer.append(line)
                samples_delay_buffer.append([sample_counter, line])
                sample_buffer.append(line)
                gui_class.widget.isonotch = 0
            if len(isonotch_buffer) >= 5:
                isonotch_value = line - sample_buffer[0] + parameter_lst[1] * isonotch_buffer[0]
                isonotch_buffer.append(isonotch_value)
                sample_buffer.append(line)
                samples_delay_buffer.append([sample_counter, isonotch_value])
                gui_class.widget.isonotch = isonotch_value
                isonotch_buffer = isonotch_buffer[1:]
            if len(sample_buffer) >= 5:
                lowpass_value = 0.125 * (sample_buffer[-1] + 2 * sample_buffer[-2] + 2 * sample_buffer[-3]
                                         + 2 * sample_buffer[-4] + sample_buffer[-5])
                lowpass_filter.append(lowpass_value)
                sample_buffer = sample_buffer[1:]

            if len(lowpass_filter) >= 19:
                comb_value = lowpass_filter[-1] - lowpass_filter[-7] + lowpass_filter[-13] - lowpass_filter[-19]
                comb_filter.append(comb_value)

            if len(comb_filter) >= 2 * parameter_lst[0] + 1:
                for index in range(len(comb_filter)):
                    added_value += comb_filter[index] ** 2
                added_value = added_value / (2 * parameter_lst[0] + 1)
                moving_average.append(added_value)
                if len(moving_average) == 1:
                    gui_class.widget.moving_average = moving_average[0]
                if len(moving_average) >= 2:
                    gui_class.widget.moving_average = moving_average[1]
                    if moving_average[1] > detection_threshold and moving_average[0] < detection_threshold:
                        n1.append(sample_counter)
                    if len(n1) > len(n2):
                        samples_between_n.append([sample_counter, moving_average[1]])
                    if moving_average[1] < detection_threshold and moving_average[0] > detection_threshold:
                        if len(n1) > 0:
                            n2.append(sample_counter)
                            qrs_position = (n1[-1] + n2[-1]) // 2
                            qrs_buffer.append((n1[-1] + n2[-1]) // 2)
                            delay_for_qrs = n2[-1] - qrs_position
                            actual_qrs = samples_delay_buffer[-(12 + parameter_lst[0] + delay_for_qrs)]
                            if qrs_counter >= 2:
                                qrs_memory.append(actual_qrs)
                            if len(qrs_buffer) == 1:
                                qrs_n2_delay = (n2[-1] - qrs_position)
                            detected_qrs = True
                            qrs_counter += 1
                            if qrs_counter == 2:
                                r2_qrs_value = samples_delay_buffer[-(12 + parameter_lst[0] + delay_for_qrs)]
                    if len(n2) >= 1 and sample_counter == (15 + n2[-1]):
                        last_detection_threshold = detection_threshold
                        for sample in samples_between_n:
                            if sample[0] == qrs_buffer[-1]:
                                current_qrs = sample[1]
                                samples_between_n = []
                        detection_threshold = 0.25 * (last_detection_threshold + 1.5 * current_qrs)

                    if qrs_counter == 2:
                        n12 = (qrs_buffer[-1] - qrs_buffer[-2]) // 2

                    if qrs_counter == 3:
                        n23 = (qrs_buffer[-1] - qrs_buffer[-2]) // 2

                    if qrs_counter == 1 or qrs_counter == 2:
                        actual_samples_averaging.append(
                            samples_delay_buffer[-(12 + parameter_lst[0] + qrs_n2_delay)])
                    if detected_qrs and qrs_counter == 3:
                        average_buffer = actual_samples_averaging[n12:(2 * n12 + n23)]
                        sum_of_average_samples = deepcopy(average_buffer)
                        if r2_qrs_value in actual_samples_averaging:
                            qrs_actual_samples_position = actual_samples_averaging.index(r2_qrs_value)
                        else:
                            qrs_actual_samples_position = len(actual_samples_averaging) // 2
                        detected_qrs = False
                    if qrs_counter >= 3:
                        if len(qrs_memory) > 0:
                            if actual_samples_averaging[qrs_actual_samples_position][1] == qrs_memory[0][1]:

                                new_samples_to_average = actual_samples_averaging[
                                                         abs(qrs_actual_samples_position - n12):abs(
                                                             qrs_actual_samples_position + n23)]
                                for index in range(len(average_buffer)):
                                    sum_of_average_samples[index][1] += new_samples_to_average[index][1]
                                    average_buffer[index][1] = sum_of_average_samples[index][1] / qrs_divider

                                averaging_lst_x = [i for i in range(len(average_buffer))]
                                averaging_lst_y = [av_samp[1] for av_samp in average_buffer]
                                gui_class.averaging_widget.x = averaging_lst_x
                                gui_class.averaging_widget.y = averaging_lst_y
                                averaging_lst_x = []
                                averaging_lst_y = []
                                qrs_divider += 1
                                qrs_memory = qrs_memory[1:]
                        actual_samples_averaging.append(
                            samples_delay_buffer[-(12 + parameter_lst[0] + qrs_n2_delay)])
                        actual_samples_averaging = actual_samples_averaging[1:]

                    moving_average = moving_average[1:]
                comb_filter = comb_filter[1:]

            sample_counter += 1
            if len(samples_delay_buffer) >= (11 + parameter_lst[0] + 100000):
                samples_delay_buffer = samples_delay_buffer[1:]
            if len(n1) > 15:
                n1 = n1[1:]
            if len(n2) > 15:
                n2 = n2[1:]
            if len(qrs_buffer) > 15:
                qrs_buffer = qrs_buffer[1:]
            if gui_class.stop_program:
                break
            if thread_handler.stop_thread:
                break
