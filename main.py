import PySimpleGUI as sg
from vika import vika_module
from polya import run_polya
import Kat_tp3
layout = [
    [sg.Button('Данные о пробежках', key='-KAT-', font='Helvetica 16', size=(60, 2))],
    [sg.Button('Данные о численности населения', key='-POLYA-', font='Helvetica 16', size=(60, 2))],
    [sg.Button('Данные о заболеваниях', key='-VIKA-', font='Helvetica 16',size=(60, 2))]
]
window = sg.Window('Главное меню', layout, size=(500,300))
while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, 'Exit'):
        break
    if event == '-VIKA-':
        vika_module()
    if event == "-POLYA":
        run_polya()
    if event == '-KAT-':
        window.hide()
        Kat_tp3.run()
        window.un_hide()
window.close()