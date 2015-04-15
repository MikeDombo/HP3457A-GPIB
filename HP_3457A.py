import serial

global unit


class hp():
	global unit
	unit = "dcv"

	def __init__(self, com):
		self.gotPlc = False
		self.gotDigits = False
		self.plc = 10
		self.digits = '6.5'
		self.ser = serial.Serial(com, 460800, timeout=3)
		raw_input("press enter to continue END ALWAYS")
		print("Writing +addr 22")
		self.ser.write(b'+addr 22\r')
		print("Asking for ID")
		self.ser.write(b'ID?\r')
		print(self.read())
		raw_input("press enter to continue END ALWAYS")
		print("Writing END ALWAYS")
		self.ser.write(b'END ALWAYS\r')
		raw_input("press enter to continue OFORMAT ASCII")
		print("Writing OFORMAT ASCII")
		self.ser.write(b'OFORMAT ASCII\r')
		raw_input("press enter to continue TRIG SYN")
		print("Writing TRIG SYN")
		self.ser.write(b'TRIG SYN\r')  # Set synchronous trigger so that it triggers when we ask it for data

	def getOffset(self, unit, value):
		digit = self.getDigits()
		plc = str(self.getPlc())
		if float(plc) > 1:
			plc = "1"
		if float(digit) > 6.5:
			digit = '6.5'
		# DC Volts Spec
		dcvRes = {'30mv': {'6.5': 10e-9, '5.5': 100e-9, '4.5': 1e-6, '3.5': 10e-6},
				  '300mv': {'6.5': 100e-9, '5.5': 1e-6, '4.5': 10e-6, '3.5': 100e-6},
				  '3v': {'6.5': 1e-6, '5.5': 10e-6, '4.5': 100e-6, '3.5': 1e-3},
				  '30v': {'6.5': 10e-6, '5.5': 100e-6, '4.5': 1e-3, '3.5': 10e-3},
				  '300v': {'6.5': 100e-6, '5.5': 1e-3, '4.5': 10e-3, '3.5': 100e-3}
				  }
		dcvAcc = {'30mv': {'100': {'acc': .0045, 'counts': 365}, '10': {'acc': .0045, 'counts': 385},
						   '1': {'acc': .0045, 'counts': 500}, '.1': {'acc': .0045, 'counts': 70},
						   '.005': {'acc': .0045, 'counts': 19}, '.0005': {'acc': .0045, 'counts': 6}},
				  '300mv': {'100': {'acc': .0035, 'counts': 39}, '10': {'acc': .0035, 'counts': 40},
							'1': {'acc': .0035, 'counts': 50}, '.1': {'acc': .0035, 'counts': 9},
							'.005': {'acc': .0035, 'counts': 4}, '.0005': {'acc': .0035, 'counts': 4}},
				  '3v': {'100': {'acc': .0025, 'counts': 6}, '10': {'acc': .0025, 'counts': 7},
						 '1': {'acc': .0025, 'counts': 7}, '.1': {'acc': .0025, 'counts': 4},
						 '.005': {'acc': .0025, 'counts': 4}, '.0005': {'acc': .0025, 'counts': 4}},
				  '30v': {'100': {'acc': .0040, 'counts': 19}, '10': {'acc': .0040, 'counts': 20},
						  '1': {'acc': .0040, 'counts': 30}, '.1': {'acc': .0040, 'counts': 7},
						  '.005': {'acc': .0040, 'counts': 4}, '.0005': {'acc': .0040, 'counts': 4}},
				  '300v': {'100': {'acc': .0055, 'counts': 6}, '10': {'acc': .0055, 'counts': 7},
						   '1': {'acc': .0055, 'counts': 7}, '.1': {'acc': .0055, 'counts': 4},
						   '.005': {'acc': .0055, 'counts': 4}, '.0005': {'acc': .0055, 'counts': 4}}
				  }

		#DC Current Spec
		dciRes = {'300ua': {'6.5': 100e-12, '5.5': 1e-9, '4.5': 10e-9, '3.5': 100e-9},
				  '3ma': {'6.5': 1e-9, '5.5': 10e-9, '4.5': 100e-9, '3.5': 1e-6},
				  '30ma': {'6.5': 10e-9, '5.5': 100e-9, '4.5': 1e-6, '3.5': 10e-6},
				  '300ma': {'6.5': 100e-9, '5.5': 1e-6, '4.5': 10e-6, '3.5': 100e-6},
				  '1a': {'6.5': 1e-6, '5.5': 10e-6, '4.5': 100e-6, '3.5': 1e-3}
				  }
		dciAcc = {'300ua': {'100': {'acc': .04, 'counts': 104}, '10': {'acc': .04, 'counts': 104},
							'1': {'acc': .04, 'counts': 115}, '.1': {'acc': .04, 'counts': 14},
							'.005': {'acc': .04, 'counts': 5}, '.0005': {'acc': .04, 'counts': 4}},
				  '3ma': {'100': {'acc': .04, 'counts': 104}, '10': {'acc': .04, 'counts': 104},
						  '1': {'acc': .04, 'counts': 115}, '.1': {'acc': .04, 'counts': 14},
						  '.005': {'acc': .04, 'counts': 5}, '.0005': {'acc': .04, 'counts': 4}},
				  '30ma': {'100': {'acc': .04, 'counts': 104}, '10': {'acc': .04, 'counts': 104},
						   '1': {'acc': .04, 'counts': 115}, '.1': {'acc': .04, 'counts': 14},
						   '.005': {'acc': .04, 'counts': 5}, '.0005': {'acc': .04, 'counts': 4}},
				  '300ma': {'100': {'acc': .08, 'counts': 204}, '10': {'acc': .08, 'counts': 204},
							'1': {'acc': .08, 'counts': 215}, '.1': {'acc': .08, 'counts': 24},
							'.005': {'acc': .08, 'counts': 6}, '.0005': {'acc': .08, 'counts': 4}},
				  '1a': {'100': {'acc': .08, 'counts': 604}, '10': {'acc': .08, 'counts': 604},
						 '1': {'acc': .08, 'counts': 615}, '.1': {'acc': .08, 'counts': 64},
						 '.005': {'acc': .08, 'counts': 10}, '.0005': {'acc': .08, 'counts': 5}}
				  }

		#2-wire and 4-wire ohms
		ohmsRes = {'30': {'6.5': 10e-6, '5.5': 100e-6, '4.5': 1e-3, '3.5': 10e-3},
				   '300': {'6.5': 100e-6, '5.5': 1e-3, '4.5': 10e-3, '3.5': 100e-3},
				   '3k': {'6.5': 1e-3, '5.5': 10e-3, '4.5': 100e-3, '3.5': 1},
				   '30k': {'6.5': 10e-3, '5.5': 100e-3, '4.5': 1, '3.5': 10},
				   '300k': {'6.5': 100e-3, '5.5': 1, '4.5': 10, '3.5': 100},
				   '3m': {'6.5': 1, '5.5': 10, '4.5': 100, '3.5': 1e3},
				   '30m': {'6.5': 10, '5.5': 100, '4.5': 1e3, '3.5': 10e3},
				   '300m': {'6.5': 100, '5.5': 1e3, '4.5': 10e3, '3.5': 100e3},
				   '3g': {'6.5': 1e3, '5.5': 10e3, '4.5': 100e3, '3.5': 1e6}
				   }
		ohms4Acc = {'30': {'100': {'acc': .0075, 'counts': 315}, '10': {'acc': .0075, 'counts': 335},
						   '1': {'acc': .0075, 'counts': 450}, '.1': {'acc': .0075, 'counts': 65},
						   '.0075': {'acc': .0075, 'counts': 18}, '.0005': {'acc': .0075, 'counts': 6}},
					'300': {'100': {'acc': .0055, 'counts': 34}, '10': {'acc': .0055, 'counts': 35},
							'1': {'acc': .0055, 'counts': 45}, '.1': {'acc': .0055, 'counts': 8},
							'.0055': {'acc': .0055, 'counts': 4}, '.0005': {'acc': .0055, 'counts': 4}},
					'3k': {'100': {'acc': .005, 'counts': 6}, '10': {'acc': .005, 'counts': 7},
						   '1': {'acc': .005, 'counts': 7}, '.1': {'acc': .005, 'counts': 4},
						   '.005': {'acc': .005, 'counts': 4}, '.0005': {'acc': .005, 'counts': 4}},
					'30k': {'100': {'acc': .005, 'counts': 6}, '10': {'acc': .005, 'counts': 7},
							'1': {'acc': .005, 'counts': 7}, '.1': {'acc': .005, 'counts': 4},
							'.005': {'acc': .005, 'counts': 4}, '.0005': {'acc': .005, 'counts': 4}},
					'300k': {'100': {'acc': .005, 'counts': 7}, '10': {'acc': .005, 'counts': 8},
							 '1': {'acc': .005, 'counts': 9}, '.1': {'acc': .005, 'counts': 4},
							 '.005': {'acc': .005, 'counts': 4}, '.0005': {'acc': .005, 'counts': 4}},
					'3m': {'100': {'acc': .0065, 'counts': 12}, '10': {'acc': .0065, 'counts': 14},
						   '1': {'acc': .0065, 'counts': 16}, '.1': {'acc': .0065, 'counts': 7},
						   '.0065': {'acc': .0065, 'counts': 5}, '.0005': {'acc': .0065, 'counts': 5}},
					'30m': {'100': {'acc': .04, 'counts': 80}, '10': {'acc': .04, 'counts': 83},
							'1': {'acc': .04, 'counts': 93}, '.1': {'acc': .04, 'counts': 14},
							'.04': {'acc': .04, 'counts': 6}, '.0005': {'acc': .04, 'counts': 5}}
					}
		ohms2Acc = {'30': {'100': {'acc': .0075, 'counts': 20315}, '10': {'acc': .0075, 'counts': 20335},
						   '1': {'acc': .0075, 'counts': 20450}, '.1': {'acc': .0075, 'counts': 20065},
						   '.0075': {'acc': .0075, 'counts': 20018}, '.0005': {'acc': .0075, 'counts': 20006}},
					'300': {'100': {'acc': .0055, 'counts': 2034}, '10': {'acc': .0055, 'counts': 2035},
							'1': {'acc': .0055, 'counts': 2045}, '.1': {'acc': .0055, 'counts': 2008},
							'.0055': {'acc': .0055, 'counts': 2004}, '.0005': {'acc': .0055, 'counts': 2004}},
					'3k': {'100': {'acc': .005, 'counts': 206}, '10': {'acc': .005, 'counts': 207},
						   '1': {'acc': .005, 'counts': 207}, '.1': {'acc': .005, 'counts': 204},
						   '.005': {'acc': .005, 'counts': 204}, '.0005': {'acc': .005, 'counts': 204}},
					'30k': {'100': {'acc': .005, 'counts': 26}, '10': {'acc': .005, 'counts': 27},
							'1': {'acc': .005, 'counts': 27}, '.1': {'acc': .005, 'counts': 24},
							'.005': {'acc': .005, 'counts': 24}, '.0005': {'acc': .005, 'counts': 24}},
					'300k': {'100': {'acc': .005, 'counts': 9}, '10': {'acc': .005, 'counts': 10},
							 '1': {'acc': .005, 'counts': 11}, '.1': {'acc': .005, 'counts': 6},
							 '.005': {'acc': .005, 'counts': 6}, '.0005': {'acc': .005, 'counts': 6}},
					'3m': {'100': {'acc': .0065, 'counts': 12}, '10': {'acc': .0065, 'counts': 14},
						   '1': {'acc': .0065, 'counts': 16}, '.1': {'acc': .0065, 'counts': 7},
						   '.0065': {'acc': .0065, 'counts': 5}, '.0005': {'acc': .0065, 'counts': 5}},
					'30m': {'100': {'acc': .04, 'counts': 80}, '10': {'acc': .04, 'counts': 83},
							'1': {'acc': .04, 'counts': 93}, '.1': {'acc': .04, 'counts': 14},
							'.04': {'acc': .04, 'counts': 6}, '.0005': {'acc': .04, 'counts': 5}},
					'300m': {'100': {'acc': 1.6, 'counts': 1000}, '10': {'acc': 1.6, 'counts': 1000},
							 '1': {'acc': 1.6, 'counts': 1000}, '.1': {'acc': 1.6, 'counts': 100},
							 '1.6': {'acc': 1.6, 'counts': 10}, '.0005': {'acc': 1.6, 'counts': 1}},
					'3g': {'100': {'acc': 16, 'counts': 1000}, '10': {'acc': 16, 'counts': 1000},
						   '1': {'acc': 16, 'counts': 1000}, '.1': {'acc': 16, 'counts': 100},
						   '16': {'acc': 16, 'counts': 10}, '.0005': {'acc': 16, 'counts': 1}}
					}

		#AC Voltage Spec 		90 day spec
		acvRes = {'30mv': {'6.5': 10e-9, '5.5': 100e-9, '4.5': 1e-6, '3.5': 10e-6},
				  '300mv': {'6.5': 100e-9, '5.5': 1e-6, '4.5': 10e-6, '3.5': 100e-6},
				  '3v': {'6.5': 1e-6, '5.5': 10e-6, '4.5': 100e-6, '3.5': 1e-3},
				  '30v': {'6.5': 10e-6, '5.5': 100e-6, '4.5': 1e-3, '3.5': 10e-3},
				  '300v': {'6.5': 100e-6, '5.5': 1e-3, '4.5': 10e-3, '3.5': 100e-3}
				  }
		acvLoAcc = {
		'20': {'1': {'acc': .62, 'counts': 1120}, '.1': {'acc': .62, 'counts': 116}, '.005': {'acc': .62, 'counts': 16},
			   '.0005': {'acc': .62, 'counts': 6}},
		'45': {'1': {'acc': .21, 'counts': 1120}, '.1': {'acc': .21, 'counts': 116}, '.005': {'acc': .21, 'counts': 16},
			   '.0005': {'acc': .21, 'counts': 6}},
		'100': {'1': {'acc': .13, 'counts': 1120}, '.1': {'acc': .13, 'counts': 116},
				'.005': {'acc': .13, 'counts': 16}, '.0005': {'acc': .13, 'counts': 6}},
		'400': {'1': {'acc': .14, 'counts': 1120}, '.1': {'acc': .14, 'counts': 550},
				'.005': {'acc': .14, 'counts': 59}, '.0005': {'acc': .14, 'counts': 10}},
		'20000': {'1': {'acc': .66, 'counts': 2100}, '.1': {'acc': .66, 'counts': 224},
				  '.005': {'acc': .66, 'counts': 27}, '.0005': {'acc': .66, 'counts': 7}},
		'100000': {'1': {'acc': 3.16, 'counts': 9700}, '.1': {'acc': 3.16, 'counts': 974},
				   '.005': {'acc': 3.16, 'counts': 102}, '.0005': {'acc': 3.16, 'counts': 14}},
		'300000': {'1': {'acc': 10.16, 'counts': 66400}, '.1': {'acc': 10.16, 'counts': 6640},
				   '.005': {'acc': 10.16, 'counts': 668}, '.0005': {'acc': 10.16, 'counts': 71}}
		}
		acvHiAcc = {
		'20': {'1': {'acc': .62, 'counts': 1120}, '.1': {'acc': .62, 'counts': 116}, '.005': {'acc': .62, 'counts': 16},
			   '.0005': {'acc': .62, 'counts': 6}},
		'45': {'1': {'acc': .27, 'counts': 1120}, '.1': {'acc': .27, 'counts': 116}, '.005': {'acc': .27, 'counts': 16},
			   '.0005': {'acc': .27, 'counts': 6}},
		'100': {'1': {'acc': .19, 'counts': 1120}, '.1': {'acc': .19, 'counts': 116},
				'.005': {'acc': .19, 'counts': 16}, '.0005': {'acc': .19, 'counts': 6}},
		'400': {'1': {'acc': .2, 'counts': 1120}, '.1': {'acc': .2, 'counts': 550}, '.005': {'acc': .2, 'counts': 59},
				'.0005': {'acc': .2, 'counts': 10}},
		'20000': {'1': {'acc': 1.06, 'counts': 3700}, '.1': {'acc': 1.06, 'counts': 374},
				  '.005': {'acc': 1.06, 'counts': 42}, '.0005': {'acc': 1.06, 'counts': 8}}
		}

		#AC DC coupled Voltage Spec		90 day spec
		acdcvLoAcc = {'20': {'1': {'acc': 1.36, 'counts': 3600}, '.1': {'acc': 1.36, 'counts': 364},
							 '.005': {'acc': 1.36, 'counts': 41}, '.0005': {'acc': 1.36, 'counts': 8}},
					  '45': {'1': {'acc': .17, 'counts': 3600}, '.1': {'acc': .17, 'counts': 364},
							 '.005': {'acc': .17, 'counts': 41}, '.0005': {'acc': .17, 'counts': 8}},
					  '100': {'1': {'acc': .17, 'counts': 3600}, '.1': {'acc': .17, 'counts': 364},
							  '.005': {'acc': .17, 'counts': 41}, '.0005': {'acc': .17, 'counts': 8}},
					  '400': {'1': {'acc': .44, 'counts': 3600}, '.1': {'acc': .44, 'counts': 2810},
							  '.005': {'acc': .44, 'counts': 285}, '.0005': {'acc': .44, 'counts': 33}},
					  '20000': {'1': {'acc': .66, 'counts': 4620}, '.1': {'acc': .66, 'counts': 466},
								'.005': {'acc': .66, 'counts': 51}, '.0005': {'acc': .66, 'counts': 9}},
					  '100000': {'1': {'acc': 3.16, 'counts': 11400}, '.1': {'acc': 3.16, 'counts': 1144},
								 '.005': {'acc': 3.16, 'counts': 119}, '.0005': {'acc': 3.16, 'counts': 16}},
					  '300000': {'1': {'acc': 10.16, 'counts': 69600}, '.1': {'acc': 10.16, 'counts': 6960},
								 '.005': {'acc': 10.16, 'counts': 701}, '.0005': {'acc': 10.16, 'counts': 74}}
					  }
		acdcvHiAcc = {'20': {'1': {'acc': 1.36, 'counts': 3600}, '.1': {'acc': 1.36, 'counts': 364},
							 '.005': {'acc': 1.36, 'counts': 41}, '.0005': {'acc': 1.36, 'counts': 8}},
					  '45': {'1': {'acc': .23, 'counts': 3600}, '.1': {'acc': .23, 'counts': 364},
							 '.005': {'acc': .23, 'counts': 41}, '.0005': {'acc': .23, 'counts': 8}},
					  '100': {'1': {'acc': .23, 'counts': 3600}, '.1': {'acc': .23, 'counts': 364},
							  '.005': {'acc': .23, 'counts': 41}, '.0005': {'acc': .23, 'counts': 8}},
					  '400': {'1': {'acc': .5, 'counts': 3600}, '.1': {'acc': .5, 'counts': 2810},
							  '.005': {'acc': .5, 'counts': 285}, '.0005': {'acc': .5, 'counts': 33}},
					  '20000': {'1': {'acc': 1.16, 'counts': 6420}, '.1': {'acc': 1.16, 'counts': 650},
								'.005': {'acc': 1.16, 'counts': 69}, '.0005': {'acc': 1.16, 'counts': 11}}
					  }


		#AC Current Spec	90 day spec
		aciRes = {'30ma': {'6.5': 10e-9, '5.5': 100e-9, '4.5': 1e-6, '3.5': 10e-6},
				  '300ma': {'6.5': 100e-9, '5.5': 1e-6, '4.5': 10e-6, '3.5': 100e-6},
				  '1a': {'6.5': 1e-6, '5.5': 10e-6, '4.5': 100e-6, '3.5': 1e-3}}
		aciLoAcc = {
		'20': {'1': {'acc': .85, 'counts': 2800}, '.1': {'acc': .85, 'counts': 290}, '.005': {'acc': .85, 'counts': 32},
			   '.0005': {'acc': .85, 'counts': 7}},
		'45': {'1': {'acc': .3, 'counts': 2800}, '.1': {'acc': .3, 'counts': 290}, '.005': {'acc': .3, 'counts': 32},
			   '.0005': {'acc': .3, 'counts': 7}},
		'100': {'1': {'acc': .25, 'counts': 2800}, '.1': {'acc': .25, 'counts': 290},
				'.005': {'acc': .25, 'counts': 32}, '.0005': {'acc': .25, 'counts': 7}},
		'400': {'1': {'acc': .25, 'counts': 2800}, '.1': {'acc': .25, 'counts': 750},
				'.005': {'acc': .25, 'counts': 80}, '.0005': {'acc': .25, 'counts': 12}},
		'20000': {'1': {'acc': 1, 'counts': 4000}, '.1': {'acc': 1, 'counts': 400}, '.005': {'acc': 1, 'counts': 42},
				  '.0005': {'acc': 1, 'counts': 8}}}
		aciHiAcc = {
		'20': {'1': {'acc': .95, 'counts': 2800}, '.1': {'acc': .95, 'counts': 290}, '.005': {'acc': .95, 'counts': 32},
			   '.0005': {'acc': .95, 'counts': 7}},
		'45': {'1': {'acc': .4, 'counts': 2800}, '.1': {'acc': .4, 'counts': 290}, '.005': {'acc': .4, 'counts': 32},
			   '.0005': {'acc': .4, 'counts': 7}},
		'100': {'1': {'acc': .35, 'counts': 2800}, '.1': {'acc': .35, 'counts': 290},
				'.005': {'acc': .35, 'counts': 32}, '.0005': {'acc': .35, 'counts': 7}},
		'400': {'1': {'acc': .35, 'counts': 2800}, '.1': {'acc': .35, 'counts': 750},
				'.005': {'acc': .35, 'counts': 80}, '.0005': {'acc': .35, 'counts': 12}}}


		#AC DC coupled Current Spec 	90 day spec
		acdciLoAcc = {'20': {'1': {'acc': 1.55, 'counts': 16000}, '.1': {'acc': 1.55, 'counts': 1600},
							 '.005': {'acc': 1.55, 'counts': 165}, '.0005': {'acc': 1.55, 'counts': 20}},
					  '45': {'1': {'acc': .4, 'counts': 16000}, '.1': {'acc': .4, 'counts': 1600},
							 '.005': {'acc': .4, 'counts': 165}, '.0005': {'acc': .4, 'counts': 20}},
					  '100': {'1': {'acc': .3, 'counts': 16000}, '.1': {'acc': .3, 'counts': 1600},
							  '.005': {'acc': .3, 'counts': 165}, '.0005': {'acc': .3, 'counts': 20}},
					  '400': {'1': {'acc': .65, 'counts': 16000}, '.1': {'acc': .65, 'counts': 3750},
							  '.005': {'acc': .65, 'counts': 375}, '.0005': {'acc': .65, 'counts': 42}},
					  '20000': {'.95': {'acc': .95, 'counts': 17500}, '..95': {'acc': .95, 'counts': 1750},
								'.005': {'acc': .95, 'counts': 180}, '.0005': {'acc': .95, 'counts': 22}}}
		acdciHiAcc = {'20': {'1': {'acc': 1.65, 'counts': 16000}, '.1': {'acc': 1.65, 'counts': 1600},
							 '.005': {'acc': 1.65, 'counts': 165}, '.0005': {'acc': 1.65, 'counts': 20}},
					  '45': {'1': {'acc': .5, 'counts': 16000}, '.1': {'acc': .5, 'counts': 1600},
							 '.005': {'acc': .5, 'counts': 165}, '.0005': {'acc': .5, 'counts': 20}},
					  '100': {'1': {'acc': .4, 'counts': 16000}, '.1': {'acc': .4, 'counts': 1600},
							  '.005': {'acc': .4, 'counts': 165}, '.0005': {'acc': .4, 'counts': 20}},
					  '400': {'1': {'acc': .75, 'counts': 16000}, '.1': {'acc': .75, 'counts': 3750},
							  '.005': {'acc': .75, 'counts': 375}, '.0005': {'acc': .75, 'counts': 42}}}

		#Frequency Spec
		freqAcc = {'10': .05, '400': .01}

		if (unit == "dcv"):
			if (value < 30.3e-3):
				range = '30mv'
			elif (value < 303e-3):
				range = '300mv'
			elif (value < 3.03):
				range = '3v'
			elif (value < 30.3):
				range = '30v'
			elif (value < 303):
				range = '300v'
			return ((value * dcvAcc[range][plc]['acc']) + dcvRes[range][digit] * dcvAcc[range][plc]['counts'])
		elif (unit == "dci"):
			if (value < 303e-6):
				range = '300ua'
			elif (value < 3.03e-3):
				range = '3ma'
			elif (value < 30.3e-3):
				range = '30ma'
			elif (value < 303e-3):
				range = '300ma'
			else:
				range = '1a'
			return ((value * dciAcc[range][plc]['acc']) + dciRes[range][digit] * dciAcc[range][plc]['counts'])
		elif (unit == "ohms2"):
			if (value < 30.3):
				range = '30'
			elif (value < 303):
				range = '300'
			elif (value < 3.03e3):
				range = '3k'
			elif (value < 30.3e3):
				range = '30k'
			elif (value < 303e3):
				range = '300k'
			elif (value < 3.03e6):
				range = '3m'
			elif (value < 30.3e6):
				range = '30m'
			elif (value < 303e6):
				range = '300m'
			elif (value < 3.03e12):
				range = '3g'
			return ((value * ohms2Acc[range][plc]['acc']) + ohmsRes[range][digit] * ohms2Acc[range][plc]['counts'])
		elif (unit == "ohms4"):
			if (value < 30.3):
				range = '30'
			elif (value < 303):
				range = '300'
			elif (value < 3.03e3):
				range = '3k'
			elif (value < 30.3e3):
				range = '30k'
			elif (value < 303e3):
				range = '300k'
			elif (value < 3.03e6):
				range = '3m'
			elif (value < 30.3e6):
				range = '30m'
			elif (value < 303e6):
				range = '300m'
			elif (value < 3.03e12):
				range = '3g'
			return ((value * ohms4Acc[range][plc]['acc']) + ohmsRes[range][digit] * ohms4Acc[range][plc]['counts'])
		elif (unit == "acv"):
			if (float(plc) > 1): plc = '1'
			freq = self.getFrequency()
			if (freq < 45):
				freq = '20'
			elif (freq < 100):
				freq = '45'
			elif (freq < 400):
				freq = '100'
			elif (freq < 20000):
				freq = '400'
			elif (freq < 100000):
				freq = '20000'
			elif (freq < 1000000):
				freq = '300000'
			if (value < 32.5e-3):
				range = '30mv'
			elif (value < 325e-3):
				range = '300mv'
			elif (value < 3.25):
				range = '3v'
			elif (value < 32.5):
				range = '30v'
			elif (value < 303):
				range = '300v'
			if (value > 32.5):
				acvAcc = acvHiAcc
			else:
				acvAcc = acvLoAcc
			return ((value * acvAcc[freq][plc]['acc']) + acvRes[range][digit] * acvAcc[freq][plc]['counts'])
		elif (unit == "acdcv"):
			if (float(plc) > 1): plc = '1'
			freq = self.getFrequency()
			if (freq < 45):
				freq = '20'
			elif (freq < 100):
				freq = '45'
			elif (freq < 400):
				freq = '100'
			elif (freq < 20000):
				freq = '400'
			elif (freq < 100000):
				freq = '20000'
			elif (freq < 1000000):
				freq = '300000'
			if (value < 32.5e-3):
				range = '30mv'
			elif (value < 325e-3):
				range = '300mv'
			elif (value < 3.25):
				range = '3v'
			elif (value < 32.5):
				range = '30v'
			elif (value < 303):
				range = '300v'
			if (value > 32.5):
				acdcvAcc = acdcvHiAcc
			else:
				acdcvAcc = acdcvLoAcc
			return ((value * acdcvAcc[freq][plc]['acc']) + acvRes[range][digit] * acdcvAcc[freq][plc]['counts'])
		elif (unit == "aci"):
			if (float(plc) > 1): plc = '1'
			freq = self.getFrequency()
			if (freq < 45):
				freq = '20'
			elif (freq < 100):
				freq = '45'
			elif (freq < 400):
				freq = '100'
			elif (freq < 20000):
				freq = '400'
			elif (freq < 100000):
				freq = '20000'
			if (value < 30.3e-3):
				range = '30ma'
			elif (value < 303e-3):
				range = '300ma'
			if (value > 303e-3):
				range = '1a'
				aciAcc = aciHiAcc
			else:
				aciAcc = aciLoAcc
			return ((value * aciAcc[freq][plc]['acc']) + aciRes[range][digit] * aciAcc[freq][plc]['counts'])
		elif (unit == "acdci"):
			if (float(plc) > 1): plc = '1'
			freq = self.getFrequency()
			if (freq < 45):
				freq = '20'
			elif (freq < 100):
				freq = '45'
			elif (freq < 400):
				freq = '100'
			elif (freq < 20000):
				freq = '400'
			elif (freq < 100000):
				freq = '20000'
			if (value < 30.3e-3):
				range = '30ma'
			elif (value < 303e-3):
				range = '300ma'
			if (value > 303e-3):
				range = '1a'
				acdciAcc = acdciHiAcc
			else:
				acdciAcc = acdciLoAcc
			return ((value * acdciAcc[freq][plc]['acc']) + aciRes[range][digit] * acdciAcc[freq][plc]['counts'])
		elif (unit == "freq"):
			if (value < 400):
				range = '10'
			else:
				range = '400'
			return (value * freqAcc[range])
		elif (unit == "per"):
			freq = self.getFrequency()
			if (freq < 400):
				range = '10'
			else:
				range = '400'
			return (value * freqAcc[range])

	def getFrequency(self):
		global unit
		units = unit
		self.setMeasure("freq")
		freq = self.measure()
		self.setMeasure(units)
		return freq
		
	def read(self):
		self.ser.write(b'+read')
		return self.read()
		
	def measure(self):
		self.ser.flushInput()
		print("Trying to get measurement")
		raw_input("press enter to continue TRIG SGL")
		self.ser.write(b'TRIG SGL\r')
		if float(self.digits) > 6.5:
			print("Reading Serial Line1")
			value = self.read()
			print(value)
			self.ser.write(b'RMATH HIRES\r')
			hire = self.read()
			print(hire)
			while self.ser.inWaiting()>0:
				print(self.read())
			return float(value) + float(hire)
		print("Reading serial line2")
		value = self.read()
		print(value)
		while self.ser.inWaiting()>0:
				print(self.read())
		return float(value)

	def getPlc(self):
		if self.gotPlc:
			return self.plc
		else:
			print("Writing NPLC?")
			self.ser.write(b'NPLC?\r')
			print("Reading NPLC? answer")
			self.plc = self.read()
			self.gotPlc = True
			return self.plc

	def getDigits(self):
		if self.gotDigits:
			return self.digits
		else:
			self.ser.write(b'NPLC?')
			self.digits = self.read()
			if float(self.digits) <= .0005:
				self.digits = '3.5'
			elif float(self.digits) <= .005:
				self.digits = '4.5'
			elif float(self.digits) <= .1:
				self.digits = '5.5'
			elif float(self.digits) <= 1:
				self.digits = '6.5'
			elif float(self.digits) <= 10:
				self.digits = '7.5'
			elif float(self.digits) <= 100:
				self.digits = '7.5'
			self.gotDigits = True
			return self.digits

	def setMeasure(self, units):
		global unit
		unit = units
		if (unit == "dcv"):
			self.ser.write(b'F10')
		elif (unit == "dci"):
			self.ser.write(b'DCI')
		elif (unit == "ohms2"):
			self.ser.write(b'F40')
		elif (unit == "ohms4"):
			self.ser.write(b'F50')
		elif (unit == "acv"):
			self.ser.write(b'ACV')
		elif (unit == "acdcv"):
			self.ser.write(b'ACDCV')
		elif (unit == "aci"):
			self.ser.write(b'ACI')
		elif (unit == "acdci"):
			self.ser.write(b'ACDCI')
		elif (unit == "freq"):
			self.ser.write(b'FREQ')
		elif (unit == "per"):
			self.ser.write(b'PER')

	def setGPIBAddr(self, addr):
		self.ser.write(b'+addr ' + addr)
		self.ser.write(b'OFORMAT ASCII')

	def getNPLC(self):
		self.ser.write(b'NPLC?')
		self.NPLC = self.read()
		return self.NPLC