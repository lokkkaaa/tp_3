import PySimpleGUI as sg
import pandas as pd
import matplotlib.pyplot as plt
sg.theme('DarkBlue3')

def load_data():
    df = pd.read_excel("infections.xlsx")
    return df


def validate_df(df):
    """Проверяет, что датафрейм содержит нужные колонки."""
    if df.empty:
        raise ValueError("Файл пустой.")
    if 'Год' not in df.columns:
        raise ValueError("В файле отсутствует колонка 'Год'.")
    if len(df.columns) < 2:
        raise ValueError("В файле нет колонок с данными о заболеваниях.")


def vika_module():
    sg.theme('DarkPurple6')
    try:
        df = load_data()
        validate_df(df)
    except Exception as e:
        sg.popup_error(f"Ошибка загрузки файла:\n{e}", title="Ошибка")
        return

    layout = [
        [sg.Button("Показать таблицу", size=(60, 2))],
        [sg.Button("Графики", size=(60, 2))],
        [sg.Button("Анализ", size=(60, 2))],
        [sg.Button("Прогноз", size=(60, 2))],
        [sg.Button("Назад", size=(60, 2))],
    ]
    window = sg.Window("Модуль Вики", layout, size=(400, 400),font=("Helvetica", 16))

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
            forecast_ui(df)

    window.close()


# ===== Таблица =====

def show_table(df):
    layout = [
        [sg.Table(
            values=df.values.tolist(),
            headings=list(df.columns),
            auto_size_columns=True,
            justification='center',
            num_rows=min(15, len(df)),
            expand_x=True,
        )],
        [sg.Button("Закрыть")],
    ]
    window = sg.Window("Таблица заболеваний", layout, size=(600, 500),font=("Helvetica", 16))
    while True:
        event, _ = window.read()
        if event in (sg.WIN_CLOSED, "Закрыть"):
            break
    window.close()


# ===== Графики =====

def plot_graphs(df):
    years = df['Год']
    fig, ax = plt.subplots(figsize=(10, 6))
    for col in df.columns[1:]:
        ax.plot(years, df[col], marker='o', markersize=3, label=col)
    ax.legend(fontsize=8, loc='upper right')
    ax.set_title("Заболеваемость по годам")
    ax.set_xlabel("Год")
    ax.set_ylabel("Количество случаев")
    ax.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.show()
    plt.close(fig)


# ===== Анализ =====

def analyze(df):
    disease_cols = df.columns[1:]
    changes = {}
    for col in disease_cols:
        start = df[col].iloc[0]
        end = df[col].iloc[-1]
        # Положительное значение = снижение, отрицательное = рост
        changes[col] = start - end

    max_disease = max(changes, key=changes.get)
    min_disease = min(changes, key=changes.get)

    lines = []
    for col, delta in sorted(changes.items(), key=lambda x: -x[1]):
        direction = "снижение" if delta >= 0 else "рост"
        lines.append(f"{col}: {direction} на {abs(delta):.1f}")

    summary = "\n".join(lines)
    max_label = f"Больше всего снизилось: {max_disease} (на {changes[max_disease]:.1f})"
    min_label = (
        f"Меньше всего снизилось: {min_disease} (снижение на {changes[min_disease]:.1f})"
        if changes[min_disease] >= 0
        else f"Выросло больше всего: {min_disease} (рост на {abs(changes[min_disease]):.1f})"
    )

    sg.popup(
        f"{max_label}\n{min_label}\n\nИзменения за период:\n{summary}",
        title="Анализ заболеваемости",
        font = ("Helvetica", 16)
    )


# ===== Скользящая средняя =====

def moving_average(series, window):
    """Возвращает скользящую среднюю. NaN в начале — ожидаемое поведение."""
    return series.rolling(window=window).mean()


def extrapolate(series, window, n_years):
    """
    Прогнозирует n_years значений методом экстраполяции по скользящей средней.
    Каждый следующий прогноз строится на основе последних window значений,
    включая уже спрогнозированные.
    """
    history = list(series)
    forecast = []
    for _ in range(n_years):
        window_values = history[-window:]
        next_val = sum(window_values) / len(window_values)
        forecast.append(next_val)
        history.append(next_val)
    return forecast


# ===== Прогноз (UI) =====

def forecast_ui(df):
    last_year = int(df['Год'].iloc[-1])
    disease_cols = list(df.columns[1:])

    layout = [
        [sg.Text("Период скользящей средней (n лет):"),
         sg.Input("3", key="-WINDOW-", size=(5, 1))],
        [sg.Text("Прогноз на N лет вперёд:"),
         sg.Input("5", key="-NYEARS-", size=(5, 1))],
        [sg.Text("Отображать заболевания:"),
         sg.Listbox(
             values=disease_cols,
             select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE,
             default_values=disease_cols,
             size=(40, min(8, len(disease_cols))),
             key="-DISEASES-"
         )],
        [sg.Button("Построить прогноз"), sg.Button("Отмена")],
    ]
    window = sg.Window("Настройки прогноза", layout)

    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, "Отмена"):
            break
        elif event == "Построить прогноз":
            try:
                window_size = int(values["-WINDOW-"])
                n_years = int(values["-NYEARS-"])
                selected = values["-DISEASES-"]

                if window_size < 1:
                    raise ValueError("Период должен быть не менее 1.")
                if n_years < 1:
                    raise ValueError("Число лет прогноза должно быть не менее 1.")
                if window_size > len(df):
                    raise ValueError(
                        f"Период ({window_size}) не может превышать "
                        f"число лет в данных ({len(df)})."
                    )
                if not selected:
                    raise ValueError("Выберите хотя бы одно заболевание.")

            except ValueError as e:
                sg.popup_error(str(e), title="Ошибка ввода")
                continue

            window.close()
            plot_forecast(df, selected, window_size, n_years, last_year)
            return

    window.close()


def plot_forecast(df, selected_cols, window_size, n_years, last_year):
    future_years = list(range(last_year + 1, last_year + n_years + 1))
    years = list(df['Год'])

    fig, ax = plt.subplots(figsize=(12, 6))
    color_cycle = iter(plt.rcParams['axes.prop_cycle'])

    for col in selected_cols:
        series = df[col]

        # Скользящая средняя по историческим данным
        ma = moving_average(series, window_size)

        # Прогноз
        forecast_values = extrapolate(series, window_size, n_years)

        color = next(color_cycle)['color']

        # Фактические данные
        ax.plot(years, series, color=color, marker='o', markersize=3,
                label=f"{col} (факт)")

        # Скользящая средняя (только там, где не NaN)
        valid_ma = ma.dropna()
        valid_years = list(df['Год'].iloc[window_size - 1:])
        ax.plot(valid_years, valid_ma, color=color, linestyle=':',
                linewidth=1.5, label=f"{col} (скол. ср.)")

        # Прогноз
        # Соединяем последнюю точку факта с первой точкой прогноза
        ax.plot(
            [years[-1]] + future_years,
            [series.iloc[-1]] + forecast_values,
            color=color, linestyle='--', linewidth=1.5,
            label=f"{col} (прогноз)"
        )

        # Закрашиваем область прогноза
        ax.fill_between(
            [years[-1]] + future_years,
            [series.iloc[-1]] + forecast_values,
            alpha=0.08, color=color
        )

    # Вертикальная линия — граница факт/прогноз
    ax.axvline(x=last_year, color='gray', linestyle='--', linewidth=1, alpha=0.6)
    ax.text(last_year + 0.1, ax.get_ylim()[1], 'прогноз →',
            fontsize=9, color='gray', va='top')

    ax.set_title(
        f"Прогноз заболеваемости на {n_years} лет "
        f"(скользящая средняя, окно = {window_size})"
    )
    ax.set_xlabel("Год")
    ax.set_ylabel("Количество случаев")
    ax.legend(fontsize=7, loc='upper right', ncol=2)
    ax.grid(True, linestyle='--', alpha=0.4)
    plt.tight_layout()
    plt.show()
    plt.close(fig)