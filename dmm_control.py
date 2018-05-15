import os
import sys

import wx
import matplotlib
import serial.tools.list_ports
from threading import *

matplotlib.use('WXAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigCanvas
import numpy as np
import pylab
import HP_3457A
import csv
import math
import time

global hp


class dataval(object):
    def __init__(self):
        self.data = []
        self.minnum = math.inf
        self.maxnum = -math.inf
        self.len = 0
        self.avg = 0
        self.devIntermediateSum = 0

    def add(self, val):
        try:
            float(val)
        except:
            print(str(val) + " is not a float!")
        if val < self.minnum:
            self.minnum = val
        if val > self.maxnum:
            self.maxnum = val
        prevAvg = self.avg
        self.avg = ((self.avg * self.len) + val) / (self.len + 1)
        self.devIntermediateSum = self.devIntermediateSum + (val - prevAvg) * (val - self.avg)
        self.len += 1
        self.data.append(val)

    def getmin(self):
        return self.minnum

    def getmax(self):
        return self.maxnum

    def getavg(self):
        return self.avg

    def getlen(self):
        return self.len

    def getstd(self):
        return math.sqrt(self.devIntermediateSum / self.len)

    def clear(self):
        self.__init__()

    def __getitem__(self, item):
        return self.data[item]


class BoundControlBox(wx.Panel):
    def __init__(self, parent, ID, label, initval):
        super(BoundControlBox, self).__init__(parent, ID)

        self.value = initval
        box = wx.StaticBox(self, -1, label)
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)

        self.radio_auto = wx.RadioButton(self, -1, label="Auto", style=wx.RB_GROUP)
        self.radio_manual = wx.RadioButton(self, -1, label="Manual")
        self.manual_text = wx.TextCtrl(self, -1, size=(35, -1), value=str(initval), style=wx.TE_PROCESS_ENTER)

        self.Bind(wx.EVT_UPDATE_UI, self.on_update_manual_text, self.manual_text)
        self.Bind(wx.EVT_TEXT_ENTER, self.on_text_enter, self.manual_text)

        manual_box = wx.BoxSizer(wx.HORIZONTAL)
        manual_box.Add(self.radio_manual, flag=wx.ALIGN_CENTER_VERTICAL)
        manual_box.Add(self.manual_text, flag=wx.ALIGN_CENTER_VERTICAL)

        sizer.Add(self.radio_auto, 0, wx.ALL, 10)
        sizer.Add(manual_box, 0, wx.ALL, 10)

        self.SetSizer(sizer)
        sizer.Fit(self)

    def on_update_manual_text(self, event):
        self.manual_text.Enable(self.radio_manual.GetValue())

    def on_text_enter(self, event):
        self.value = self.manual_text.GetValue()

    def is_auto(self):
        return self.radio_auto.GetValue()

    def manual_value(self):
        return self.value


class BinRangeBox(wx.Panel):
    def __init__(self, parent, ID, label):
        super(BinRangeBox, self).__init__(parent, ID)

        self.value = None
        box = wx.StaticBox(self, -1, label)
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)

        self.radio_auto = wx.RadioButton(self, -1, label="Auto", style=wx.RB_GROUP)
        self.radio_manual_span = wx.RadioButton(self, -1, label="Center-Span")
        self.radio_manual_range = wx.RadioButton(self, -1, label="Min-Max")
        self.manual_text_1 = wx.TextCtrl(self, -1, size=(35, -1), value=str(""), style=wx.TE_PROCESS_ENTER)
        self.manual_text_2 = wx.TextCtrl(self, -1, size=(35, -1), value=str(""), style=wx.TE_PROCESS_ENTER)

        self.Bind(wx.EVT_UPDATE_UI, self.on_update_manual_text, self.manual_text_1)
        self.Bind(wx.EVT_TEXT_ENTER, self.on_text_enter, self.manual_text_1)

        manual_box = wx.BoxSizer(wx.HORIZONTAL)
        manual_box.Add(self.radio_manual_span, flag=wx.ALIGN_CENTER_VERTICAL)
        manual_box.Add(self.radio_manual_range, flag=wx.ALIGN_CENTER_VERTICAL)
        manual_box.Add(self.manual_text_1, border=1, flag=wx.ALIGN_CENTER_VERTICAL)
        manual_box.Add(self.manual_text_2, flag=wx.ALIGN_CENTER_VERTICAL)

        sizer.Add(self.radio_auto, 0, wx.ALL, 10)
        sizer.Add(manual_box, 0, wx.ALL, 10)

        self.SetSizer(sizer)
        sizer.Fit(self)

    def on_update_manual_text(self, event):
        self.manual_text_1.Enable(self.radio_manual_range.GetValue() or self.radio_manual_span.GetValue())
        self.manual_text_2.Enable(self.radio_manual_range.GetValue() or self.radio_manual_span.GetValue())

    def on_text_enter(self, event):
        self.value = [self.manual_text_1.GetValue(), self.manual_text_2.GetValue()]

    def is_auto(self):
        return self.radio_auto.GetValue()

    def manual_value(self):
        return [[self.manual_text_1.GetValue(), self.manual_text_2.GetValue()], self.radio_manual_range.GetValue(),
                self.radio_manual_span.GetValue()]


class BinControlBox(wx.Panel):
    def __init__(self, parent, ID, label, initval):
        super(BinControlBox, self).__init__(parent, ID)

        self.value = initval

        box = wx.StaticBox(self, -1, label)
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        self.manual_text = wx.TextCtrl(self, -1, size=(35, -1), value=str(initval), style=wx.TE_PROCESS_ENTER)

        self.Bind(wx.EVT_UPDATE_UI, self.on_update_manual_text, self.manual_text)
        self.Bind(wx.EVT_TEXT_ENTER, self.on_text_enter, self.manual_text)
        manual_box = wx.BoxSizer(wx.HORIZONTAL)
        manual_box.Add(self.manual_text, flag=wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(manual_box, 0, wx.ALL, 10)
        self.SetSizer(sizer)
        sizer.Fit(self)

    def on_update_manual_text(self, event):
        self.manual_text.Enable(True)

    def on_text_enter(self, event):
        self.value = self.manual_text.GetValue()

    def manual_value(self):
        return int(self.value)


class offsetBox(wx.Panel):
    def __init__(self, parent, ID, label):
        super(offsetBox, self).__init__(parent, ID)

        box = wx.StaticBox(self, -1, label)
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        self.manual_text = wx.TextCtrl(self, -1, "", size=(185, 40))
        self.manual_text.SetFont(wx.Font(16, wx.FONTFAMILY_DECORATIVE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        manual_box = wx.BoxSizer(wx.HORIZONTAL)
        manual_box.Add(self.manual_text, flag=wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(manual_box, 0, wx.ALL, 10)
        self.SetSizer(sizer)
        sizer.Fit(self)

    def SetValue(self, value):
        self.manual_text.SetValue(value)


EVT_RESULT_ID = wx.NewId()


def EVT_RESULT(win, func):
    win.Connect(-1, -1, EVT_RESULT_ID, func)


class ResultEvent(wx.PyEvent):
    def __init__(self, data, ids):
        super(ResultEvent, self).__init__()
        self.SetEventType(EVT_RESULT_ID)
        self.datas = data
        self.ids = ids


class Worker(Thread):
    def __init__(self, notify_window, id):
        self.stopped = False
        Thread.__init__(self)
        self._notify_window = notify_window
        self.id = id
        self.start()

    def run(self):
        if not self.stopped:
            global hp
            try:
                hp
            except NameError:
                self.setCom()
            event = ResultEvent(hp.measure(), self.id)
            if not self.stopped:
                wx.PostEvent(self._notify_window, event)


class GraphFrame(wx.Frame):
    def __init__(self):
        super(GraphFrame, self).__init__(None, title='HP/Agilent 3457A Multimeter Panel')

        self.menubar = None
        global hp
        try:
            hp
        except NameError:
            self.setCom(None)

        self.m_stddev = 0
        self.m_offset = 0
        self.panel = None
        self.canvas = None
        self.xmin_control = None
        self.xmax_control = None
        self.ymin_control = None
        self.ymax_control = None
        self.histo_width = None
        self.bin_control = None
        self.pause_button = None
        self.cb_grid = None
        self.cb_xlab = None
        self.xVal = None
        self.yVal = None
        self.std = None
        self.histoMax = None
        self.hbox1 = None
        self.hbox2 = None
        self.clear = None
        self.hbox3 = None
        self.mainNum = None
        self.vbox6 = None
        self.hbox4 = None
        self.avg = None
        self.samps = None
        self.vbox2 = None
        self.upperLim = None
        self.lowerLim = None
        self.max = None
        self.min = None
        self.vbox3 = None
        self.vbox4 = None
        self.DCV = None
        self.DCI = None
        self.aci = None
        self.acv = None
        self.freq = None
        self.ohms2 = None
        self.ohms4 = None
        self.vbox5 = None
        self.acdci = None
        self.acdcv = None
        self.per = None
        self.vbox = None

        self.fig = None
        self.Mode = None
        self.axes = None
        self.histo = None
        self.plot_data = None

        self.paused = False
        self.dataval = dataval()
        self.timing = []
        self.worker = None
        self.id = 1
        if not self.worker:
            self.worker = Worker(self, self.id)
        EVT_RESULT(self, self.OnResult)
        self.create_menu()
        self.create_main_panel()

    def create_menu(self):
        self.menubar = wx.MenuBar()

        # file menu
        menu_file = wx.Menu()
        m_expt = menu_file.Append(-1, "&Save Plot\tCtrl-S", "Save Plot to File")
        self.Bind(wx.EVT_MENU, self.on_save_plot, m_expt)
        m_csv = menu_file.Append(-1, "&Save Data to CSV", "Save Data to CSV")
        self.Bind(wx.EVT_MENU, self.on_save_csv, m_csv)
        menu_file.AppendSeparator()
        m_exit = menu_file.Append(-1, "E&xit\tCtrl-X", "Exit")
        self.Bind(wx.EVT_MENU, self.OnExit, m_exit)
        self.menubar.Append(menu_file, "&File")

        # settings menu
        menu_set = wx.Menu()
        m_ser = menu_set.Append(-1, "Serial Ports", "Set serial port")
        self.Bind(wx.EVT_MENU, self.setCom, m_ser)
        m_nplc = menu_set.Append(-1, "NPLC", "Number of Power Line Cycles")
        self.Bind(wx.EVT_MENU, self.setNPLC, m_nplc)
        m_term = menu_set.Append(-1, "Set Terminals", "Set Front/Rear Terminal")
        self.Bind(wx.EVT_MENU, self.setTerm, m_term)
        self.menubar.Append(menu_set, "&Settings")

        # view menu
        menu_view = wx.Menu()
        self.m_stddev = menu_view.Append(wx.ID_ANY, "Standard Deviation as Percentage",
                                         "Standard Deviation as Percentage", kind=wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, None, self.m_stddev)
        self.m_offset = menu_view.Append(wx.ID_ANY, "Possibilities as Percentage", "Possibilities as Percentage",
                                         kind=wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, None, self.m_offset)
        menu_view.Check(self.m_stddev.GetId(), False)
        menu_view.Check(self.m_offset.GetId(), False)
        self.menubar.Append(menu_view, "&View")

        self.SetMenuBar(self.menubar)

    def create_main_panel(self):
        self.panel = wx.Panel(self)
        self.Bind(wx.EVT_CLOSE, self.OnExit)
        self.init_plot()
        self.canvas = FigCanvas(self.panel, -1, self.fig)

        self.xmin_control = BoundControlBox(self.panel, -1, "X min", 0)
        self.xmax_control = BoundControlBox(self.panel, -1, "X max", 60)
        self.ymin_control = BoundControlBox(self.panel, -1, "Y min", 0)
        self.ymax_control = BoundControlBox(self.panel, -1, "Y max", 10)
        self.histo_width = BinRangeBox(self.panel, -1, "Histogram Width")
        self.bin_control = BinControlBox(self.panel, -1, "# of Bins", 10)

        self.pause_button = wx.Button(self.panel, -1, "Pause")
        self.Bind(wx.EVT_BUTTON, self.on_pause_button, self.pause_button)
        self.Bind(wx.EVT_UPDATE_UI, self.on_update_pause_button, self.pause_button)

        self.cb_grid = wx.CheckBox(self.panel, -1, "Show Grid", style=wx.ALIGN_RIGHT)
        self.Bind(wx.EVT_CHECKBOX, self.on_cb_grid, self.cb_grid)
        self.cb_grid.SetValue(True)

        self.cb_xlab = wx.CheckBox(self.panel, -1, "Show X labels", style=wx.ALIGN_RIGHT)
        self.Bind(wx.EVT_CHECKBOX, self.on_cb_xlab, self.cb_xlab)
        self.cb_xlab.SetValue(True)

        self.xVal = offsetBox(self.panel, -1, "Cursor X Value")
        self.yVal = offsetBox(self.panel, -1, "Cursor Y Value")
        self.std = offsetBox(self.panel, -1, "Standard Deviation")
        self.histoMax = offsetBox(self.panel, -1, "Histogram Peak")

        self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox1.Add(self.pause_button, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox1.Add(self.cb_grid, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox1.Add(self.cb_xlab, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox1.Add(self.xVal, border=1, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox1.Add(self.yVal, border=1, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox1.Add(self.std, border=1, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox1.Add(self.histoMax, border=1, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox2.Add(self.xmin_control, border=5, flag=wx.ALL)
        self.hbox2.Add(self.xmax_control, border=5, flag=wx.ALL)
        self.hbox2.AddSpacer(24)
        self.hbox2.Add(self.ymin_control, border=5, flag=wx.ALL)
        self.hbox2.Add(self.ymax_control, border=5, flag=wx.ALL)
        self.hbox2.AddSpacer(24)
        self.hbox2.Add(self.bin_control, border=5, flag=wx.ALL)
        self.hbox2.Add(self.histo_width, border=1, flag=wx.ALL)
        self.clear = wx.Button(self.panel, -1, "Clear Data")
        self.Bind(wx.EVT_BUTTON, self.clear_data, self.clear)
        self.hbox2.Add(self.clear, border=5, flag=wx.ALL)

        # Top Block
        self.hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        self.mainNum = wx.TextCtrl(self.panel, -1, "", size=(440, 90))
        self.mainNum.SetFont(wx.Font(48, wx.FONTFAMILY_DECORATIVE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.vbox6 = wx.BoxSizer(wx.VERTICAL)
        self.hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        self.vbox6.Add(self.mainNum, border=5, flag=wx.ALL)
        self.vbox6.Add(self.hbox4)
        self.avg = offsetBox(self.panel, -1, "Average")
        self.hbox4.Add(self.avg, border=1, flag=wx.ALL)
        self.samps = offsetBox(self.panel, -1, "# of Samples")
        self.hbox4.Add(self.samps, border=1, flag=wx.ALL)
        self.vbox2 = wx.BoxSizer(wx.VERTICAL)
        self.hbox3.Add(self.vbox6, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.hbox3.Add(self.vbox2, 0, flag=wx.ALIGN_RIGHT | wx.TOP)
        self.upperLim = offsetBox(self.panel, -1, "Upper Possibility")
        self.lowerLim = offsetBox(self.panel, -1, "Lower Possibility")
        self.max = offsetBox(self.panel, -1, "Maximum")
        self.min = offsetBox(self.panel, -1, "Minimum")
        self.vbox2.Add(self.upperLim, border=1, flag=wx.ALL)
        self.vbox2.Add(self.lowerLim, border=1, flag=wx.ALL)
        self.vbox3 = wx.BoxSizer(wx.VERTICAL)
        self.vbox3.Add(self.max, border=1, flag=wx.ALL)
        self.vbox3.Add(self.min, border=1, flag=wx.ALL)
        self.hbox3.Add(self.vbox3, 0, flag=wx.ALIGN_RIGHT | wx.TOP)
        self.vbox4 = wx.BoxSizer(wx.VERTICAL)

        # Control Buttons
        self.DCV = wx.Button(self.panel, 0, "DCV")
        self.Bind(wx.EVT_BUTTON, self.setMode, self.DCV)
        self.vbox4.Add(self.DCV, border=1, flag=wx.ALL)
        self.DCI = wx.Button(self.panel, 1, "DCI")
        self.Bind(wx.EVT_BUTTON, self.setMode, self.DCI)
        self.vbox4.Add(self.DCI, border=1, flag=wx.ALL)
        self.ohms2 = wx.Button(self.panel, 2, "2-" + u"\u2126")
        self.Bind(wx.EVT_BUTTON, self.setMode, self.ohms2)
        self.vbox4.Add(self.ohms2, border=1, flag=wx.ALL)
        self.ohms4 = wx.Button(self.panel, 3, "4-" + u"\u2126")
        self.Bind(wx.EVT_BUTTON, self.setMode, self.ohms4)
        self.vbox4.Add(self.ohms4, border=1, flag=wx.ALL)
        self.freq = wx.Button(self.panel, 9, "Frequency")
        self.Bind(wx.EVT_BUTTON, self.setMode, self.freq)
        self.vbox4.Add(self.freq, border=1, flag=wx.ALL)
        self.vbox5 = wx.BoxSizer(wx.VERTICAL)
        self.acv = wx.Button(self.panel, 4, "ACV")
        self.Bind(wx.EVT_BUTTON, self.setMode, self.acv)
        self.vbox5.Add(self.acv, border=1, flag=wx.ALL)
        self.aci = wx.Button(self.panel, 5, "ACI")
        self.Bind(wx.EVT_BUTTON, self.setMode, self.aci)
        self.vbox5.Add(self.aci, border=1, flag=wx.ALL)
        self.acdcv = wx.Button(self.panel, 6, "ACDCV")
        self.Bind(wx.EVT_BUTTON, self.setMode, self.acdcv)
        self.vbox5.Add(self.acdcv, border=1, flag=wx.ALL)
        self.acdci = wx.Button(self.panel, 7, "ACDCI")
        self.Bind(wx.EVT_BUTTON, self.setMode, self.acdci)
        self.vbox5.Add(self.acdci, border=1, flag=wx.ALL)
        self.per = wx.Button(self.panel, 8, "Period")
        self.Bind(wx.EVT_BUTTON, self.setMode, self.per)
        self.vbox5.Add(self.per, border=1, flag=wx.ALL)

        self.hbox3.Add(self.vbox4, 0, flag=wx.ALIGN_RIGHT | wx.TOP)
        self.hbox3.Add(self.vbox5, 0, flag=wx.ALIGN_RIGHT | wx.TOP)

        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.hbox3, 0, flag=wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL)
        self.vbox.Add(self.canvas, 1, flag=wx.LEFT | wx.TOP | wx.GROW)
        self.vbox.Add(self.hbox1, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.Add(self.hbox2, 0, flag=wx.ALIGN_LEFT | wx.TOP)

        self.panel.SetSizer(self.vbox)
        self.vbox.Fit(self)
        self.canvas.mpl_connect('motion_notify_event', self._onMotion)

    def _onMotion(self, event):
        if event.xdata is not None and event.ydata is not None:
            if int(round(event.xdata)) < self.dataval.getlen() and int(round(event.xdata)) in range(
                    int(self.axes.get_xlim()[0]), int(self.axes.get_xlim()[1])):
                self.xVal.SetValue(str(int(round(event.xdata))))
                self.yVal.SetValue(str(Units().convert(self.dataval[int(round(event.xdata))])[0]) + " " +
                                   Units().convert(self.dataval[int(round(event.xdata))])[1] + self.Mode[2])

    def init_plot(self):
        self.Mode = ["DC Voltage", "Volts", "V", "dcv"]
        self.fig = Figure((10, 5), dpi=100, tight_layout=True)
        self.axes = self.fig.add_subplot(121)
        self.axes.set_facecolor('black')
        self.histo = self.fig.add_subplot(122)
        pylab.setp(self.axes.get_xticklabels(), fontsize=8)
        pylab.setp(self.axes.get_yticklabels(), fontsize=8)
        self.axes.set_xlabel("Samples", size=10)
        pylab.setp(self.histo.get_xticklabels(), fontsize=8)
        pylab.setp(self.histo.get_yticklabels(), fontsize=8)
        self.plot_data = self.axes.plot(self.dataval.data, linewidth=1, color=(1, 1, 0))[0]

    def draw_plot(self):
        self.axes.set_title(self.Mode[0] + ' Trend', size=12)
        self.axes.set_ylabel(self.Mode[1], size=10)

        if self.xmax_control.is_auto():
            xmax = self.dataval.getlen() if self.dataval.getlen() > 100 else 100
        else:
            xmax = int(self.xmax_control.manual_value())
        if self.xmin_control.is_auto():
            xmin = xmax - 100
        else:
            if int(self.xmin_control.manual_value()) < 0:
                xmin = xmax + int(self.xmin_control.manual_value())
                if xmin < 0:
                    xmin = 0
            else:
                xmin = int(self.xmin_control.manual_value())

        if xmax == self.dataval.getlen() and xmin == 0:
            mins = self.dataval.getmin()
        else:
            mins = min(self.dataval[xmin:xmax])
        if xmax == self.dataval.getlen() and xmin == 0:
            maxs = self.dataval.getmax()
        else:
            maxs = max(self.dataval[xmin:xmax])

        if self.ymax_control.is_auto():
            ymax = float(maxs + ((maxs - mins) * .05))
        else:
            ymax = float(self.ymax_control.manual_value())

        if self.ymin_control.is_auto():
            if maxs == mins:
                ymin = float(mins - (mins * .05))
            else:
                ymin = float(mins - ((maxs - mins) * .05))
        else:
            ymin = float(self.ymin_control.manual_value())

        self.axes.set_xbound(lower=xmin, upper=xmax)
        self.axes.set_ybound(lower=ymin, upper=ymax)

        if self.cb_grid.IsChecked():
            self.axes.grid(True, color='gray')
        else:
            self.axes.grid(False)

        pylab.setp(self.axes.get_xticklabels(), visible=self.cb_xlab.IsChecked())
        pylab.setp(self.histo.get_xticklabels(), visible=True)
        self.plot_data.set_xdata(np.arange(self.dataval.getlen()))
        self.plot_data.set_ydata(np.array(self.dataval.data))

        if self.dataval.getlen() > 1:
            global hp
            self.mainNum.SetValue(str(Units().convert(self.dataval[self.dataval.getlen() - 1])[0]) + " " +
                                  Units().convert(self.dataval[self.dataval.getlen() - 1])[1] + self.Mode[2])
            offset = hp.getOffset(self.Mode[3], self.dataval[self.dataval.getlen() - 1])
            if self.m_offset.IsChecked():
                self.upperLim.SetValue(self.ppmPercent((float(offset / abs(self.dataval[self.dataval.getlen() - 1])))))
                self.lowerLim.SetValue(self.ppmPercent((-float(offset / abs(self.dataval[self.dataval.getlen() - 1])))))
            else:
                self.upperLim.SetValue(
                    str(Units().convert(self.dataval[self.dataval.getlen() - 1] + offset)[0])[0:8] + " " +
                    Units().convert(self.dataval[self.dataval.getlen() - 1] + offset)[1] + self.Mode[2])
                self.lowerLim.SetValue(
                    str(Units().convert(self.dataval[self.dataval.getlen() - 1] - offset)[0])[0:8] + " " +
                    Units().convert(self.dataval[self.dataval.getlen() - 1] - offset)[1] + self.Mode[2])
            max1 = Units().convert(self.dataval.getmax())
            min1 = Units().convert(self.dataval.getmin())
            self.max.SetValue(str(max1[0]) + " " + max1[1] + self.Mode[2])
            self.min.SetValue(str(min1[0]) + " " + min1[1] + self.Mode[2])
            avg = Units().convert(self.dataval.getavg())
            self.avg.SetValue(str(avg[0])[0:9] + " " + avg[1] + self.Mode[2])
            self.samps.SetValue(str(self.dataval.getlen()))
            if self.m_stddev.IsChecked():
                self.std.SetValue(self.ppmPercent(abs(float(self.dataval.getstd() / self.dataval.getavg()))))
            else:
                std = Units().convert(self.dataval.getstd())
                self.std.SetValue(str(std[0])[0:8] + " " + std[1] + self.Mode[2])
            self.histo.clear()
            if self.histo_width.manual_value()[1] or self.histo_width.manual_value()[2]:
                if self.histo_width.manual_value()[1] and self.histo_width.manual_value()[0][0] != "" and \
                        self.histo_width.manual_value()[0][1] != "":
                    rng = (float(self.histo_width.manual_value()[0][0]), float(self.histo_width.manual_value()[0][1]))
                    n, b, self.hist = self.histo.hist(self.dataval.data, bins=self.bin_control.manual_value(),
                                                      histtype='stepfilled', color='b', range=rng)
                elif self.histo_width.manual_value()[2] and self.histo_width.manual_value()[0][0] != "" and \
                        self.histo_width.manual_value()[0][1] != "":
                    try:
                        center = float(self.histo_width.manual_value()[0][0])
                    except:
                        center = 1
                    try:
                        span = float(self.histo_width.manual_value()[0][1])
                    except:
                        span = 1
                    rng = (center - span, center + span)
                    n, b, self.hist = self.histo.hist(self.dataval.data, bins=self.bin_control.manual_value(),
                                                      histtype='stepfilled', color='b', range=rng)
            else:
                n, b, self.hist = self.histo.hist(self.dataval.data, bins=self.bin_control.manual_value(),
                                                  histtype='stepfilled', color='b')
            self.histoMax.SetValue(str(Units().convert(b[np.where(n == n.max())][0])[0])[0:8] + " " +
                                   Units().convert(b[np.where(n == n.max())][0])[1] + self.Mode[2])
            self.histo.set_title(self.Mode[0] + ' Histogram', size=12)
            self.histo.set_xlabel(self.Mode[1], size=10)
            self.histo.set_ylabel("Samples", size=10)
            pylab.setp(self.histo.get_xticklabels(), fontsize=8)
            pylab.setp(self.histo.get_yticklabels(), fontsize=8)
        self.canvas.draw()

    def on_pause_button(self, event):
        self.paused = not self.paused
        if not self.paused:
            self.id = self.id + 1
            self.worker = Worker(self, self.id)

    def clear_data(self, event):
        self.timing = []
        self.dataval.clear()

    def OnResult(self, event):
        self.worker = None
        if not self.paused and event.ids == self.id:
            self.id = self.id + 1
            self.worker = Worker(self, self.id)
        if event.datas is None:
            print("killing")
        else:
            if event.datas != 1.0000000E+38:
                self.dataval.add(event.datas)
                self.timing.append(int(round(time.time() * 1000)))
                self.draw_plot()
            else:
                self.mainNum.SetValue("OVLD")

    def setMode(self, event):
        dlg = wx.MessageDialog(self, "Changing Measurement Will Clear Previous Data, Continue?",
                               "Delete Data and Change Measurement?", wx.YES_NO | wx.CENTRE | wx.STAY_ON_TOP,
                               wx.DefaultPosition)
        if dlg.ShowModal() != 5103:
            return
        dlg.Destroy()
        if self.worker is not None:
            self.paused = True
            time.sleep(1)
        mode = event.GetId()
        if mode == 0:
            self.Mode = ["DC Voltage", "Volts", "V", "dcv"]
        if mode == 1:
            self.Mode = ["DC Current", "Amperes", "A", "dci"]
        if mode == 2:
            self.Mode = ["2-Wire Ohms", "Ohms", u"\u2126", "ohms2"]
        if mode == 3:
            self.Mode = ["4-Wire Ohms", "Ohms", u"\u2126", "ohms4"]
        if mode == 4:
            self.Mode = ["AC Voltage", "Volts", "V", "acv"]
        if mode == 5:
            self.Mode = ["AC Current", "Amperes", "A", "aci"]
        if mode == 6:
            self.Mode = ["DC Coupled AC Voltage", "Volts", "V", "acdcv"]
        if mode == 7:
            self.Mode = ["DC Coupled AC Current", "Amperes", "A", "acdci"]
        if mode == 8:
            self.Mode = ["Period", "Seconds", "s", "per"]
        if mode == 9:
            self.Mode = ["Frequency", "Hertz", "Hz", "freq"]
        hp.setMeasure(self.Mode[3])
        self.paused = False
        self.id = self.id + 1
        self.worker = Worker(self, self.id)
        self.clear_data(self)

    def on_update_pause_button(self, event):
        label = "Resume" if self.paused else "Pause"
        self.pause_button.SetLabel(label)

    def on_cb_grid(self, event):
        self.draw_plot()

    def on_cb_xlab(self, event):
        self.draw_plot()

    def on_save_plot(self, event):
        file_choices = "PNG (*.png)|*.png"
        dlg = wx.FileDialog(
            self,
            message="Save Plot as...",
            defaultDir=os.getcwd(),
            defaultFile="plot.png",
            wildcard=file_choices,
            style=wx.FD_SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.canvas.print_figure(path, dpi=100)

    def on_save_csv(self, event):
        file_choices = "CSV (*.csv)|*.csv"
        dlg = wx.FileDialog(
            self,
            message="Save Data as...",
            defaultDir=os.getcwd(),
            defaultFile="output.csv",
            wildcard=file_choices,
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            with open(path, "w", newline='') as f:
                writer = csv.writer(f)
                writer.writerow([self.Mode[0], "Timestamp (ms)"])
                for i in range(0, self.dataval.getlen()):
                    writer.writerow([self.dataval[i], self.timing[i]])

    def setCom(self, event):
        global hp
        if len(sys.argv) == 1:
            dlg = wx.TextEntryDialog(self, "What is the serial port?", value=sorted(serial.tools.list_ports.comports())[0][0])
            dlg.ShowModal()
            com = dlg.GetValue()
            dlg.Destroy()
        else:
            com = sys.argv[1]
        hp = HP_3457A.hp(com)

    def setNPLC(self, event):
        global hp
        dlg = wx.TextEntryDialog(self, "How Many Power Line Cycles?", value="10")
        dlg.ShowModal()
        plc = dlg.GetValue()
        dlg.Destroy()
        hp.setPlc(plc)

    def setTerm(self, event):
        global hp
        dlg = wx.SingleChoiceDialog(self, 'Set Terminals', 'Set Terminals', ["Front", "Rear"], wx.CHOICEDLG_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            if self.worker is not None:
                self.paused = True
                time.sleep(1)
            term = dlg.GetStringSelection()
            hp.setTerm(term)
            self.paused = False
            self.id = self.id + 1
            self.worker = Worker(self, self.id)
        dlg.Destroy()

    def OnExit(self, event):
        self.worker.stopped = True
        self.Destroy()

    def ppmPercent(self, percent):
        if abs(percent * 100) >= 0.001:
            return str(percent * 100)[0:8] + "%"
        else:
            return str(10000 * percent)[0:8] + "ppm"


class Units:
    def __init__(self):
        global si
        si = {
            -18: {'multiplier': 10 ** 18, 'prefix': 'a'},
            -17: {'multiplier': 10 ** 18, 'prefix': 'a'},
            -16: {'multiplier': 10 ** 18, 'prefix': 'a'},
            -15: {'multiplier': 10 ** 15, 'prefix': 'f'},
            -14: {'multiplier': 10 ** 15, 'prefix': 'f'},
            -13: {'multiplier': 10 ** 15, 'prefix': 'f'},
            -12: {'multiplier': 10 ** 12, 'prefix': 'p'},
            -11: {'multiplier': 10 ** 12, 'prefix': 'p'},
            -10: {'multiplier': 10 ** 12, 'prefix': 'p'},
            -9: {'multiplier': 10 ** 9, 'prefix': 'n'},
            -8: {'multiplier': 10 ** 9, 'prefix': 'n'},
            -7: {'multiplier': 10 ** 9, 'prefix': 'n'},
            -6: {'multiplier': 10 ** 6, 'prefix': u'\u03bc'},
            -5: {'multiplier': 10 ** 6, 'prefix': u'\u03bc'},
            -4: {'multiplier': 10 ** 6, 'prefix': u'\u03bc'},
            -3: {'multiplier': 10 ** 3, 'prefix': 'm'},
            -2: {'multiplier': 10 ** 3, 'prefix': 'm'},
            -1: {'multiplier': 1, 'prefix': ''},
            0: {'multiplier': 1, 'prefix': ''},
            1: {'multiplier': 1, 'prefix': ''},
            2: {'multiplier': 1, 'prefix': ''},
            3: {'multiplier': 10 ** 3, 'prefix': 'k'},
            4: {'multiplier': 10 ** 3, 'prefix': 'k'},
            5: {'multiplier': 10 ** 3, 'prefix': 'k'},
            6: {'multiplier': 10 ** 6, 'prefix': 'M'},
            7: {'multiplier': 10 ** 6, 'prefix': 'M'},
            8: {'multiplier': 10 ** 6, 'prefix': 'M'},
            9: {'multiplier': 10 ** 9, 'prefix': 'G'},
            10: {'multiplier': 10 ** 9, 'prefix': 'G'},
            11: {'multiplier': 10 ** 9, 'prefix': 'G'},
            12: {'multiplier': 10 ** 12, 'prefix': 'T'},
            13: {'multiplier': 10 ** 12, 'prefix': 'T'},
            14: {'multiplier': 10 ** 12, 'prefix': 'T'},
            15: {'multiplier': 10 ** 15, 'prefix': 'P'},
            16: {'multiplier': 10 ** 15, 'prefix': 'P'},
            17: {'multiplier': 10 ** 15, 'prefix': 'P'},
            18: {'multiplier': 10 ** 18, 'prefix': 'E'},
        }

    def convert(self, number):
        if number == 0:
            return [number, '']
        if number < 0:
            negative = True
        else:
            negative = False
        if negative:
            number -= number * 2
        exponent = int(math.log10(number))
        if negative:
            number -= number * 2
        if exponent < 0:
            exponent -= 1
            return [number * si[exponent]['multiplier'], si[exponent]['prefix']]
        elif exponent > 0:
            return [number / si[exponent]['multiplier'], si[exponent]['prefix']]
        elif exponent == 0:
            return [number, '']


if __name__ == '__main__':
    app = wx.App()
    app.frame = GraphFrame()
    app.frame.Show()
    app.MainLoop()
    sys.exit(0)
