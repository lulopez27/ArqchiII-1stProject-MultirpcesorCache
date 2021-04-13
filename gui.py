import PySimpleGUI as sg


layout = [[sg.Text('Caches:', size=(30,1),pad=(500,0))],

          [sg.Text('Cache1', size=(30,1),pad=(60,0)),
          sg.Text('Cache2', size=(30,1),pad=(10,0)),
          sg.Text('Cache3', size=(30,1),pad=(10,0)),
          sg.Text('Cache4', size=(30,1),pad=(10,0))],
          [sg.Text('[0, I, 0, 0]', size=(30,1),pad=(50,0),key='C1V0'),
          sg.Text('[0, I, 0, 0]', size=(30,1),pad=(6,0),key='C2V0'),
          sg.Text('[0, I, 0, 0]', size=(30,1),pad=(5,0),key='C3V0'),
          sg.Text('[0, I, 0, 0]', size=(30,1),pad=(7,0),key='C4V0')],
          [sg.Text('[1, I, 0, 0]', size=(30,1),pad=(70,0),key='C1V1'),
          sg.Text('[1, I, 0, 0]', size=(30,1),pad=(6,0),key='C2V1'),
          sg.Text('[1, I, 0, 0]', size=(30,1),pad=(5,0),key='C3V1'),
          sg.Text('[1, I, 0, 0]', size=(30,1),pad=(7,0),key='C4V1')],

          [[sg.Text('L2 Cache:', size=(30,1),pad=(500,0))]],
          [sg.Text('[0, I, 0, 0]', size=(30,1),pad=(515,0),key='L2V0')],
          [sg.Text('[1, I, 0, 0]', size=(30,1),pad=(515,0),key='L2V1')],
          [sg.Text('[2, I, 0, 0]', size=(30,1),pad=(515,0),key='L2V2')],
          [sg.Text('[3, I, 0, 0]', size=(30,1),pad=(515,0),key='L2V3')],

          [[sg.Text('MainMem:', size=(30,1),pad=(500,0))]],
          [sg.Text('0 - 0', size=(30,1),pad=(515,0),key='MV0')],
          [sg.Text('1 - 0', size=(30,1),pad=(515,0),key='MV1')],
          [sg.Text('2 - 0', size=(30,1),pad=(515,0),key='MV2')],
          [sg.Text('3 - 0', size=(30,1),pad=(515,0),key='MV3')],
          [sg.Text('4 - 0', size=(30,1),pad=(515,0),key='MV4')],
          [sg.Text('5 - 0', size=(30,1),pad=(515,0),key='MV5')],
          [sg.Text('6 - 0', size=(30,1),pad=(515,0),key='MV6')],
          [sg.Text('7 - 0', size=(30,1),pad=(515,0),key='MV7')],
          [sg.Button('OK'), sg.Button('Exit')]]

window = sg.Window('Title', layout)


def run():
    while True:
        event, values = window.read()

        if event == 'Exit' or event == sg.WIN_CLOSED:
            break
        
    window.close()

run()

def updateWindow(val,key):
    window[key].update(val)