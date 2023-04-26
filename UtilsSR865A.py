# Basic utilities for using the SR865A Lock-in Amplifier
import pyvisa
import time
import numpy as np

sensitivity = {1:0, 0.1:3, 0.01:6, 0.001:9, 0.5:1, 0.00005:13,
               0.0001:12, 0.00001:15, 0.000001:18, 0.0002:11, 0.05:4, 0.00002:14}
               
class Lockin:
    def __init__(self, GPIBnum=10):
        rm = pyvisa.ResourceManager()
        self.lock_in = rm.open_resource('GPIB0::{}::INSTR'.format(GPIBnum))

    def changeHarmonic(self, harm=1, sens=1):
        self.lock_in.write("HARM {}".format(harm))
        self.lock_in.write("SCAL {}".format(sensitivity[sens]))
        print('set harmonic to {} with sensitivity {}\n'.format(harm,sensitivity[sens]))

    def readLockin(self):
        x = float(self.lock_in.query("OUTP? 0").strip())
        y = float(self.lock_in.query("OUTP? 1").strip())
        r = float(self.lock_in.query("OUTP? 2").strip())
        theta = float(self.lock_in.query("OUTP? 3").strip())
        return x, y, r, theta

    def measureLockin(self, count=10, time_step=0.1,
                        wait_before_measure=10,
                        harm=1, sens=0.00001):
        self.changeHarmonic(harm, sens)
        time.sleep(wait_before_measure)
        xs, ys, rs, thetas = [], [], [], []
        for i in range(count):
            x, y, r, theta = self.readLockin()
            xs += [x]
            ys += [y]
            rs += [r]
            thetas += [theta]
            time.sleep(time_step)
        x_mean, x_std = np.mean(xs), np.std(xs)
        y_mean, y_std = np.mean(ys), np.std(ys)
        r_mean, r_std = np.mean(rs), np.std(rs)
        theta_mean, theta_std = np.mean(thetas), np.std(thetas)

        return x_mean, y_mean, r_mean, theta_mean, \
               x_std, y_std,r_std, theta_std


"""Example Commands"""

"""
#Open pyvisa rescource manager to check which devices are connected
rm = pyvisa.ResourceManager()
rm.list_resources()
#connect to and read lock-in
lock=Lockin(GPIBnum=10)
lock.readLockin()
"""