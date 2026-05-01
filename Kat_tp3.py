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
