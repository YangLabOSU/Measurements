# Basic utilities for using the Keithley 6221 AC /DC current source
import pyvisa
import time

class K6221:
    """Class for Keithley 6221"""
    def __init__(self, GPIBnum=16):
        #Initialize the 6221 connection through specified GPIB port
        rm = pyvisa.ResourceManager()
        self.ac = rm.open_resource('GPIB0::{}::INSTR'.format(GPIBnum))
        
    def sinOut(self, amp=1e-5, duration='INF' ,freq=17e3, offs=0, wait_after_arm=2):
        #Trigger a sine wave output from the 6221(Useful for Lock-in measurements)
        self.ac.write("SOUR:WAVE:ABOR")
        self.ac.write("SOUR:WAVE:FUNC SIN")
        self.ac.write("SOUR:WAVE:FREQ {}".format(freq))
        self.ac.write("SOUR:WAVE:OFFS {}".format(offs))
        self.ac.write("SOUR:WAVE:AMPL {}".format(amp))
        self.ac.write("SOUR:WAVE:DUR:TIME {}".format(duration))
        """For lock-in measurements, we want the Phase marker on and 
        on pin 1 of the trigger link cable (connect VMC to REF IN on the Lock-in)"""
        self.ac.write("SOUR:WAVE:PMAR 180")
        self.ac.write("SOUR:WAVE:PMAR:STAT ON")
        self.ac.write("SOUR:WAVE:PMAR:OLIN 1")
        self.ac.write("SOUR:WAVE:ARM")
        time.sleep(wait_after_arm)
        self.ac.write("SOUR:WAVE:INIT")
        
    def pulseOut(self, amp=1e-5, duration=1e-3, offs=0, wait_after_arm=2):
        #Trigger a square pulse output from the 6221 (Useful for switching measurements)
        self.ac.write("SOUR:WAVE:ABOR")
        self.ac.write("SOUR:WAVE:FUNC SQUARE")
        self.ac.write("SOUR:WAVE:FREQ 1")
        self.ac.write("SOUR:WAVE:OFFS {}".format(offs))
        self.ac.write("SOUR:WAVE:AMPL {}".format(amp))
        self.ac.write("SOUR:WAVE:DUR:TIME {}".format(duration))
        self.ac.write("SOUR:WAVE:ARM")
        time.sleep(wait_after_arm)
        self.ac.write("SOUR:WAVE:INIT")


"""Example Commands"""

"""
#Open pyvisa rescource manager to check which devices are connected
rm = pyvisa.ResourceManager()
rm.list_resources()
#Connect to the 6221 through GPIB port 16
ac=K6221(GPIBnum=16)
"""