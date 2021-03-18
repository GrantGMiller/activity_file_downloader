import datetime
import threading
import time
import tkinter
from tkinter import filedialog, simpledialog
from sftpclient import SFTPClient
import ui
from tk_tools import askHostUserPass


def AddToLog(*args):
    text = str(datetime.datetime.now()) + ' ' + ' '.join([str(a) for a in args])
    if not text.endswith('\n'):
        text += '\n'
    ui.textLog.insert(tkinter.END, text)


def SaveIPs():
    ui.pv.Set('ips', ui.listboxIPs.get(0, tkinter.END))
    AddToLog('SaveIPs')


def GetFolder(initDir=None):
    global saveToDir
    directory = filedialog.askdirectory()
    print('GetFolder return', directory)
    ui.strVarSaveToDir.set(directory)
    ui.pv.Set('save_to_directory', directory)
    AddToLog('save_to_directory', directory)
    saveToDir = directory
    SaveIPs()
    return directory


def SaveCreds(host, pw):
    ui.pv.SetItem('credentials', host, pw)


def AddTLS():
    tup = askHostUserPass(ui.root, 'Add TLS', 'Enter the Host/IP and admin password')
    if tup:
        host, pw = tup
        ui.listboxIPs.insert(tkinter.END, host)
        SaveIPs()
        SaveCreds(host, pw)
        AddToLog('Add TLS', host)


def DeleteTLS():
    res = ui.listboxIPs.curselection()
    print('res=', res)
    ui.listboxIPs.delete(
        res
    )
    SaveIPs()
    AddToLog('Deleted', res)


def SaveDelay(*a, **k):
    print('SaveDelay(', a, k)
    v = ui.entryDelay.get()
    print('v=', v)
    val = int(v)
    ui.pv.Set('delay', val)
    AddToLog('delay', val)


def ToggleGoStop():
    go = bool(ui.pv.Get('go', False))
    go = not go
    ui.pv.Set('go', go)
    ui.btnGoStop.config(text='Go' if not go else 'Stop')
    AddToLog('Go' if go else 'Stop')
    if go:
        StartThread()


def GetActivityFiles():
    while ui.pv.Get('go', False) is True:
        print('while True')

        SaveDelay()
        for ip in ui.pv.Get('ips', []):
            try:
                AddToLog(ip, 'Connecting')
                client = SFTPClient(
                    host=ip,
                    port=22022,
                    username='admin',
                    password=ui.pv.GetItem('credentials', ip),
                    use_known_hosts=False,
                )
                AddToLog(ip, 'Downloading Activity File')
                file = client.download('/Activity.csv', text=True)

                with open('{}/Activity_{}.csv'.format(ui.pv.Get('save_to_directory'), ip), mode='wt') as activityFile:
                    activityFile.write(file.read())

                AddToLog(ip, 'Complete')

            except Exception as e:
                AddToLog(ip, 'Error:', e)

        delay = ui.pv.Get('delay', 60)
        if not delay:
            delay = 60
        AddToLog('Delaying for', int(delay), 'seconds')
        startTime = time.time()
        while ui.pv.Get('go', False) is True and time.time() - startTime < delay:
            time.sleep(0.1)

    SaveDelay()
    AddToLog('Stopping thread')


def StartThread():
    t = threading.Timer(0, GetActivityFiles)
    t.start()
    AddToLog('Starting thread', t)
