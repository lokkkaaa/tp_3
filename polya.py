import PySimpleGUI as sg
import pandas as pd
import matplotlib.pyplot as plt


# ======================
# ЗАГРУЗКА ДАННЫХ

def load_data(path):
    return pd.read_excel(path)


def validate_df(df):
    if df.empty:
        raise ValueError("Файл пустой.")
    if 'Год' not in df.columns or 'Население' not in df.columns:
        raise ValueError("Нужны колонки: 'Год' и 'Население'.")



# ТАБЛИЦА
def show_table(df):
    layout = [
        [sg.Table(
            values=df.values.tolist(),
            headings=list(df.columns),
            auto_size_columns=True,
            justification='center',
            num_rows=min(15, len(df)),
            expand_x=True,
            expand_y=True
        )],
        [sg.Button("Закрыть")]
    ]

    window = sg.Window("Таблица населения", layout, modal=True)

    while True:
        event, _ = window.read()
        if event in (sg.WIN_CLOSED, "Закрыть"):
            break

    window.close()



# ГРАФИК

def plot_graph(df):
    plt.figure()
    plt.plot(df['Год'], df['Население'], marker='o')
    plt.title("Численность населения России")
    plt.xlabel("Год")
    plt.ylabel("Млн человек")
    plt.grid()
    plt.show()



# АНАЛИЗ

def analyze(df):
    pop = df['Население']

    changes = []
    for i in range(1, len(pop)):
        percent = ((pop[i] - pop[i - 1]) / pop[i - 1]) * 100
        changes.append(percent)

    sg.popup(
        f"Максимальный рост: {max(changes):.2f}%\n"
        f"Максимальная убыль: {min(changes):.2f}%",
        title="Анализ"
    )



# ПРОГНОЗ

def extrapolate(series, window, n):
    history = list(series)
    forecast = []

    for _ in range(n):
        next_val = sum(history[-window:]) / window
        forecast.append(next_val)
        history.append(next_val)

    return forecast


def forecast(df, window, years):
    last_year = int(df['Год'].iloc[-1])

    future_years = list(range(last_year + 1, last_year + years + 1))
    population = list(df['Население'])

    forecast_values = extrapolate(population, window, years)

    plt.figure()

    plt.plot(df['Год'], population, marker='o', label="Факт")

    plt.plot(
        [df['Год'].iloc[-1]] + future_years,
        [population[-1]] + forecast_values,
        linestyle='--',
        label="Прогноз"
    )

    plt.fill_between(
        [df['Год'].iloc[-1]] + future_years,
        [population[-1]] + forecast_values,
        alpha=0.2
    )

    plt.axvline(x=last_year, linestyle='--')

    plt.title("Прогноз населения")
    plt.xlabel("Год")
    plt.ylabel("Млн человек")
    plt.legend()
    plt.grid()

    plt.show()



# добавлен модуль для полноценного запуска из главного меню

def run_polya():
    sg.theme('LightBlue2')

    layout = [
        [sg.Text(
            "Анализ численности населения РФ",
            font=("Helvetica", 24),
            justification='center',
            expand_x=True
        )],

        [sg.Text("Выберите Excel файл:", expand_x=True, justification='center')],

        [sg.Input(key='-FILE-', expand_x=True),
         sg.FileBrowse(size=(15, 1))],

        [sg.Button("Загрузить данные", size=(30, 2), expand_x=True)],

        [sg.TabGroup([[

            sg.Tab("Таблица", [
                [sg.Button("Показать таблицу", expand_x=True, expand_y=True)]
            ]),

            sg.Tab("График", [
                [sg.Button("Построить график", expand_x=True, expand_y=True)]
            ]),

            sg.Tab("Анализ", [
                [sg.Button("Показать анализ", expand_x=True, expand_y=True)]
            ]),

            sg.Tab("Прогноз", [
                [sg.Text("Окно:"), sg.Input("3", key='-W-', size=(5, 1))],
                [sg.Text("Лет:"), sg.Input("5", key='-N-', size=(5, 1))],
                [sg.Button("Построить прогноз", expand_x=True, expand_y=True)]
            ])

        ]], expand_x=True, expand_y=True)],

        [sg.Button("Выход", expand_x=True)]
    ]

    window = sg.Window(
        "Население России",
        layout,
        resizable=True,
        finalize=True,
        element_justification='center'
    )

    window.maximize()

    df = None

    while True:
        event, values = window.read()

        if event in (sg.WIN_CLOSED, "Выход"):
            break

        if event == "Загрузить данные":
            try:
                df = load_data(values['-FILE-'])
                validate_df(df)
                sg.popup("Файл загружен!")
            except Exception as e:
                sg.popup_error(f"Ошибка:\n{e}")

        if df is None:
            continue

        if event == "Показать таблицу":
            show_table(df)

        elif event == "Построить график":
            plot_graph(df)

        elif event == "Показать анализ":
            analyze(df)

        elif event == "Построить прогноз":
            try:
                w = int(values['-W-'])
                n = int(values['-N-'])
                forecast(df, w, n)
            except:
                sg.popup_error("Ошибка ввода")

    window.close()


# чтобы можно было запускать отдельно
if __name__ == "__main__":
    run_polya()