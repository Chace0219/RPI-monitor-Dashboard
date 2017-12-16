import os, sys
import threading
import time

'''
# pacakges - install of paramiko on raspbian
    sudo apt-get install libffi-dev
    sudo pip install paramiko

'''
import paramiko

import RPi.GPIO as GPIO
RELAYON = GPIO.LOW
RELAYOFF = GPIO.HIGH

### utility functions definition
millis = lambda: int(round(time.time() * 1000))
seconds = lambda: int(round(time.time()))

# status definition
CHECK = 0
POWEROFF = 1
OFFDELAY = 2
POWERON = 3
BOOTING = 4

# timing settings for status transition
CHECKTIME = 60 # if for specified time, ssh connection error status is kept, it will force power on or power off and on
POWEROFFTIME = 10 # when power off, relay action time
OFFDELAYTIME = 30 # after power off, delay time
POWERONTIME = 2 # when power on, relay action time
BOOTINGTIME = 150 # after power on, botting time, when booting, we don't have to check status

### miner monitoring class
class ManagerMiner(threading.Thread):
    ### logging callback functions
    info = None
    warning = None
    error = None

    def logginginfo(self, msg):
        if(ManagerMiner.info != None):
            ManagerMiner.info(self, msg)

    def loggingwarning(self, msg):
        if(ManagerMiner.warning != None):
            ManagerMiner.warning(self, msg)

    def loggingerror(self, msg):
        if(ManagerMiner.error != None):
            ManagerMiner.error(self, msg)

    def __init__(self, uniqueid, gpio, ipaddr, uid='', pwd='', cycle=30, description='', auto=False):
        threading.Thread.__init__(self)
        # event instance
        self.event = threading.Event()
        # init setting values
        self.uniqueid = uniqueid
        self.cycle = cycle
        self.gpio = gpio
        self.ipaddr = ipaddr
        self.description = description
        self.uid = uid
        self.pwd = pwd
        self.auto = auto

        self.logginginfo(self.getinfo() + ', thread started')
        self.status = CHECK
        self.lastResult = False
        self.lastchecktime = seconds()
        self.enterChecking()

        ### GPIO init
        GPIO.setmode(GPIO.BCM)  # Broadcom pin-numbering scheme
        GPIO.setwarnings(False)
        GPIO.setup(self.gpio, GPIO.OUT)
        GPIO.output(self.gpio, RELAYOFF)

        ### thread start
        self.start()

    def setGPIO(self, gpio):
        if(gpio >= 2 and gpio <= 26):
            self.gpio = gpio
            GPIO.setwarnings(False)
            GPIO.setup(self.gpio, GPIO.OUT)
            GPIO.output(self.gpio, RELAYOFF)
            print('gpio testing')

    # enter routine for check status
    def enterChecking(self):
        self.status = CHECK
        self.transitTime = seconds()
        self.lastchecktime = seconds()
        self.logginginfo(self.getinfo() + ', entered into chcking status')


    # enter routine for power off status
    def enterPowerOff(self):
        self.status = POWEROFF
        self.transitTime = seconds()
        self.logginginfo(self.getinfo() + ', entered into power off status')

    # enter routine for off delay status
    def enterOffDelay(self):
        self.status = OFFDELAY
        self.transitTime = seconds()
        self.logginginfo(self.getinfo() + ', after power off delay status')

    # enter routine for power on status
    def enterPowerOn(self):
        self.status = POWERON
        self.transitTime = seconds()
        self.logginginfo(self.getinfo() + ', power on status')

    # enter routine for booting status
    def enterBooting(self):
        self.status = BOOTING
        self.transitTime = seconds()
        self.logginginfo(self.getinfo() + ', booting status')

    # check ssh for specified ip
    def checkSSH(self):
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(self.ipaddr, username=self.uid, password=self.pwd)
            client.close()
        except paramiko.AuthenticationException:
            self.loggingwarning(self.getinfo() + ', ssh connect password error')
        except:
            self.loggingerror(self.getinfo() + ', ssh connect error')
            return False
        return True

    # check ping for specified ip, if ip is checked, return false, else return true
    def pingToServer(self):
        try:
            hostname = self.ipaddr
            response = os.system("ping -c 1 " + hostname)
            return response
        except:
            return False

    # get information of monitor class
    def getinfo(self):
        return ('monitor id:' + str(self.uniqueid) + ', serverip:' + self.ipaddr + ', gpio:' + str(self.gpio))

    # thread proc
    def run(self):
        while not self.event.is_set():
            # status management
            if(self.status == CHECK):
                ### relay action
                GPIO.output(self.gpio, RELAYOFF)

                ### every checking cycle, it will check ssh connection
                if(seconds() >= self.lastchecktime + self.cycle):
                    if(self.checkSSH()):
                        self.transitTime = seconds() # if success in checking ssh, reset status time
                        self.lastResult = True
                    else:
                        self.lastResult = False


                    # reset checking time
                    self.lastchecktime = seconds()
                ### check status time
                if(self.auto):
                    if((seconds() - self.transitTime) >= CHECKTIME):
                        if(not self.pingToServer()):
                            # if miner powered on, we have to power off and on again
                            self.enterPowerOff() ### enter into power off
                        else:
                            # if miner powered off, we have to only power on
                            self.enterPowerOn() ### enter into power on

            elif(self.status == POWEROFF):
                ### relay action
                GPIO.output(self.gpio, RELAYON)
                ### check status time
                if((seconds() - self.transitTime) >= POWEROFFTIME):
                    GPIO.output(self.gpio, RELAYOFF)
                    self.enterOffDelay() ### enter into offdelay
            elif(self.status == OFFDELAY):
                ### relay action
                GPIO.output(self.gpio, RELAYOFF)
                ### check status time
                if((seconds() - self.transitTime) >= OFFDELAYTIME):
                    self.enterPowerOn() ### enter into power on
            elif(self.status == POWERON):
                ### relay action
                GPIO.output(self.gpio, RELAYON)
                ### check status time
                if((seconds() - self.transitTime) >= POWERONTIME):
                    GPIO.output(self.gpio, RELAYOFF)
                    self.enterBooting() ### enter into booting
            elif(self.status == BOOTING):
                ### relay action
                GPIO.output(self.gpio, RELAYOFF)
                ### check status time
                if((seconds() - self.transitTime) >= BOOTINGTIME):
                    self.enterChecking() ### enter into checking
            time.sleep(0.5)

        # when thread stop is forced
        GPIO.output(self.gpio, RELAYOFF)
        self.logginginfo(self.getinfo() + ', thread proc completed')