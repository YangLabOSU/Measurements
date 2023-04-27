import pyvisa as visa
import telnet as tn
from pymeasure.instruments.keithley import Keithley2400
import io
import time
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython import display
from UtilsPPMS import *
rm = visa.ResourceManager()
print('Visa Rescource List:')
rm.list_resources()

'''
**************************************************************************************************
PPMS ROTATOR UTILITIES
**************************************************************************************************
updated 4/26/23
Justin Michel
michel.169@osu.edu
'''
# Empty class for dummy connection testing
class Empty: pass

#Check that the Python version is ok:
import sys
if float(sys.version.split(' ')[0].split('.')[0]) >= 3.8:
    raise SystemError('Python 3.7 or less is required to interface with the PPMS. Pythonnet package does not work with newer Python versions.')

'''
**************************************************************************************************
BASIC UTILITY FUNCTIONS
**************************************************************************************************
'''

def print_to_string(*args, **kwargs):
    # Prints the output of print() to a string
    output = io.StringIO()
    print(*args, file=output, **kwargs)
    contents = output.getvalue()
    output.close()
    return contents
    
    
        
'''
CONNECTION DEFINITION CLASSES
'''

class RotPuckConnection:
    # Class for defining instrument properties of rotator puck connections.
    def __init__(self,PuckPinNumber,ConnectionName,SwitchLabel='none'):
        if 7 <= PuckPinNumber <= 14:
            self.PuckPinNumber=PuckPinNumber 
            self.ConnectionName=ConnectionName
            self.BreakoutBoxNumber=self.PuckPinNumber-4
            if SwitchLabel != 'none':
                if not SwitchLabel in ['a','b','c','d','e','f','g','h']:
                    raise ValueError('Switch box connection must be in the top row.')
            self.SwitchLabel=SwitchLabel
        else:
            raise ValueError('Pin number must be between 7 and 14! (use the pin number of the puck when calling this function)')
            
    
class Instrument:
    # Class for defining instrument properties of connected Keithleys.
    def __init__(self,DeviceType,GPIBNumber,DeviceName='Default',SwitchLabels={},Dummy=False):
        self.DeviceType=DeviceType
        self.GPIBNumber=GPIBNumber
        self.Dummy=Dummy
        if self.DeviceType==2182:
            self.addKeithley2182(GPIBNumber,DeviceName=DeviceName,SwitchLabels=SwitchLabels)
        elif self.DeviceType==2400:
            self.addKeithley2400(GPIBNumber,DeviceName=DeviceName,SwitchLabels=SwitchLabels)
        else:
            raise ValueError('Valid Device Types are 2182, 2400.')
            
    def addKeithley2182(self,GPIBNumber,DeviceName='Voltmeter',SwitchLabels={}):
        # Add a Keithley 2182 to the instrument list associated with the breakout box
        if DeviceName == 'Default':
            self.DeviceName = 'Voltmeter'
        else:
            self.DeviceName = DeviceName
        if not self.Dummy:
            self.InstrumentObject=rm.open_resource('GPIB0::{}::INSTR'.format(GPIBNumber))
        else:
            self.InstrumentObject=Empty()
            print('Dummy 2182')
        print('Added Keithley 2182 with name {} and GPIB number {}'.format(self.DeviceName,GPIBNumber))
        if len(SwitchLabels) > 0:
            if len(SwitchLabels) == 2 or 4:
            # If Switchlabels are given of the form
            # {'<Positive connection name>:<Positive connection switch terminal>',
            # <Negative connection name>:<Negative connection switch terminal>}
            # then add these to the Instrument properties
                self.ConnectionNames=list(SwitchLabels)
                self.ConnectionSwitchLabels=list(SwitchLabels.values())
            else:
                raise ValueError('2182 supports only 2 or 4 connections!')
        else:
            self.ConnectionNames=['none defined']
            self.ConnectionSwitchLabels=['none defined']
            
            
    def addKeithley2400(self,GPIBNumber,DeviceName='Default',SwitchLabels={}):
        # Add a Keithley 2400 to the instrument list associated with the breakout box
        if DeviceName == 'Default':
            self.DeviceName = 'CurrentSource'
        else:
            self.DeviceName = DeviceName
        if not self.Dummy:
            self.InstrumentObject=Keithley2400("GPIB::{}".format(GPIBNumber))
        else:
            self.InstrumentObject=Empty()
            print('Dummy 2400')
        print('Added Keithley 2400 with name {} and GPIB number {}'.format(self.DeviceName,GPIBNumber))
        if len(SwitchLabels) > 0:
            if len(SwitchLabels) == 2:
            # If Switchlabels are given of the form
            # {'<Positive connection name>:<Positive connection switch terminal>',
            # <Negative connection name>:<Negative connection switch terminal>}
            # then add these to the Instrument properties
                self.ConnectionNames=list(SwitchLabels)
                self.ConnectionSwitchLabels=list(SwitchLabels.values())
            else:
                raise ValueError('2400 supports only 2 connections!')
        else:
            self.ConnectionNames=['none defined']
            self.ConnectionSwitchLabels=['none defined']
                
        
class BreakoutBoxConnections:
    # Main Class for keeping track of connections to the breakoutbox/ switchbox and PPMS
    def __init__(self):
        self.RotPuckConnectionList=[]
        self.InstrumentList=[]
            
    def addPPMS(self,PPMS_IP='192.168.0.7',Dummy=False):
        # Adds PPMS object and connects to the PPMS, reading current properties. 
        # Call the object with BreakoutBoxConnections.PPMS.<function>
        # See UtilsPPMS.py for function definitions.
        # For code testing, you can use the Dummy flag to make a fake PPMS connection.
        self.PPMS_IP=PPMS_IP
        if not Dummy:
            self.PPMS = Dynacool(PPMS_IP)
            CurrentPosition=self.PPMS.getPosition()
            CurrentTemperature=self.PPMS.getTemperature()
            CurrentField=self.PPMS.getField()
        else:
            self.PPMS=Empty()
            print('DUMMY PPMS')
            CurrentPosition=-999
            CurrentTemperature=-999
            CurrentField=-999
        print('PPMS connection established!')
        print('Current Rotator Position: {}'.format(CurrentPosition))
        print('Current PPMS Temperature: {}'.format(CurrentTemperature))
        print('Current PPMS Field: {}'.format(CurrentField))
        return self.PPMS
            
    def addMatrixSwitch(self,Switch_IP='192.168.0.8', Dummy=False):
        # Adds a matrix switch and gets the current status. Only supports 1 matrix switch for now.
        # For code testing, you can use the Dummy flag to make a fake Switch connection.
        self.Switch_IP=Switch_IP
        if not Dummy:
            self.Switch=tn.telnet(Switch_IP)
            print('Matrix Switch State:')
            self.Switch.getStatus()
        else:
            self.Switch=Empty()
            print('DUMMY Switch')
            print('Matrix Switch State:')
            print('NC')
        return self.Switch
    
    def addInstrument(self,DeviceType,GPIBNumber,DeviceName='Default',SwitchLabels={},Dummy=False):
        # Adds an instrument (Keithley). If the parent BreakoutBoxConnections object has an associated Switch,
        # connections to it and labels can be defined (See Instrument class above for details).
        # If using multiple Current Sources/ Voltmeters, you will want to manually name them, otherwise
        # naming is not necessary, as each different device type will get a unique name.
        if len(SwitchLabels) != 0:
            if not hasattr(self,'Switch'):
                raise ValueError('First add a switch with addMatrixSwitch() before defining switch labels for instruments')
        AddedInstrument=Instrument(DeviceType,GPIBNumber,DeviceName=DeviceName,SwitchLabels=SwitchLabels,Dummy=Dummy)
        self.InstrumentList.append(AddedInstrument)
        return AddedInstrument
        
    def addRotPuckConnection(self,PuckPinNumber,ConnectionName,SwitchLabel='none'):
        # Defines a connection to a rotator puck pin. OPtionally label the switch port that this pin is connected to.
        # (Switch port labelling requires a Switch object definition with addMatrixSwitch first)
        if SwitchLabel != 'none':
            if not hasattr(self,'Switch'):
                raise ValueError('First add a switch with addMatrixSwitch() before defining switch labels for connections')
        self.RotPuckConnectionList.append(RotPuckConnection(PuckPinNumber,ConnectionName,SwitchLabel=SwitchLabel))
        
    def getSwitchPortfromName(self,GivenConnectionName):
        # Function to get the switch port given a connection name.
        # Note that this is general, so it should work both for Rotator puck pin connections and instruments.
        # Also returns the Instrument or Connection object. Checks for duplicates an raises error if not found.
        FoundCount=0
        for RotPuckConnection in self.RotPuckConnectionList:
            if GivenConnectionName == RotPuckConnection.ConnectionName:
                return RotPuckConnection.SwitchLabel, RotPuckConnection
                FoundCount+=1
        for Instrument in self.InstrumentList:
            for i in range(len(Instrument.ConnectionNames)):
                if GivenConnectionName == Instrument.ConnectionNames[i]:
                    return Instrument.ConnectionSwitchLabels[i], Instrument
                    FoundCount+=1
        if FoundCount > 1:
            raise NameError('Found multiple instances of {} in BreakoutBoxConnections!'.format(GivenConnectionName))
        elif FoundCount == 0:
            raise NameError('Could not find any intances of {} in BreakoutBoxConnections!'.format(GivenConnectionName))


    def getInstrumentfromDeviceName(self,name):
        # Function to get an instrument given its Device name.
        FoundInstrument=False
        for i in self.InstrumentList:
            if name in i.DeviceName:
                FoundInstrument = True
                return i
        if not FoundInstrument:
            raise NameError('Could not find {} in InstrumentList'.format(name))

    def __repr__(self):
    # For printing the contents of this class
        OutPString=''
        OutPString += 'list of connected instruments:'
        OutPString += '\nPPMS IP: '
        if hasattr(self,'PPMS_IP'):
            OutPString += self.PPMS_IP
            if isinstance(self.PPMS,Empty):
                OutPString += '\nDUMMY PPMS'
        else:
            OutPString += 'PPMS not added'
        OutPString += '\nSwitch IP: '
        
        if hasattr(self,'Switch_IP'):
            OutPString += self.Switch_IP
            if isinstance(self.Switch,Empty):
                OutPString += '\nDUMMY Switch'
        else:
            OutPString += 'Switch not added'
        for i in self.InstrumentList:
            OutPString += '\n\n\t Device Name:'
            OutPString += i.DeviceName
            if isinstance(i.InstrumentObject,Empty):
                OutPString += '\nDUMMY INSTRUMENT'
            OutPString += '\n\t Device Type:'
            OutPString += str(i.DeviceType)
            OutPString += '\n\t Device GPIB Number:'
            OutPString += str(i.GPIBNumber)
            if len(i.ConnectionNames) > 0:
                OutPString += '\n\t {:20s}{:1s} {:20s}'.format('Connection Name',',','Connection Switch Label')
                for j in range(len(i.ConnectionNames)):
                    OutPString += '\n\t {:20s}{:1s} {:20s}'.format(i.ConnectionNames[j],',',i.ConnectionSwitchLabels[j])
        
        OutPString += '\n\nlist of rotator puck connections:'
        OutPString += '\n\t {:20s}{:1s} {:20s}{:1s} {:20s}{:1s} {:20s}'.format('Connection Name',',','Puck Pin Number',',',
                                                                             'Breakout Box Number',',','Switch Label')
        for i in self.RotPuckConnectionList:
            OutPString += '\n\t {:20s}{:1s} {:20s}{:1s} {:20s}{:1s} {:20s}'.format(i.ConnectionName,',',str(i.PuckPinNumber),
                                                                                 ',',str(i.BreakoutBoxNumber),',',i.SwitchLabel)
                
        return OutPString
        
    
    def getSettingsString(self):
        # Get Class info in string format (for writing to headers or settings files) 
        sets=print_to_string(self)
        return('\n*********************\nConnection Settings:\n*********************\n'+sets)


'''
**************************************************************************************************
MEASUREMENT DEFINITIONS
**************************************************************************************************
'''

class MeasurementConnection:
    # Class defining a measurement connection setup. Use 'Continuous' as the current source if you want the DC measurement 
    # current to be continuous. If this is the case the CurrentAmplitude will be overwritten by the continuous current settings.
    # SwitchConnections is a list of the form ['<ConnectionName1>,<PartenerName1>','<ConnectionName2>,<PartenerName2>']
    # Which defines what connections to make in the switch box. This is optional, and requires a Switch to be added first.
    def __init__(self,MeasurementName,BreakoutBoxConnections,Voltmeter='Voltmeter',CurrentSource='Continuous',CurrentAmplitude=1e-4,SwitchConnections=[]):
        self.MeasurementName=MeasurementName
        self.BreakoutBoxConnections=BreakoutBoxConnections
        # Check if the specified current source  and voltmeter exists
        self.BreakoutBoxConnections.getInstrumentfromDeviceName(CurrentSource)
        self.BreakoutBoxConnections.getInstrumentfromDeviceName(Voltmeter)
        self.Voltmeter=Voltmeter
        self.CurrentSource=CurrentSource
        self.CurrentAmplitude=CurrentAmplitude
        if len(SwitchConnections) > 0:
            if not hasattr(self.BreakoutBoxConnections,'Switch'):
                raise NameError('You must define all connections in BreakoutBoxConnections BEFORE defining the measurement settings! (add a Switch object before you set switch connections)')
            else:
            # Here try to match the given pair of switch port names to the switch port letter addresses.
                self.SwitchPairs=[]
                for Pair in SwitchConnections:
                    First,Second=Pair.split(',')
                    FirstSwitchPort,FirstConnection=self.BreakoutBoxConnections.getSwitchPortfromName(First)
                    SecondSwitchPort,SecondConnection=self.BreakoutBoxConnections.getSwitchPortfromName(Second)
                    self.SwitchPairs.append('{},{}'.format(FirstSwitchPort,SecondSwitchPort))
            self.SwitchConnections=SwitchConnections
            # Make dicts between SwitchConnections and SwitchPairs
            self.SwitchConnectiontoSwitchPairdict=dict(zip(self.SwitchConnections, self.SwitchPairs))
            self.SwitchPairtoSwitchConnectiondict=dict(zip(self.SwitchPairs, self.SwitchConnections))

class MeasurementSettings:
    # This class defines all settings related to running measurements.
    def __init__(self,BreakoutBoxConnections,MeasurementID='',SampleID='',MeasurementNote=''):
        self.MeasurementID=MeasurementID
        self.SampleID=SampleID
        self.MeasurementNote=MeasurementNote
        self.BreakoutBoxConnections=BreakoutBoxConnections
        self.MeasurementConnections=[]
        self.CCFlag=False
        self.setVoltageMeasurementOptions()
        self.setCurrentSourceOptions()
    
    def addMeasurementConnection(self,MeasurementName,Voltmeter='Voltmeter',CurrentSource='CurrentSource',CurrentAmplitude=1e-4,SwitchConnections=[]):
        # Adds a measurement connection setup to the list.if CurrentSource == 'Continuous':
        if CurrentSource=='Continuous':
            if not hasattr(self,'CCAmplitude'):
                raise ValueError('When using "Continuous" as the current source, you must define a continuous current first with setContinuousCurrent(amplitdue)')
        self.MeasurementConnections.append(MeasurementConnection(MeasurementName,self.BreakoutBoxConnections,Voltmeter=Voltmeter,CurrentSource=CurrentSource,CurrentAmplitude=CurrentAmplitude,SwitchConnections=SwitchConnections))
        
    def ListMeasurementNames(self):
        # Gets a list of the measurement names and stores it in self.MeasurementNames.
        # Also returns a dict of MeasurementNames and corresponding MeasurementConnections
        self.MeasurementNames=[]
        for MeasurementConnection in self.MeasurementConnections:
            self.MeasurementNames.append(MeasurementConnection.MeasurementName)
        self.MeasurementNamedict=dict(zip(self.MeasurementNames, self.MeasurementConnections))
        return self.MeasurementNamedict

    def setMeasurementParams(self,Angles,MagneticField,Temperature=300,WaitForSetpoints=True,InitialWaitTime=0,WaitAfterSwitch=0.3, SaveFolder='./data/PPMS_SMR/'):
        # Sets up general measurement parameters
        self.SaveFolder=SaveFolder
        self.Angles=Angles
        self.MagneticField=MagneticField
        self.Temperature=Temperature
        self.WaitForSetpoints=WaitForSetpoints
        self.InitialWaitTime=InitialWaitTime
        self.WaitAfterSwitch=WaitAfterSwitch
        
    def setContinuousCurrent(self,CurrentAmplitude,CurrentSource='CurrentSource'):
        # Defines a current source and amplitude to be run continuously throughout the measurements.
        if not self.BiPolar:
            self.CCFlag=True
            self.CCSource=CurrentSource
            self.CCAmplitude=CurrentAmplitude
        else:
            raise ValueError('Can only set the current source to constant if the voltage measurement is unipolar. Change it with setVoltageMeasurementOptions(BiPolar=False)')
        
    def setVoltageMeasurementOptions(self,NumberofVPoints=30,TimePerPoint=0.1,SkipPoints=5,DropOutliers=3,BiPolar=True, WaitAfterOn=3):
        #Use this function to set custom voltage measurement options. Otherwise the above defaults will be set.
        self.NumberofVPoints=NumberofVPoints
        self.TimePerPoint=TimePerPoint
        self.SkipPoints=SkipPoints
        self.DropOutliers=DropOutliers
        self.BiPolar=BiPolar
        self.WaitAfterOn=WaitAfterOn
        
    def setCurrentSourceOptions(self,SourceCurrentRange=10e-3,SourceComplianceVoltage=20):
        #Use this function to set custom current source options. Otherwise the above defaults will be set.
        self.SourceCurrentRange=SourceCurrentRange
        self.SourceComplianceVoltage=SourceComplianceVoltage

    def ApplyCurrent(self,CurrentSourceInstrument,CurrentAmplitude=1e-5, Verbose=False):
        # Use this function to have the current source output current
        CSIO=CurrentSourceInstrument.InstrumentObject
        if Verbose:
            print('Sourcing Current of {:.1e} from {}'.format(CurrentAmplitude,CurrentSourceInstrument.DeviceName))
        if not isinstance(CurrentSourceInstrument.InstrumentObject,Empty):
            # Check if the instrument is a dummy or not
            CSIO.apply_current()  # Sets up to source current
            CSIO.source_current_range = self.SourceCurrentRange
            CSIO.compliance_voltage = self.SourceComplianceVoltage
            CSIO.source_current = CurrentAmplitude
            CSIO.enable_source()
        time.sleep(self.WaitAfterOn)

    def CurrentOff(self,CurrentSourceInstrument, Verbose=False):
        #Use this function to have the current source turn off its output
        if Verbose:
            print('Stopping output from {}'.format(CurrentSourceInstrument.DeviceName))
        if not isinstance(CurrentSourceInstrument.InstrumentObject,Empty):
            CurrentSourceInstrument.InstrumentObject.shutdown() 

    def MeasureVoltage(self,Voltmeter='Voltmeter', CurrentSource='CurrentSource', CurrentAmplitude=1e-5, Verbose=False):
        #This function measures the voltage and standard deviation at a given Voltmeter. 
        #If the CCFlag is negative, it will first apply a current with the given Current Source

        #First get the Voltmeter and Current Source Instrument objects from the Device Names given.
        VM=self.BreakoutBoxConnections.getInstrumentfromDeviceName(Voltmeter)
        CS=self.BreakoutBoxConnections.getInstrumentfromDeviceName(CurrentSource)

        # Turn on the current if constant current is not set
        if not self.CCFlag:
            self.ApplyCurrent(CS,CurrentAmplitude=CurrentAmplitude, Verbose=Verbose)
        v_up = []
        if Verbose:
            print('Measuring Positive Voltages with {}'.format(VM.DeviceName))

        # Measure the positive current voltages
        for i in range(self.NumberofVPoints):  
            time.sleep(self.TimePerPoint)
            if i < self.SkipPoints:
                continue
            if not isinstance(VM.InstrumentObject,Empty):
            # Only fetch if the instrument object is real, otherwise add -999 V for dummy objects
                v_up.append(float(VM.InstrumentObject.query("fetch?")))
            else:
                v_up.append(-999.0+i)
        # Sort and drop the outliers
        v_up = sorted(v_up)
        v_up = v_up[self.DropOutliers: -self.DropOutliers]
        
        if self.BiPolar:
            if Verbose:
                print('Sourcing Current of {:.1e} from {}'.format(-1 * CurrentAmplitude,CS.DeviceName))

            # If BiPolar flag is true, now measure negative current voltages
            if not isinstance(CS.InstrumentObject,Empty):
                CS.InstrumentObject.source_current = -1 * CurrentAmplitude
                CS.InstrumentObject.enable_source()

            v_dn = []
            if Verbose:
                print('Measuring Negative Voltages with {}'.format(VM.DeviceName))
            for i in range(self.NumberofVPoints):  # Measure for negative current
                time.sleep(self.TimePerPoint)
                if i < self.SkipPoints:
                    continue
                if not isinstance(VM.InstrumentObject,Empty):
                    v_dn.append(float(VM.InstrumentObject.query("fetch?")))
                else:
                    v_dn.append(999.0+i)

            # Turn off the current        
            self.CurrentOff(CS, Verbose=Verbose)
            # Drop outliers
            v_dn = sorted(v_dn)
            v_dn = v_dn[self.DropOutliers: -self.DropOutliers]

            # Take averages for Bipolar setting
            average_v = (np.array(v_up).mean() - np.array(v_dn).mean())/2
            std_v = (np.array(v_up).std() + np.array(v_dn).std())/2
            return average_v, std_v
        else:
            # Turn off the current and do the same for unipolar
            self.CurrentOff(CurrentSource=CurrentSource, Verbose=Verbose)
            average_v = np.array(v_up).mean()
            std_v = np.array(v_up).std()
            return average_v, std_v
            
    def ConnectanddoVoltageMeasurement(self,ConnectionMeasurementName, Verbose=False):
        # Measures the resistance of a given connection and stores it. If switch ports are provided,does switch connection first.
        # First get the MeasurementConnection object from the name
        self.ListMeasurementNames()
        MeasurementConnection=self.MeasurementNamedict[ConnectionMeasurementName]
        if Verbose:
            print('Performing Measurement {}...'.format(ConnectionMeasurementName))
        # If SwitchPairs is defined for the MeasurementConnection, then get first connect those 
        if hasattr(MeasurementConnection,'SwitchPairs'):
            for SwitchPair in MeasurementConnection.SwitchPairs:
                # Check if the Switch is a dummy first
                if not isinstance(self.BreakoutBoxConnections.Switch,Empty):
                    self.BreakoutBoxConnections.Switch.sendCommand('on {}'.format(SwitchPair))
                if Verbose:
                    print('Connected {} corresponding to {} on the SwitchBox.'.format(MeasurementConnection.SwitchPairtoSwitchConnectiondict[SwitchPair],SwitchPair))
                time.sleep(self.WaitAfterSwitch)
        # Measure the resistance
        average_v,std_v=self.MeasureVoltage(Voltmeter=MeasurementConnection.Voltmeter,CurrentSource=MeasurementConnection.CurrentSource, 
                                            CurrentAmplitude=MeasurementConnection.CurrentAmplitude, Verbose=Verbose)
        # Resest the switch again if SwitchPairs is provided
        if hasattr(MeasurementConnection,'SwitchPairs'):
            if not isinstance(self.BreakoutBoxConnections.Switch,Empty):
                self.BreakoutBoxConnections.Switch.sendCommand('reset')
            if Verbose:
                print('Reset the switch')
        return MeasurementConnection.CurrentAmplitude,average_v, std_v

    def RunMeasurement(self):
        #Use this function to run the measurement after you have set it up fully.
        #First set the Temperature 
        self.BreakoutBoxConnections.PPMS.setTemperature(self.Temperature)
        #Then the field
        self.BreakoutBoxConnections.PPMS.setField(self.MagneticField)
        if self.WaitForSetpoints:
            #Wait for them to be reached
            self.BreakoutBoxConnections.PPMS.waitForTemperature()
            self.BreakoutBoxConnections.PPMS.waitForField()
        #Reset Switch conenctions
        self.BreakoutBoxConnections.Switch.sendCommand('reset')
        time.sleep(self.InitialWaitTime)
        name = self.SaveFolder+self.SampleID+"/{}_{}".format(time.strftime("%m%d_%H%M", time.localtime()),self.MeasurementID)
        self.FileName = name+".csv"
        try:
            os.mkdir(self.SaveFolder+self.SampleID)
        except OSError:
            pass
    
        with open(self.FileName, 'a') as f:
            #Write down the settings header for the connections and the measurement
            f.write(self.BreakoutBoxConnections.getSettingsString())
            f.write(self.getSettingsString())
            self.ListMeasurementNames()
            self.DataColumnNames=[]
            for MeasurementName in self.MeasurementNames:
                self.DataColumnNames.append(MeasurementName+'_DC_Current(A)')
                self.DataColumnNames.append(MeasurementName+'_Average_V')
                self.DataColumnNames.append(MeasurementName+'_Std_V')
            f.write("Angle(deg),Temp(K),Field(Oe),{}\n".format(','.join(self.DataColumnNames)))
            
        for angle in self.Angles:
            self.BreakoutBoxConnections.PPMS.setPosition(angle)
            self.BreakoutBoxConnections.PPMS.waitForPosition()
            ang=self.BreakoutBoxConnections.PPMS.getPosition()
            readtemp=self.BreakoutBoxConnections.PPMS.getTemperature()
            readfield=self.BreakoutBoxConnections.PPMS.getField()
            vlist=[]
            for msmt in self.MeasurementConnections:
                if hasattr(msmt,'SwitchPairs'):
                    for i in msmt.SwitchPairs:
                        self.BreakoutBoxConnections.Switch.sendCommand('on {}'.format(i))
                        time.sleep(self.WaitAfterSwitch)
                average_v,std_v=self.MeasureVoltage(Voltmeter=msmt.Voltmeter,CurrentSource=msmt.CurrentSource, CurrentAmplitude=msmt.CurrentAmplitude)
                self.BreakoutBoxConnections.Switch.sendCommand('reset')
                vlist.append(msmt.CurrentAmplitude)
                vlist.append(average_v)
                vlist.append(std_v)
        
            with open(self.FileName, 'a') as f:
                f.write('{},{},{},{}\n'.format(ang,readtemp,readfield,','.join(str(x) for x in vlist)))
            display.clear_output(wait=True)
            PlotSMR(FileName=self.FileName)
            plt.show()
        
        
    def __repr__(self):
    # For printing the contents of this class
        OutPString=''
        OutPString += 'Continuous current?:'
        if self.CCFlag:
            OutPString += 'Yes'
            OutPString += '\nDevice Name: {}'.format(self.CCSource)
            OutPString += '\nCurrent Amplitude: {0:.2f}mA'.format(self.CCAmplitude*1000)
        else:
            OutPString += 'No'
        OutPString += '\n\nMeasurement List:'
        for i in self.MeasurementConnections:
            OutPString += '\n\n\t Measurement Name:'
            OutPString += i.MeasurementName
            OutPString += '\n\t Voltmeter:'
            OutPString += str(i.Voltmeter)
            if not self.CCFlag:
                OutPString += '\n\t Current Source Name: {}'.format(i.CurrentSource)
                OutPString += '\n\t Current Amplitude: {0:.2f}mA'.format(i.CurrentAmplitude*1000)
            if len(i.SwitchConnections) > 0:
                OutPString += '\n\t {:30s}{:14s}:'.format('Switch Connection Pairs','Matrix Switch Addresses')
                for j in range(len(i.SwitchConnections)):
                    OutPString += '\n\t {:8s}{:5s}{:20s}{:3s}{:3s}{:10s}'.format(i.SwitchConnections[j].split(',')[0],',',
                                                                                 i.SwitchConnections[j].split(',')[1],i.SwitchPairs[j].split(',')[0],
                                                                                ',',i.SwitchPairs[j].split(',')[1])
        
        OutPString += '\n\nCurrent Source Settings:'
        OutPString += '\n\ncurrent source range: {0:.1f}(mA)'.format(self.SourceCurrentRange*1e3)
        OutPString += '\ncurrent source compliance voltage: {0:.1f}(V)'.format(self.SourceComplianceVoltage)
        
        OutPString += '\n\nVoltage Measurement Settings:'
        OutPString += '\n\naverage both current polarities?: {}'.format(self.BiPolar)
        OutPString += '\nwait time after current turns on to start measuring: {0:.2f}(s)'.format(self.WaitAfterOn)
        OutPString += '\nnumber of Voltage measurement points per polarity: {}'.format(self.NumberofVPoints)
        OutPString += '\ntime per Voltage measurement point: {0:.2f}(s)'.format(self.TimePerPoint)
        OutPString += '\nnumber of Voltage measurement points to skip at ends: {}'.format(self.SkipPoints)
        OutPString += '\nnumber of Voltage measurement outlier points to drop at each end: {}'.format(self.DropOutliers)
        
        OutPString += '\n\nTiming Settings:'
        OutPString += '\n\nwait for initial setpoints?: {}'.format(self.WaitForSetpoints)
        OutPString += '\nwait time at measurement start: {}'.format(self.InitialWaitTime)
        OutPString += '\nwait time after switching connections: {}'.format(self.WaitAfterSwitch)
        
        OutPString += '\n\nOverall Measurement Settings:'
        OutPString += '\n\nmagnetic field setpoint: {}(Oe)'.format(self.MagneticField)
        OutPString += '\ntemperature setpoint: {}(K)'.format(self.Temperature)
        OutPString += '\nsave folder: \n{}'.format(self.SaveFolder)
        OutPString += '\nmeasurement note: \n{}'.format(self.MeasurementNote)
        OutPString += '\n\nmeasurement ID: {}'.format(self.MeasurementID)
        
        return OutPString
        
    def getSettingsString(self):
        # Get Class info in string format (for writing to headers or settings files) 
        sets=print_to_string(self)
        return('\n*********************\nMeasurement Settings:\n*********************\n'+sets)
        
'''
**************************************************************************************************
DATA ANALYSIS FUNCTIONS
**************************************************************************************************
'''


def PlotSMR(FileName):
    #Plot data
    hlength = 0
    ncorr=0
    measnames=[]
    with open(FileName) as myFile:
        for num, line in enumerate(myFile, 1):
            if line == '\n':
                ncorr+=-1
            if 'Angle(deg)' in line:
                hlength = num-1+ncorr
            if 'Measurement Name:' in line:
                measnames.append(line.split(':')[1].split('\n')[0])
    
    df = pd.read_csv(FileName, header=hlength)
    #print(df)
    
    for measname in measnames:
        cols = [label for label in df.columns if any(x in label for x in [measname+'Average_V', 'Angle', 'Temp','Field'])]
        sdf=df[cols]
        fig,ax=plt.subplots()

        plt.suptitle(FileName.split('/')[-1][:-4]+'_'+measname)
        ax.plot(df['Angle(deg)'],df[measname+'_Average_V']/df[measname+'_DC_Current(A)'], linestyle='-',marker='o', markersize='2',linewidth=1, label=measname)

        ax.set_xlabel('Angle(deg)')
        ax.set_ylabel('$\Omega$')

        ax.legend()
        fig.savefig(FileName[:-4]+'_'+measname+'.png', dpi=600)
        
'''Example Usage:
C=BreakoutBoxConnections()
C.addMatrixSwitch()
C.addPPMS()
C.addRotPuckConnection(7,'HB+', SwitchLabel='a')
C.addRotPuckConnection(8,'HB-', SwitchLabel='b')
C.addRotPuckConnection(9,'HBR1', SwitchLabel='c')
C.addRotPuckConnection(10,'HBL6', SwitchLabel='d')
C.addRotPuckConnection(11,'HBL1', SwitchLabel='e')
C.addRotPuckConnection(12,'HBR6', SwitchLabel='f')
C.addRotPuckConnection(13,'HBL3', SwitchLabel='g')
C.addRotPuckConnection(14,'HBL4', SwitchLabel='h')
C.addInstrument(2400,15,SwitchLabels={'I+':'p','I-':'n'})
C.addInstrument(2182,17,DeviceName='Voltmeter',SwitchLabels={'V1+':'k','V1-':'l'})

#print(C.getSettingsString())

MS=MeasurementSettings(C, MeasurementID='300K_14T_test1', SampleID='LMB713_MnTe(30min)_InP(111)')
MS.setVoltageMeasurementOptions(WaitAfterOn=1)
DC_Current=1e-4
MS.addMeasurementConnection('PtRxy',CurrentAmplitude=DC_Current,SwitchConnections=['HBL1,V1+','HBR1,V1-','HB+,I+','HB-,I-'])
MS.addMeasurementConnection('PtRxx',CurrentAmplitude=DC_Current,SwitchConnections=['HBL1,V1+','HBL3,V1-','HB+,I+','HB-,I-'])
MS.addMeasurementConnection('BareRxx',CurrentAmplitude=DC_Current,SwitchConnections=['HBL4,V1+','HBL6,V1-','HB+,I+','HB-,I-'])
MS.addMeasurementConnection('BareRxy',CurrentAmplitude=DC_Current,SwitchConnections=['HBL6,V1+','HBR6,V1-','HB+,I+','HB-,I-'])
MS.addMeasurementConnection('FullRxx',CurrentAmplitude=DC_Current,SwitchConnections=['HBL1,V1+','HBL6,V1-','HB+,I+','HB-,I-'])

Angles=CreateArrayWithSteps([0,360,0],[5,-5])
MS.setMeasurementParams(Angles,140000,Temperature=300)

#print(MS.getSettingsString())
MS.RunMeasurement()
'''