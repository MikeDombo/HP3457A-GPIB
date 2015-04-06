import os
import pprint
import random
import sys
import wx
import matplotlib
matplotlib.use('WXAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
	FigureCanvasWxAgg as FigCanvas, \
	NavigationToolbar2WxAgg as NavigationToolbar
import numpy as np
import pylab
from pylab import get_current_fig_manager as gcfm
import HP_3457A
import csv
import math
hp = HP_3457A.hp()

class DataGen(object):
	def __init__(self, init=50):
		self.data = self.init = init
		
	def next(self):
		self._recalc_data()
		return self.data
	
	def _recalc_data(self):
		delta = random.uniform(-0.5, 0.5)
		r = random.random()
		if r > 0.9:
			self.data += delta * 15
		elif r > 0.8: 
			delta += (0.5 if self.init > self.data else -0.5)
			self.data += delta
		else:
			self.data += delta
			
class dataval(object):
	def __init__(self):
		self.minnum = sys.maxint
		self.maxnum = -sys.maxint+1
		self.len = 0
		self.avg = 0
	def add(self, val):
		if(val<self.minnum):
			self.minnum = val
		if(val>self.maxnum):
			self.maxnum = val
		self.avg = ((self.avg*self.len)+val)/(self.len+1)
		self.len+=1
	def getmin(self):
		return self.minnum
	def getmax(self):
		return self.maxnum
	def getavg(self):
		return self.avg
	def getlen(self):
		return self.len
	def getstd(self, data):
		diffsquared = 0
		sum_diffsquared = 0
		for val in data:
			diffsquared = (val-self.avg)**2
			sum_diffsquared = diffsquared + sum_diffsquared
		return (sum_diffsquared/self.len)**(.5)
		
class BoundControlBox(wx.Panel):
	def __init__(self, parent, ID, label, initval):
		wx.Panel.__init__(self, parent, ID)
		self.value = initval
		box = wx.StaticBox(self, -1, label)
		sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
		
		self.radio_auto = wx.RadioButton(self, -1, 
			label="Auto", style=wx.RB_GROUP)
		self.radio_manual = wx.RadioButton(self, -1,
			label="Manual")
		self.manual_text = wx.TextCtrl(self, -1, 
			size=(35,-1),
			value=str(initval),
			style=wx.TE_PROCESS_ENTER)
		
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
		wx.Panel.__init__(self, parent, ID)
		
		box = wx.StaticBox(self, -1, label)
		sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
		
		self.radio_auto = wx.RadioButton(self, -1, 
			label="Auto", style=wx.RB_GROUP)
		self.radio_manual_span = wx.RadioButton(self, -1,
			label="Center-Span")
		self.radio_manual_range = wx.RadioButton(self, -1,
			label="Min-Max")
		self.manual_text_1 = wx.TextCtrl(self, -1, 
			size=(35,-1),
			value=str(""),
			style=wx.TE_PROCESS_ENTER)
		self.manual_text_2 = wx.TextCtrl(self, -1, 
			size=(35,-1),
			value=str(""),
			style=wx.TE_PROCESS_ENTER)
		
		self.Bind(wx.EVT_UPDATE_UI, self.on_update_manual_text, self.manual_text_1)
		self.Bind(wx.EVT_TEXT_ENTER, self.on_text_enter, self.manual_text_1)
		
		manual_box = wx.BoxSizer(wx.HORIZONTAL)
		manual_box.Add(self.radio_manual_span, flag=wx.ALIGN_CENTER_VERTICAL)
		manual_box.Add(self.radio_manual_range, flag=wx.ALIGN_CENTER_VERTICAL)
		manual_box.Add(self.manual_text_1,border=1, flag=wx.ALIGN_CENTER_VERTICAL)
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
		return [[self.manual_text_1.GetValue(), self.manual_text_2.GetValue()], self.radio_manual_range.GetValue(), self.radio_manual_span.GetValue()]
		
class BinControlBox(wx.Panel):
	def __init__(self, parent, ID, label, initval):
		wx.Panel.__init__(self, parent, ID)
		
		self.value = initval
		
		box = wx.StaticBox(self, -1, label)
		sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
		self.manual_text = wx.TextCtrl(self, -1, size=(35,-1), value=str(initval), style=wx.TE_PROCESS_ENTER)
		
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
		wx.Panel.__init__(self, parent, ID)
		box = wx.StaticBox(self, -1, label)
		sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
		self.manual_text = wx.TextCtrl(self, -1, "", size=(185,40))
		self.manual_text.SetFont(wx.Font(16, wx.DECORATIVE, wx.NORMAL, wx.NORMAL))
		manual_box = wx.BoxSizer(wx.HORIZONTAL)
		manual_box.Add(self.manual_text, flag=wx.ALIGN_CENTER_VERTICAL)
		sizer.Add(manual_box, 0, wx.ALL, 10)
		self.SetSizer(sizer)
		sizer.Fit(self)
	def SetValue(self, value):
		self.manual_text.SetValue(value)

class GraphFrame(wx.Frame):
	title = 'HP/Agilent 3457A Multimeter Panel'
	def __init__(self):
		wx.Frame.__init__(self, None, -1, self.title)
		
		self.datagen = DataGen()
		add = self.datagen.next()
		self.dataval = dataval()
		self.dataval.add(add)
		self.data = [add]
		self.paused = False
		
		self.create_menu()
		self.create_main_panel()
		
		self.redraw_timer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.on_redraw_timer, self.redraw_timer)        
		self.redraw_timer.Start(0)

	def create_menu(self):
		self.menubar = wx.MenuBar()
		
		menu_file = wx.Menu()
		m_expt = menu_file.Append(-1, "&Save plot\tCtrl-S", "Save plot to file")
		self.Bind(wx.EVT_MENU, self.on_save_plot, m_expt)
		menu_file.AppendSeparator()
		m_exit = menu_file.Append(-1, "E&xit\tCtrl-X", "Exit")
		self.Bind(wx.EVT_MENU, self.on_exit, m_exit)
		self.menubar.Append(menu_file, "&File")
		self.SetMenuBar(self.menubar)
	
	def create_main_panel(self):
		self.panel = wx.Panel(self)
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
		
		#Top Block
		self.hbox3 = wx.BoxSizer(wx.HORIZONTAL)
		self.mainNum = wx.TextCtrl(self.panel, -1, "", size=(440,90))
		self.mainNum.SetFont(wx.Font(40, wx.DECORATIVE, wx.NORMAL, wx.NORMAL))
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
		#Control Buttons
		self.DCV = wx.Button(self.panel, 0, "DCV")
		self.Bind(wx.EVT_BUTTON, self.setMode, self.DCV)
		self.vbox4.Add(self.DCV, border=1, flag=wx.ALL)
		self.DCI = wx.Button(self.panel, 1, "DCI")
		self.Bind(wx.EVT_BUTTON, self.setMode, self.DCI)
		self.vbox4.Add(self.DCI, border=1, flag=wx.ALL)
		self.ohms2 = wx.Button(self.panel, 2, "2-"+u"\u2126")
		self.Bind(wx.EVT_BUTTON, self.setMode, self.ohms2)
		self.vbox4.Add(self.ohms2, border=1, flag=wx.ALL)
		self.ohms4 = wx.Button(self.panel, 3, "4-"+u"\u2126")
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
		if event.xdata != None and event.ydata != None:
			if int(round(event.xdata)) < len(self.data) and int(round(event.xdata)) in range (int(self.axes.get_xlim()[0]), int(self.axes.get_xlim()[1])):
				self.xVal.SetValue(str(int(round(event.xdata)))[0:8])
				self.yVal.SetValue(str(self.data[int(round(event.xdata))])[0:8]+" "+self.Mode[2])
				
	def init_plot(self):
		self.Mode = ["DC Voltage", "Volts", "V", "dcv"]
		self.fig = Figure((10, 5), dpi=100, tight_layout=True)
		self.axes = self.fig.add_subplot(121)
		self.histo = self.fig.add_subplot(122)
		self.axes.set_axis_bgcolor('black')
		pylab.setp(self.axes.get_xticklabels(), fontsize=8)
		pylab.setp(self.axes.get_yticklabels(), fontsize=8)
		self.axes.set_xlabel("Samples", size=10)
		pylab.setp(self.histo.get_xticklabels(), fontsize=8)
		pylab.setp(self.histo.get_yticklabels(), fontsize=8)
		self.plot_data = self.axes.plot(self.data, linewidth=1, color=(1, 1, 0),)[0]
		
	def draw_plot(self):
		self.axes.set_title(self.Mode[0]+' Trend', size=12)
		self.axes.set_ylabel(self.Mode[1], size=10)
		if self.xmax_control.is_auto():
			xmax = self.dataval.getlen() if self.dataval.getlen() > 60 else 60
		else:
			xmax = int(self.xmax_control.manual_value())
		if self.xmin_control.is_auto():            
			xmin = xmax - 60
		else:
			xmin = int(self.xmin_control.manual_value())
		if self.ymin_control.is_auto():
			ymin = int(min(self.data[xmin:xmax]))-1
		else:
			ymin = int(self.ymin_control.manual_value())
		if self.ymax_control.is_auto():
			ymax = int(max(self.data[xmin:xmax]))+1
		else:
			ymax = (self.ymax_control.manual_value())
		self.axes.set_xbound(lower=xmin, upper=xmax)
		self.axes.set_ybound(lower=ymin, upper=ymax)
		if self.cb_grid.IsChecked():
			self.axes.grid(True, color='gray')
			self.histo.grid(True, color='gray')
		else:
			self.axes.grid(False)
			self.histo.grid(False)
			
		pylab.setp(self.axes.get_xticklabels(), visible=self.cb_xlab.IsChecked())
		pylab.setp(self.histo.get_xticklabels(), visible=True)
		self.plot_data.set_xdata(np.arange(self.dataval.getlen()))
		self.plot_data.set_ydata(np.array(self.data))
		
		if len(self.data)>1:
			self.mainNum.SetValue(str(Units().convert(self.data[self.dataval.getlen()-1])[0])[0:8]+" "+Units().convert(self.data[self.dataval.getlen()-1])[1]+self.Mode[2])
			offset = hp.getOffset(self.Mode[3],self.data[self.dataval.getlen()-1], "1", "6.5")
			self.upperLim.SetValue(str(Units().convert(self.data[self.dataval.getlen()-1]+offset)[0])[0:8]+" "+Units().convert(self.data[self.dataval.getlen()-1]+offset)[1]+self.Mode[2])
			self.lowerLim.SetValue(str(self.data[self.dataval.getlen()-1]-offset)[0:8]+" "+Units().convert(self.data[self.dataval.getlen()-1]-offset)[1]+self.Mode[2])
			max1 = Units().convert(self.dataval.getmax())
			min1 = Units().convert(self.dataval.getmin())
			self.max.SetValue(str(max1[0])[0:8]+" "+max1[1]+self.Mode[2])
			self.min.SetValue(str(min1[0])[0:8]+" "+min1[1]+self.Mode[2])
			avg = Units().convert(self.dataval.getavg())
			self.avg.SetValue(str(avg[0])[0:8]+" "+avg[1]+self.Mode[2])
			self.samps.SetValue(str(self.dataval.getlen()))
			std = Units().convert(self.dataval.getstd(self.data))
			self.std.SetValue(str(std[0])[0:8]+" "+std[1]+self.Mode[2])
			self.histo.clear()
			if(self.histo_width.manual_value()[1] or self.histo_width.manual_value()[2]):
				if(self.histo_width.manual_value()[1] and self.histo_width.manual_value()[0][0] != "" and self.histo_width.manual_value()[0][1] != ""):
					rng = (int(self.histo_width.manual_value()[0][0]), int(self.histo_width.manual_value()[0][1]))
					n,b,self.hist = self.histo.hist(self.data, bins=self.bin_control.manual_value(), histtype='stepfilled', color='b', range=rng)
					self.histoMax.SetValue(str(b[np.where(n == n.max())][0])[0:8]+" "+self.Mode[2])
				elif(self.histo_width.manual_value()[2] and self.histo_width.manual_value()[0][0] != "" and self.histo_width.manual_value()[0][1] != ""):
					center = int(self.histo_width.manual_value()[0][0])
					span = int(self.histo_width.manual_value()[0][1])
					rng = (center-span, center+span)
					n, b, self.hist = self.histo.hist(self.data, bins=self.bin_control.manual_value(), histtype='stepfilled', color='b', range=rng)
					self.histoMax.SetValue(str(b[np.where(n == n.max())][0])[0:8]+" "+self.Mode[2])
			else:
				n, b, self.hist = self.histo.hist(self.data, bins=self.bin_control.manual_value(), histtype='stepfilled', color='b')
				self.histoMax.SetValue(str(b[np.where(n == n.max())][0])[0:8]+" "+self.Mode[2])
			self.histo.set_title(self.Mode[0]+' Histogram', size=12)
			self.histo.set_xlabel(self.Mode[1], size=10)
			self.histo.set_ylabel("Samples", size=10)
			pylab.setp(self.histo.get_xticklabels(), fontsize=8)
			pylab.setp(self.histo.get_yticklabels(), fontsize=8)
		self.canvas.draw()
	
	def on_pause_button(self, event):
		self.paused = not self.paused
		
	def clear_data(self, event):
		self.data = []
		
	def setMode(self, event):
		mode = event.GetId()
		if(mode==0):
			self.Mode = ["DC Voltage", "Volts", "V", "dcv"]
		if(mode==1):
			self.Mode = ["DC Current", "Amperes", "A", "dci"]
		if(mode==2):
			self.Mode = ["2-Wire Ohms", "Ohms", u"\u2126", "ohms2"]
		if(mode==3):
			self.Mode = ["4-Wire Ohms", "Ohms", u"\u2126", "ohms4"]
		if(mode==4):
			self.Mode = ["AC Voltage", "Volts", "V", "acv"]
		if(mode==5):
			self.Mode = ["AC Current", "Amperes", "A", "aci"]
		if(mode==6):
			self.Mode = ["DC Couple AC Voltage", "Volts", "V", "acdcv"]
		if(mode==7):
			self.Mode = ["DC Coupled AC Current", "Amperes", "A", "acdci"]
		if(mode==8):
			self.Mode = ["Period", "Seconds", "s", "per"]
		if(mode==9):
			self.Mode = ["Frequency", "Hertz", "Hz", "freq"]
		#hp.setMeasure(self.Mode[3])
		
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
			message="Save plot as...",
			defaultDir=os.getcwd(),
			defaultFile="plot.png",
			wildcard=file_choices,
			style=wx.SAVE)
		if dlg.ShowModal() == wx.ID_OK:
			path = dlg.GetPath()
			self.canvas.print_figure(path, dpi=self.dpi)
		with open("output.csv", "wb") as f:
			writer = csv.writer(f)
			for row in self.data:
				writer.writerow([row])
				
	def on_redraw_timer(self, event):
		if not self.paused:
			add = self.datagen.next()
			self.dataval.add(add)
			self.data.append(add)
		self.draw_plot()
	
	def on_exit(self, event):
		self.Destroy()
	
class Units:
	def __init__(self):
		global si
		si = {
			  -18 : {'multiplier' : 10 ** 18, 'prefix' : 'a'},
			  -17 : {'multiplier' : 10 ** 18, 'prefix' : 'a'},
			  -16 : {'multiplier' : 10 ** 18, 'prefix' : 'a'},
			  -15 : {'multiplier' : 10 ** 15, 'prefix' : 'f'},
			  -14 : {'multiplier' : 10 ** 15, 'prefix' : 'f'},
			  -13 : {'multiplier' : 10 ** 15, 'prefix' : 'f'},
			  -12 : {'multiplier' : 10 ** 12, 'prefix' : 'p'},
			  -11 : {'multiplier' : 10 ** 12, 'prefix' : 'p'},
			  -10 : {'multiplier' : 10 ** 12, 'prefix' : 'p'},
			  -9 : {'multiplier' : 10 ** 9, 'prefix' : 'n'},
			  -8 : {'multiplier' : 10 ** 9, 'prefix' : 'n'},
			  -7 : {'multiplier' : 10 ** 9, 'prefix' : 'n'},
			  -6 : {'multiplier' : 10 ** 6, 'prefix' : u'\u03bc'},
			  -5 : {'multiplier' : 10 ** 6, 'prefix' : u'\u03bc'},
			  -4 : {'multiplier' : 10 ** 6, 'prefix' : u'\u03bc'},
			  -3 : {'multiplier' : 10 ** 3, 'prefix' : 'm'},
			  -2 : {'multiplier' : 10 ** 3, 'prefix' : 'm'},
			  -1 : {'multiplier' : 1, 'prefix' : ''},
			   0 : {'multiplier' : 1, 'prefix' : ''},
			   1 : {'multiplier' : 1, 'prefix' : ''},
			   2 : {'multiplier' : 1, 'prefix' : ''},
			   3 : {'multiplier' : 10 ** 3, 'prefix' : 'k'},
			   4 : {'multiplier' : 10 ** 3, 'prefix' : 'k'},
			   5 : {'multiplier' : 10 ** 3, 'prefix' : 'k'},
			   6 : {'multiplier' : 10 ** 6, 'prefix' : 'M'},
			   7 : {'multiplier' : 10 ** 6, 'prefix' : 'M'},
			   8 : {'multiplier' : 10 ** 6, 'prefix' : 'M'},
			   9 : {'multiplier' : 10 ** 9, 'prefix' : 'G'},
			  10 : {'multiplier' : 10 ** 9, 'prefix' : 'G'},
			  11 : {'multiplier' : 10 ** 9, 'prefix' : 'G'},
			  12 : {'multiplier' : 10 ** 12, 'prefix' : 'T'},
			  13 : {'multiplier' : 10 ** 12, 'prefix' : 'T'},
			  14 : {'multiplier' : 10 ** 12, 'prefix' : 'T'},
			  15 : {'multiplier' : 10 ** 15, 'prefix' : 'P'},
			  16 : {'multiplier' : 10 ** 15, 'prefix' : 'P'},
			  17 : {'multiplier' : 10 ** 15, 'prefix' : 'P'},
			  18 : {'multiplier' : 10 ** 18, 'prefix' : 'E'},
			  }

	def convert(self, number):
		if number < 0:
			negative = True
		else:
			negative = False
		if negative:
			number = number - (number*2)
		exponent = int(math.log10(number))
		if negative:
			number = number - (number*2)
		if exponent < 0:
			exponent = exponent-1
			return [number * si[exponent]['multiplier'], si[exponent]['prefix']]
		elif exponent > 0:
			return [number / si[exponent]['multiplier'], si[exponent]['prefix']]
		elif exponent == 0:
			return [number, '']

if __name__ == '__main__':
	app = wx.App(False)
	app.frame = GraphFrame()
	app.frame.Show()
	app.MainLoop()

