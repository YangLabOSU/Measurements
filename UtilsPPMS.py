import platform, clr, subprocess

"""Connect to the ppms in order to control the field and temperature"""
try: clr.AddReference('QDInstrument')
except Exception as e:
    print("Exception found:", e)
    if clr.FindAssembly('QDInstrument') is None: print('Could not find QDInstrument.dll')
    else:
        print('Found QDInstrument.dll at {}'.format(clr.FindAssembly('QDInstrument')))
        print('Try right-clicking the .dll, selecting "Properties", and then clicking "Unblock"')
        # import the C# classes for interfacing with the PPMS
        #The dll file must be unblocked in the dll file's properties
        
        
"""The control of PPMS field/temperature is given by the manufacturer Quantum Design. 
    They provide Labview packages to interface with the PPMS, and such packages are also 
    included in QDInstrument.dll in the folder with python codes. Each python code loads the dll
    and REGISTERS it as QuantumDesign library and import it
"""
from QuantumDesign.QDInstrument import *

QDI_PPMS_TYPE = QDInstrumentBase.QDInstrumentType.DynaCool
#QDI_FIELD_APPROACH = QDInstrumentBase.FieldApproach.NoOvershoot
QDI_FIELD_APPROACH = QDInstrumentBase.FieldApproach.Linear
QDI_FIELD_MODE = QDInstrumentBase.FieldMode.Persistent
QDI_FIELD_MODE_driven = QDInstrumentBase.FieldMode.Driven
MOVE_TO_POSITION_MODE = QDInstrumentBase.PositionMode.MoveToPosition

DEFAULT_PORT = 11000
QDI_FIELD_STATUS = ['MagnetUnknown', 'StablePersistent', 'StableDriven',
                    'WarmingSwitch', 'CoolingSwitch',
                    'Iterating', 'Charging', 'Discharging',
                    'CurrentError',
                    'Unused9', 'Unused10', 'Unused11', 'Unused12', 'Unused13', 'Unused14',
                    'MagnetFailure']
QDI_TEMP_STATUS = ['TemperatureUnknown',
                    'Stable', 'Tracking',
                    'Unused3', 'Unused4',
                    'Near', 'Chasing', 'Filling',
                    'Unused8', 'Unused9',
                    'Standby',
                    'Unused11', 'Unused12',
                    'Disabled', 'ImpedanceNotFunction', 'TempFailure']
                    
    
PPMS_ComputerIPAddress = "192.168.0.7"
class Dynacool:
    """Thin wrapper around the QuantumDesign.QDInstrument.QDInstrumentBase class"""
    def __init__(self, ip_address):
        self.qdi_instrument = QDInstrumentFactory.GetQDInstrument(QDI_PPMS_TYPE, True, ip_address, DEFAULT_PORT)
        
    """Handle temperature of the PPMS. Get/Set/WaitForStabilizing"""
    def getTemperature(self):
        """Return the current temperature, in Kelvin."""
        return self.qdi_instrument.GetTemperature(0,0)[1]
        
    def setTemperature(self, temp, rate=20):
        """Set temperature. Keyword arguments: temp(Kelvin), rate(K/min)"""
        return self.qdi_instrument.SetTemperature(temp, rate, 0)
        
    def waitForTemperature(self, delay=2, timeout=6000):
        """Pause execution until the PPMS reaches the temperature setpoint."""
        return self.qdi_instrument.WaitFor(True, False, False, False, delay, timeout)
        
    """Handle field of the PPMS. Get/Set/WaitForStabilizing"""
    def getField(self):
        """Return the current field, in gauss."""
        return self.qdi_instrument.GetField(0, 0)[1]
    
    def setField(self, field, rate=100, persistent=False):
        """Set the field. Keyword arguments: field(gauss), rate(gauss/second)"""
        if persistent: return self.qdi_instrument.SetField(field, rate, QDI_FIELD_APPROACH, QDI_FIELD_MODE)
        else: return self.qdi_instrument.SetField(field, rate, QDI_FIELD_APPROACH, QDI_FIELD_MODE_driven)
        
    def waitForField(self, delay=2, timeout=3600):
        """Pause execution until the PPMS reaches the field setpoint."""
        return self.qdi_instrument.WaitFor(False, True, False, False, delay, timeout)

    """Handle motor rotation of the PPMS. Get/Set/WaitForStabilizing"""
    def setPosition(self, position, speed=1): #position: float, deg; speed: float, deg/sec
        return self.qdi_instrument.SetPosition("Horizontal Rotator", position, speed, MOVE_TO_POSITION_MODE)

    def getPosition(self):
        return self.qdi_instrument.GetPosition("Horizontal Rotator",0, 0)[1]

    def waitForPosition(self, delay=2, timeout=1200):
        return self.qdi_instrument.WaitFor(False, False, True, False, delay, timeout)

    
def connect2PPMS(ipAddress=PPMS_ComputerIPAddress):
    #The computer LAN address is 192.168.0.7. The computer server must be up in order to respond to command.
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ["ping", param, '1', ipAddress]
    if subprocess.call(command) == 0:
        ppms = Dynacool(ipAddress)
        print("Successfully pinged the PPMS IP address", ipAddress, "\nThe PPMS:", ppms)
        print("Current field: {}G".format(ppms.getField()[1])) #ppms.getField() returns a tuple 
        print("Current temperature: {}K".format(ppms.getTemperature()[1])) #ppms.getTemperature() returns a tuple 
        return ppms
    else:
        print("Attempt to ping the PPMS computer failed.")
        raise
        
class DummyPPMS:
    def getTemperature(self): return None
    def setTemperature(self, temp, rate=20): return None
    def waitForTemperature(self, delay=5, timeout=6000): return None
    def getField(self): return None
    def setField(self, field, rate=100, persistent=False): return None
    def waitForField(self, delay=5, timeout=3600): return None
    
    