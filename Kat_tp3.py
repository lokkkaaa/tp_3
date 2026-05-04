import csv
import PySimpleGUI as sg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

# ------------------------------------------------------------
# Загрузка данных из CSV
# ------------------------------------------------------------
def load_data(filename='running_data.csv'):
    data = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                row['day'] = int(row['day'])
                row['duration_min'] = int(row['duration_min'])
                row['distance_km'] = float(row['distance_km'])
                row['max_speed'] = float(row['max_speed'])
                row['min_speed'] = float(row['min_speed'])
                row['avg_speed'] = float(row['avg_speed'])
                row['avg_heartrate'] = int(row['avg_heartrate'])
                row['weekend'] = int(row['weekend'])
                data.append(row)
        return data
    except Exception as e:
        sg.popup_error(f'Ошибка загрузки {filename}:\n{e}')
        return None

# ------------------------------------------------------------
# Таблица
# ------------------------------------------------------------
def show_table(data):
    if not data:
        sg.popup('Нет данных')
        return
    headers = list(data[0].keys())
    rows = [[row[h] for h in headers] for row in data]
    layout = [
        [sg.Table(values=rows, headings=headers, auto_size_columns=True,
                  justification='center', num_rows=min(20, len(rows)))],
        [sg.Button('Закрыть')]
    ]
    win = sg.Window('Таблица пробежек', layout, finalize=True, size=(1000, 600))
    while True:
        event, _ = win.read()
        if event in (sg.WIN_CLOSED, 'Закрыть'):
            break
    win.close()

# ------------------------------------------------------------
# Графики (интерактивные)
# ------------------------------------------------------------
def show_plots(data):
    params = ['distance_km', 'duration_min', 'max_speed', 'min_speed', 'avg_speed', 'avg_heartrate']
    param_names = ['Дистанция (км)', 'Длительность (мин)', 'Макс. скорость', 'Мин. скорость', 'Ср. скорость', 'Ср. пульс']

    layout = [
        [sg.Text('Параметр Y1:'), sg.Combo(param_names, key='-Y1-', default_value=param_names[0])],
        [sg.Text('Параметр Y2:'), sg.Combo(param_names, key='-Y2-', default_value=param_names[3])],
        [sg.Text('Период:'), sg.Combo(['Все дни', 'Последние 7 дней', 'Последние 14 дней'], key='-PERIOD-', default_value='Все дни')],
        [sg.Button('Построить'), sg.Button('Сохранить'), sg.Button('Закрыть')],
        [sg.Canvas(key='-CANVAS-', size=(800, 500))]
    ]
    win = sg.Window('Графики', layout, finalize=True, size=(900, 700))
    fig = None
    canvas = None
    toolbar = None

    def draw(y1_key, y2_key, period):
        nonlocal fig, canvas, toolbar
        days = [row['day'] for row in data]
        y1 = [row[y1_key] for row in data]
        y2 = [row[y2_key] for row in data]
        if period == 'Последние 7 дней' and len(days) >= 7:
            days = days[-7:]; y1 = y1[-7:]; y2 = y2[-7:]
        elif period == 'Последние 14 дней' and len(days) >= 14:
            days = days[-14:]; y1 = y1[-14:]; y2 = y2[-14:]
        if fig:
            plt.close(fig)
        fig, ax = plt.subplots(figsize=(8,5))
        ax.plot(days, y1, marker='o', label=param_names[params.index(y1_key)])
        ax.plot(days, y2, marker='s', label=param_names[params.index(y2_key)])
        ax.set_xlabel('День'); ax.set_ylabel('Значение'); ax.set_title('Зависимость от дня')
        ax.legend(); ax.grid(True)
        if canvas:
            canvas.get_tk_widget().destroy()
        if toolbar:
            toolbar.destroy()
        canvas = FigureCanvasTkAgg(fig, win['-CANVAS-'].TKCanvas)
        canvas.draw()
        toolbar = NavigationToolbar2Tk(canvas, win['-CANVAS-'].TKCanvas)
        toolbar.update()
        canvas.get_tk_widget().pack(side='top', fill='both', expand=1)

    while True:
        event, values = win.read()
        if event in (sg.WIN_CLOSED, 'Закрыть'):
            break
        if event == 'Построить':
            y1_key = params[param_names.index(values['-Y1-'])]
            y2_key = params[param_names.index(values['-Y2-'])]
            draw(y1_key, y2_key, values['-PERIOD-'])
        if event == 'Сохранить' and fig:
            fig.savefig('plots.png', dpi=150)
            sg.popup('Сохранено как plots.png')
    win.close()

# ------------------------------------------------------------
# Сумма км за выходные
# ------------------------------------------------------------
def weekend_km(data):
    total = sum(row['distance_km'] for row in data if row['weekend'] == 1)
    sg.popup(f'Всего за выходные: {total:.2f} км', title='Пробежные км')

# ------------------------------------------------------------
# Прогноз скользящей средней
# ------------------------------------------------------------
def forecast_window(data):
    distances = [row['distance_km'] for row in data]
    layout = [
        [sg.Text('Период N:'), sg.InputText('5', key='-N-', size=(10,1))],
        [sg.Text('Дней прогноза K:'), sg.InputText('7', key='-K-', size=(10,1))],
        [sg.Button('Построить'), sg.Button('Сохранить'), sg.Button('Закрыть')],
        [sg.Canvas(key='-CANVAS-', size=(800, 500))]
    ]
    win = sg.Window('Прогноз', layout, finalize=True, size=(900, 700))
    fig = None
    canvas = None
    toolbar = None

    def draw_forecast(n, k):
        nonlocal fig, canvas, toolbar
        y = distances[:]
        forecast = []
        cur = y[:]
        for _ in range(k):
            if len(cur) < n:
                break
            ma = sum(cur[-n:]) / n
            forecast.append(ma)
            cur.append(ma)
        hist_days = list(range(1, len(y)+1))
        pred_days = list(range(len(y)+1, len(y)+k+1))
        if fig:
            plt.close(fig)
        fig, ax = plt.subplots(figsize=(8,5))
        ax.plot(hist_days, y, marker='o', label='История', color='blue')
        ax.plot(pred_days, forecast, marker='x', linestyle='--', label='Прогноз', color='red')
        ax.set_xlabel('День'); ax.set_ylabel('Дистанция (км)')
        ax.set_title(f'Прогноз на {k} дней, N={n}')
        ax.legend(); ax.grid(True)
        if canvas:
            canvas.get_tk_widget().destroy()
        if toolbar:
            toolbar.destroy()
        canvas = FigureCanvasTkAgg(fig, win['-CANVAS-'].TKCanvas)
        canvas.draw()
        toolbar = NavigationToolbar2Tk(canvas, win['-CANVAS-'].TKCanvas)
        toolbar.update()
        canvas.get_tk_widget().pack(side='top', fill='both', expand=1)

    while True:
        event, values = win.read()
        if event in (sg.WIN_CLOSED, 'Закрыть'):
            break
        if event == 'Построить':
            try:
                n = int(values['-N-']); k = int(values['-K-'])
                if n>0 and k>0:
                    draw_forecast(n, k)
                else:
                    sg.popup('N и K > 0')
            except ValueError:
                sg.popup('Введите числа')
        if event == 'Сохранить' and fig:
            fig.savefig('forecast.png', dpi=150)
            sg.popup('Сохранено как forecast.png')
    win.close()

# ------------------------------------------------------------
# Главная функция, вызываемая из main.py
# ------------------------------------------------------------
def run():
    data = load_data('running_data.csv')
    if data is None:
        return
    layout = [
        [sg.Text('Информация о пробежках', font='Helvetica 20', justification='center', expand_x=True)],
        [sg.Button('Открыть таблицу', key='-OPEN_TABLE-', font='Helvetica 16', size=(25, 1))],
        [sg.Button('Показать графики', key='-SHOW_PLOTS-', font='Helvetica 16', size=(25, 1))],
        [sg.Button('Пробежные км', key='-TOTAL_KM-', font='Helvetica 16', size=(25, 1))],
        [sg.Button('Прогноз на следующее N дней', key='-FORECAST-', font='Helvetica 16', size=(25, 1))],
        [sg.Button('◀ Назад', key='-BACK-', font='Helvetica 14', size=(25, 1))]
    ]
    window = sg.Window('Меню: пробежки', layout, size=(500, 400), finalize=True)
    while True:
        event, _ = window.read()
        if event in (sg.WIN_CLOSED, '-BACK-'):
            break
        if event == '-OPEN_TABLE-':
            show_table(data)
        elif event == '-SHOW_PLOTS-':
            show_plots(data)
        elif event == '-TOTAL_KM-':
            weekend_km(data)
        elif event == '-FORECAST-':
            forecast_window(data)
    window.close()

# ------------------------------------------------------------
# Если запускают этот файл напрямую
# ------------------------------------------------------------
if __name__ == '__main__':
    run()
