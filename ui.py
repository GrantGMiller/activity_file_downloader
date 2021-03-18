import threading
import tkinter
from tkinter import filedialog
from persistent_variables import PersistentVariables as PV
import helpers
from tk_tools import ListboxWithScrollbar, TextWithScrollbar


root = tkinter.Tk()
root.title('Activity File Downloader')
#####################################################
frameDirectory = tkinter.Frame(root)

lblSaveToDir = tkinter.Label(frameDirectory, text='Save Activity Files To:')
lblSaveToDir.grid(row=0, column=0)

strVarSaveToDir = tkinter.StringVar()
entrySaveToDir = tkinter.Entry(frameDirectory, width=50, textvariable=strVarSaveToDir)
entrySaveToDir.grid(row=0, column=1)

btnBrowse = tkinter.Button(frameDirectory, text='Browse', command=helpers.GetFolder)
btnBrowse.grid(row=0, column=2)

frameDirectory.grid(row=0, column=0)

#######################################
frameControls = tkinter.Frame(root)

lblDelay = tkinter.Label(frameControls, text='Delay (seconds):')
entryDelay = tkinter.Entry(frameControls)

lblDelay.grid(row=0, column=0)
entryDelay.grid(row=0, column=1)

btnGoStop = tkinter.Button(frameControls, text='Go', command=helpers.ToggleGoStop)
btnGoStop.grid(row=1, column=1)

frameControls.grid(row=1, column=0)

######################################

frameIPs = tkinter.Frame(root)

btnAdd = tkinter.Button(frameIPs, text='Add TLS', command=helpers.AddTLS)
btnAdd.grid(row=0, column=1)

btnDelete = tkinter.Button(frameIPs, text='Delete TLS', command=helpers.DeleteTLS)
btnDelete.grid(row=0, column=0)

listboxIPs = ListboxWithScrollbar(frameIPs)
listboxIPs.grid(row=1, column=0, columnspan=2)

frameIPs.grid(row=0, column=1, rowspan=2)

##########################################

frameLog = tkinter.Frame(root)

textLog = TextWithScrollbar(frameLog)
textLog.pack()

frameLog.grid(row=2, column=0, columnspan=2)


def mainloop():
    global pv
    pvDir = filedialog.askdirectory()

    strVarSaveToDir.set(pvDir)
    pv = PV('{}/activity_file_ips.json'.format(pvDir))
    pv.Set('save_to_directory', pvDir)

    for ip in pv.Get('ips', []):
        listboxIPs.insert(tkinter.END, ip)

    if pv.Get('delay', None):
        entryDelay.insert(0, pv.Get('delay'))
    else:
        pv.Set('delay', 60)
        entryDelay.insert(0, 60)

    if pv.Get('go', False):
        btnGoStop.config(text='Stop')
        threading.Timer(1, helpers.StartThread).start()
    else:
        btnGoStop.config(text='Go')

    root.mainloop()
