# Digital Multimeter Interface
This project is a Python based user interface for digital multimeters. I built the frontend so that anyone can change the device that it talks to by writing only a couple functions in a class. The frontend uses wxPython for the GUI and Matplotlib for the trend plot and histogram. 

##Features
The most important features are located in the top panel of the interface. These features include the main readout, average, number of samples, minimum, maximum, possible offset based on accuracy specifications, and finally the measurement buttons.
###Offset Values
![offset values](https://raw.githubusercontent.com/md100play/HP3457A-GPIB/master/md/possibility.png)
This section shows the greatest and least possible value of a measurement for a given reading. The offset is based on the worst stated specification of the HP/Agilent 3457A for each range and measurement.  This section is helpful to determine if a meter is within specification or, conversely, if the thing you are measuring is within specification.
