# Basic utilities for using the Keithley 6221 AC /DC current source
import pyvisa
import time
import numpy as np

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
        self.ac.write("SOUR:CURR:COMP 105")
        if amp > 0:
            firstpoint=1.0
        else:
            firstpoint=-1.0
        self.ac.write("SOUR:WAVE:ARB:DATA {}, 0, 0".format(firstpoint))
        self.ac.write("SOUR:WAVE:FUNC ARB0")
        self.ac.write("SOUR:WAVE:FREQ 1")
        self.ac.write("SOUR:WAVE:OFFS {}".format(offs))
        self.ac.write("SOUR:WAVE:AMPL {}".format(np.abs(amp)))
        self.ac.write("SOUR:WAVE:DUR:TIME {}".format(duration))
        self.ac.write("SOUR:WAVE:ARM")
        time.sleep(wait_after_arm)
        self.ac.write("SOUR:WAVE:INIT")
        
    def PulseDeltaMeasurement(self, amp=1e-5, count=50, width=500e-6, sourcedelay=100e-6, interval=5, range=1):
        # Pulse Delta Measurement
        # To set this up, you need to connect the 6221 to a 2182 with both an RS-232 and trigger link cable.
        # Then set RS-232 communications as defined in the manuals. Lastly, connect only the 6221 to the computer via GPIB.

        self.ac.write('*RST')
        self.ac.write("SYST:COMM:SER:SEND 'VOLT:RANG {}'".format(range))
        #returns 1 if the 6221 finds the 2182 connection via RS-232 (you must also set the connection via front panel with 19.2K baudrate)
        if not self.ac.query('SOUR:DELT:NVPR?').split('/n')[0] == '1':
            RuntimeError('No 2182A connecttion to 6221. Connect with a RS-232 cable and trigger link.')
        self.ac.write('SOUR:PDEL:HIGH {}'.format(amp))
        self.ac.write('SOUR:PDEL:LOW {}'.format(0))
        self.ac.write('SOUR:PDEL:WIDT {}'.format(width))
        self.ac.write('SOUR:PDEL:SDEL {}'.format(sourcedelay))
        self.ac.write('SOUR:PDEL:COUN {}'.format(count))
        self.ac.write('SOUR:PDEL:INT {}'.format(interval))
        self.ac.write('SOUR:PDEL:SWE OFF')
        self.ac.write('TRAC:POIN {}'.format(count))
        self.ac.write('SOUR:PDEL:ARM')
        self.ac.write('INIT:IMM')
        time.sleep(int(count)*int(interval)/60)
        time.sleep(1)
        self.ac.write('SOUR:SWE:ABOR') 
        self.ac.write('CALC2:FORM SDEV')
        self.ac.write('CALC2:STAT ON')
        self.ac.write('CALC2:IMM')
        Vstd=float(self.ac.query('CALC2:DATA?').split('\n')[0])
        self.ac.write('CALC2:FORM MEAN')
        self.ac.write('CALC2:STAT ON')
        self.ac.write('CALC2:IMM')
        Vmean=float(self.ac.query('CALC2:DATA?').split('\n')[0])

        return Vmean, Vstd


"""Example Commands"""

"""
#Open pyvisa rescource manager to check which devices are connected
rm = pyvisa.ResourceManager()
rm.list_resources()
#Connect to the 6221 through GPIB port 16
ac=K6221(GPIBnum=16)
"""