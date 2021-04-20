import PySimpleGUI as sg
from threading import Lock


step_wait = True
step = True
step_mutex = Lock()
single_thread = True
start = True
dead = False
inst =[]
layout = [[sg.Text('Caches:', size=(30,1),pad=(550,0))],

          [sg.Text('Core:1', size=(30,1),pad=(60,0),key='C1I'),
          sg.Text('Core:2', size=(30,1),pad=(10,0), key='C2I'),
          sg.Text('Core:3', size=(30,1),pad=(10,0), key='C3I'),
          sg.Text('Core:4', size=(30,1),pad=(10,0), key='C4I')],
          [sg.Text('0)   Addr: Val:', size=(30,1),pad=(55,0),key='C1V0'),
          sg.Text( '0)   Addr: Val:', size=(30,1),pad=(14,0),key='C2V0'),
          sg.Text( '0)   Addr: Val:', size=(30,1),pad=(7,0),key= 'C3V0'),
          sg.Text( '0)   Addr: Val:', size=(30,1),pad=(10,0),key='C4V0')],
          [sg.Text('1)   Addr: Val:', size=(30,1),pad=(55,0),key='C1V1'),
          sg.Text( '1)   Addr: Val:', size=(30,1),pad=(14,0),key='C2V1'),
          sg.Text( '1)   Addr: Val:', size=(30,1),pad=(7,0),key='C3V1'),
          sg.Text( '1)   Addr: Val:', size=(30,1),pad=(10,0),key='C4V1')],

          [[sg.Text('L2 Cache:', size=(30,1),pad=(500,0))]],
          [sg.Text('0) DM O: Shar:  Addr: Val:', size=(60,1),pad=(500,0),key='L2V0')],
          [sg.Text('1) DM O: Shar:  Addr: Val:', size=(60,1),pad=(500,0),key='L2V1')],
          [sg.Text('2) DM O: Shar:  Addr: Val:', size=(60,1),pad=(500,0),key='L2V2')],
          [sg.Text('3) DM O: Shar:  Addr: Val:', size=(60,1),pad=(500,0),key='L2V3')],

          [[sg.Text('MainMem:', size=(30,1),pad=(500,0))]],
          [sg.Text('0 - 0', size=(30,1),pad=(515,0),key='MV0')],
          [sg.Text('1 - 0', size=(30,1),pad=(515,0),key='MV1')],
          [sg.Text('10 - 0', size=(30,1),pad=(515,0),key='MV2')],
          [sg.Text('11 - 0', size=(30,1),pad=(515,0),key='MV3')],
          [sg.Text('100 - 0', size=(30,1),pad=(515,0),key='MV4')],
          [sg.Text('101 - 0', size=(30,1),pad=(515,0),key='MV5')],
          [sg.Text('110 - 0', size=(30,1),pad=(515,0),key='MV6')],
          [sg.Text('111 - 0', size=(30,1),pad=(515,0),key='MV7')],
          [sg.Listbox(values=('One-by-one', 'Continous step', 'Continous non-stop'),default_values='One-by-one', size=(30, 3),key ='runmode')
          ,sg.Button('Change')],
          [sg.Radio('C1', 'num', default=True),sg.Radio('C2', 'num'),sg.Radio('C3', 'num'),sg.Radio('C4', 'num'),
          sg.Combo([0,1,2,3,4,5,6,7],default_value='0',tooltip='Select Address',key='block_addr',size=(5, 1)),
          sg.Input(default_text='Val',key='write_val',size=(10,1)),
          sg.Button('Read'),sg.Button('Write')],
          [sg.Button('Next'),sg.Button('Exit'),sg.Text('',size=(2,1),key='running')]]

window = sg.Window('Title', layout)


def runGUI():
    global step_mutex
    global dead
    global step
    global single_thread
    global inst
    while True:
        event, values = window.read()
        if event == 'Exit' or event == sg.WIN_CLOSED:
            step_mutex.acquire()
            dead = True
            step_mutex.release()
            break
        elif event == 'Next':
            next_step()
        elif event == 'Change':
            if(values['runmode'][0] == 'One-by-one'):
                step_mutex.acquire()
                step = True
                single_thread = True
                step_mutex.release()
            elif(values['runmode'][0] == 'Continous step'):
                step_mutex.acquire()
                step = True
                single_thread = False
                step_mutex.release()
            elif(values['runmode'][0] == 'Continous non-stop'):
                step_mutex.acquire()
                step = False
                single_thread = False
                step_mutex.release()
        elif(event == 'Read'):
            step_mutex.acquire()
            inst = [getcache(values),True,values['block_addr']]
            step_mutex.release()
        elif(event == 'Write'):
            step_mutex.acquire()
            inst = [getcache(values),False,values['block_addr'],int(values['write_val'])]
            step_mutex.release()
    window.close()

def updateWindow(val,key):
    window[key].update(val)

def getcache(values):
    for i in range(3):
        if(values[i]):
            return i
    return 0

def next_step():
    print("Next step")
    step_mutex.acquire()
    global step_wait
    step_wait = False
    step_mutex.release()