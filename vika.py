import PySimpleGUI as sg
import pandas as pd
import matplotlib.pyplot as plt
def load_data():
    return pd.read_excel("infections.xlsx")
def vika_module():
    try:
        df = load_data()
    except Exception as e:
        sg.popup(f"Ошибка загрузки файла: {e}")
        return

    layout = [
        [sg.Button("Показать таблицу")],
        [sg.Button("Графики")],
        [sg.Button("Анализ")],
        [sg.Button("Прогноз")],
        [sg.Button("Назад")]
    ]

    window = sg.Window("Модуль Вики", layout)

    while True:
        event, _ = window.read()

        if event in (sg.WIN_CLOSED, "Назад"):
            break
        elif event == "Показать таблицу":
            show_table(df)
        elif event == "Графики":
            plot_graphs(df)
        elif event == "Анализ":
            analyze(df)
        elif event == "Прогноз":
            forecast(df)
    window.close()
#ТАБЛИЦЫ
def show_table(df):
    layout = [
        [sg.Table(
            values=df.values.tolist(),
            headings=list(df.columns),
            auto_size_columns=True,
            justification='center',
            num_rows=10
        )],
        [sg.Button("Закрыть")]
    ]

    window = sg.Window("Таблица заболеваний", layout)

    while True:
        event, _ = window.read()
        if event in (sg.WIN_CLOSED, "Закрыть"):
            break

    window.close()
# ГРАФИКИ
def plot_graphs(df):
    years = df['Год']

    for col in df.columns[1:]:
        plt.plot(years, df[col], label=col)

    plt.legend()
    plt.title("Заболеваемость по годам")
    plt.xlabel("Год")
    plt.ylabel("Количество")
    plt.grid()
    plt.show()
    # ===== Анализ =====


def analyze(df):
    changes = {}

    for col in df.columns[1:]:
        start = df[col].iloc[0]
        end = df[col].iloc[-1]
        changes[col] = start - end

    max_disease = max(changes, key=changes.get)
    min_disease = min(changes, key=changes.get)

    sg.popup(f"Больше всего снизилось: {max_disease}\n"
             f"Меньше всего снизилось: {min_disease}")
# ===== Скользящая средняя =====
def moving_average(series, window=3):
    return series.rolling(window=window).mean()


# ===== Прогноз =====
def forecast(df, n_years=5):
    last_year = df['Год'].iloc[-1]
    future_years = [last_year + i for i in range(1, n_years + 1)]

    plt.figure()

    for col in df.columns[1:]:
        ma = moving_average(df[col])
        last_value = ma.iloc[-1]

        forecast_values = [last_value] * n_years

        plt.plot(df['Год'], df[col], label=f"{col} (факт)")
        plt.plot(future_years, forecast_values, '--', label=f"{col} (прогноз)")

    plt.legend()
    plt.title("Прогноз (скользящая средняя)")
    plt.grid()
    plt.show()
