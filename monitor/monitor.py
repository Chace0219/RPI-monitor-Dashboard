from flask import Flask, render_template, request, jsonify, url_for, json
import os, sys
import threading
import time
import logging
import socketio

# miner monitor class package import
from rebootcontroller import *

### logging file name definition - 2017-11-21.txt
import datetime as dt
sitepath = os.path.realpath(os.path.dirname(__file__))
loggingdir = os.path.join(sitepath, 'static/logging/')
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s ', datefmt='%Y-%m-%d %H:%M:%S')
logfilename = loggingdir + dt.datetime.now().strftime('%Y-%m-%d') + '.txt'
rootlogger = logging.getLogger()
#handler = logging.FileHandler(logfilename)
#handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
#rootlogger.addHandler(handler)

NAMESPACE = '/status'

def checkLogFileName():
    ### build log file name with current date
    sitepath = os.path.realpath(os.path.dirname(__file__))
    loggingdir = os.path.join(sitepath, 'static/logging/')
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s ',
                        datefmt='%Y-%m-%d %H:%M:%S')
    newLogFileName = loggingdir + dt.datetime.now().strftime('%Y-%m-%d') + '.txt'
    ### check datetime and change logging file name

    '''
    if(logfilename != newLogFileName):
        # close current file and open new file
        global handler
        handler.close()
        global rootlogger
        rootlogger.removeHandler(handler)
        handler = logging.FileHandler(newLogFileName)
        handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
        rootlogger.addHandler(handler)
    '''

### logging callback function defitions
def callbacklogginginfo(monitor, msg):
    checkLogFileName()
    logging.info(msg)
    triggerScoketEmit()

def callbackloggingerror(monitor, msg):
    checkLogFileName()
    logging.error(msg)
    triggerScoketEmit()

def callbackloggingwarning(monitor, msg):
    checkLogFileName()
    logging.warning(msg)
    triggerScoketEmit()

### manager thread testing example
managers = [] # list of monitor threads
def loadmonitors():

    # if you need to use logging function,
    ManagerMiner.info = callbacklogginginfo
    ManagerMiner.error = callbackloggingerror
    ManagerMiner.warning = callbackloggingwarning

    # get setting json path
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, 'static/data', 'setting.json')

    ### load settings from json
    settingarray = json.load(open(json_url))
    for item in settingarray:
        # init miner monitor thread instance
        newManager = ManagerMiner(uniqueid=item['uniqueid'], gpio=item['gpio'], ipaddr=item['ipaddr'], uid=item['uid'], pwd=item['pwd'], description=item['description'], cycle=item['cycle'],
                                  auto=item['auto'])
        # append thread into list
        managers.append(newManager)

def savesettings():
    global managers
    try:
        settings = []
        for monitor in managers:
            item = dict()
            item['uniqueid'] = monitor.uniqueid
            item['ipaddr'] = monitor.ipaddr
            item['gpio'] = monitor.gpio
            item['description'] = monitor.description
            item['cycle'] = monitor.cycle
            item['uid'] = monitor.uid
            item['pwd'] = monitor.pwd
            item['auto'] = monitor.auto
            settings.append(item)

        # get setting json path
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, 'static/data', 'setting.json')
        with open(json_url, 'w') as outfile:
            json.dump(settings, outfile, sort_keys=True, indent=4)
    except:
        logging.error('it happens error in saving json')

def getinfo():
    systemInfo = []
    try:
        for manager in managers:
            inforow = dict()
            inforow['uniqueid'] = manager.uniqueid
            inforow['description'] = manager.description
            inforow['cycle'] = manager.cycle
            inforow['gpio'] = manager.gpio
            inforow['ipaddr'] = manager.ipaddr
            inforow['uid'] = manager.uid
            inforow['pwd'] = manager.pwd

            if(manager.status == CHECK):
                inforow['status'] = 'checking action'
            elif(manager.status == POWEROFF):
                inforow['status'] = 'poweroff action'
            elif(manager.status == OFFDELAY):
                inforow['status'] = 'delay after poweroff'
            elif(manager.status == POWERON):
                inforow['status'] = 'poweron action'
            elif(manager.status == BOOTING):
                inforow['status'] = 'booting action'

            if(manager.lastResult):
                inforow['SSHCkecking'] = 'success'
            else:
                inforow['SSHCkecking'] = 'failed'
            systemInfo.append(inforow)
    except:
        print('error in getting system information')
    return systemInfo

# socket io init
sio = socketio.Server(logger=True, async_mode=None)
app = Flask(__name__)
app.wsgi_app = socketio.Middleware(sio, app.wsgi_app)
app.config['SECRET_KEY'] = 'secret!'
thread = None
changedStatus = False

def triggerScoketEmit():
    global changedStatus
    changedStatus = True

def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        sio.sleep(0.25)
        global changedStatus
        if changedStatus:
            changedStatus = False
            sio.emit('status', {'data': json.dumps(getinfo())},
                     namespace=NAMESPACE)

@app.route('/')
def index():
    global thread
    if thread is None:
        thread = sio.start_background_task(background_thread)
    return render_template('index.html')

@sio.on('disconnect request', namespace=NAMESPACE)
def disconnect_request(sid):
    sio.disconnect(sid, namespace=NAMESPACE)

@sio.on('connect', namespace=NAMESPACE)
def test_connect(sid, environ):
    sio.emit('status', {'data': json.dumps(getinfo())}, room=sid,
             namespace=NAMESPACE)

@sio.on('disconnect', namespace=NAMESPACE)
def test_disconnect(sid):
    print('Client disconnected')


@app.route('/update')
def updateMonitor():
    global managers
    try:
        # get id from get request
        uniqueid = request.args.get('uniqueid')
        if (uniqueid != None):
            # find thread in list
            targets = filter(lambda monitor: monitor.uniqueid == int(uniqueid), managers)
            if (len(targets) > 0):
                ipaddr = request.args.get('ipaddr')
                if(ipaddr != None):
                    targets[0].ipaddr = ipaddr
                gpio = request.args.get('gpio')
                if(gpio != None):
                    print('gpio updating')
                    targets[0].setGPIO(int(gpio))
                description = request.args.get('description')
                if(description != None):
                    targets[0].description = description
                cycle = request.args.get('cycle')
                if(cycle != None):
                    targets[0].cycle = int(cycle)
                uid = request.args.get('uid')
                if(uid != None):
                    targets[0].uid = uid
                pwd = request.args.get('pwd')
                if(pwd != None):
                    targets[0].pwd = pwd
                savesettings()
                triggerScoketEmit()
            else:
                return('there is no monitor which you find')
            return 'update action is executed'
        else:
            return 'invalid update request format'
    except:
        return 'it happens error in executing update action'

@app.route('/insert')
def insertMonitor():
    global managers
    try:
        # get last item id number
        uniqueid = managers[len(managers) - 1].uniqueid
        uniqueid = uniqueid + 1
        # init miner monitor thread instance
        newMonitor = ManagerMiner(uniqueid=uniqueid, gpio=25, ipaddr='192.168.1.1', uid='uid', pwd='pwd', description='', cycle=30, auto=False)
        print('normal working')
        managers.append(newMonitor)
        savesettings()
        triggerScoketEmit()
        return 'insert action is executed'
    except:
        return 'it happens error in executing update action'

@app.route('/delete')
def deleteMonitor():
    global managers
    try:
        # get id from get request
        uniqueid = request.args.get('uniqueid')
        if (uniqueid != None):
            # find thread in list
            targets = filter(lambda monitor: monitor.uniqueid == int(uniqueid), managers)
            if (len(targets) > 0):
                targets[0].event.set()
                managers.remove(targets[0])
                savesettings()
                triggerScoketEmit()
            else:
                print('there is no monitor which you find')
            return 'reboot action is executed'
        else:
            return 'invalid reboot request format'
    except:
        return 'it happens error in executing reboot action'

@app.route('/reboot')
def reboot():
    global managers
    try:
        # get id from get request
        uniqueid = request.args.get('uniqueid')
        if (uniqueid != None):
            # find thread in list
            targets = filter(lambda monitor: monitor.uniqueid == int(uniqueid), managers)
            if (len(targets) > 0):
                targets[0].enterPowerOff()
                triggerScoketEmit()
            else:
                print('there is no monitor which you find')
            return 'reboot action is executed'
        else:
            return 'invalid reboot request format'
    except:
        return 'it happens error in executing reboot action'

@app.route('/poweron')
def poweron():
    global managers
    try:
        # get id from get request
        uniqueid = request.args.get('uniqueid')
        if (uniqueid != None):
            # find thread in list
            targets = filter(lambda monitor: monitor.uniqueid == int(uniqueid), managers)
            if (len(targets) > 0):
                targets[0].enterPowerOn()
                triggerScoketEmit()
            else:
                print('there is no monitor which you find')
            return 'power on action is executed'
        else:
            return 'invalid poweron request format'
    except:
        return 'it happens error in executing poweron'

if __name__ == '__main__':
    # deploy with eventlet
    import eventlet
    import eventlet.wsgi
    try:
        loadmonitors()
        eventlet.wsgi.server(eventlet.listen(('', 5002)), app)
    except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
        print('CTRL + C key pressed')
        pass
    finally:
        for manager in managers:
            manager.event.set()
        time.sleep(5)
        logging.info('script is finished')


