'''
//****************************************************//
//        Module: TELNETlinkbone.py                   //
//        Author: Marcin Debski                       //
//        XLR Switch or BNC Switch module for remote  //
//        control via Telnet                          //
//        www.linkbone.com                            //
//****************************************************//
'''
 
import time
import threading
import telnetlib
 
class telnet:
    def __init__(self, ip):
        self.ip = ip
        try:
            tn = telnetlib.Telnet(ip)
            print("Telnet connection to LinkBone has been established!")
            self.tn = tn
            self.thread = threading.Timer(30, self.pingSwitch)
            self.run = 1
            self.thread.start()
            tn.read_until(b'Hello. Please enter your command:')
        except:
            print("Cannot connect via telnet to LinkBone!")
 
    # keep telnet connection alive to XLR switch or BNC switch
    def pingSwitch(self):
        try:
            while self.run:
                self.tn.write(b'ping\n')
                self.tn.read_until(b'Pong.')
                time.sleep(30)
        except:
            pass
 
    # print information about status of the XLR switch or BNC switch
    def getStatus(self):
        self.tn.write(b'status\r')
        time.sleep(1)
        while 1:
            status = self.tn.read_very_eager()
            if status:
                print(status.decode())
            else:
                break
 
    # print list of available commands
    def getHelp(self):
        self.tn.write(b'help\r')
        time.sleep(1)
        while 1:
            status = self.tn.read_very_eager()
            if status:
                print(status.decode())
            else:
                break
 
    # print information about XLR switch or BNC switch device
    def getInfo(self):
        self.tn.write(b'info\r')
        time.sleep(1)
        while 1:
            status = self.tn.read_very_eager()
            if status:
                print(status.decode())
            else:
                break
 
    # send text command to LinkBone XLR switch or BNC Switch
    def sendCommand(self, command):
        self.tn.write(b''+str(command).encode()+'\n'.encode())
        time.sleep(.1)
        while 1:
            data = self.tn.read_very_eager()
            if data:
                print(data.decode())
            else:
                break
 
    # close telnet connection
    def close(self):
        self.run=0
        self.tn.close()