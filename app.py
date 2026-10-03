import streamlit as st
import datetime
import pandas as pd
import os
import io
import sys
from contextlib import redirect_stdout
from unittest.mock import patch

# Настройка страницы
st.set_page_config(page_title="Практикум Python", page_icon="💻", layout="wide")

DATA_FILE = "results.csv"

# --- Функция автопроверки (Runner) ---
def run_student_code(code, mock_inputs):
    """
    Запускает код ученика. Подменяет встроенный input() на заранее заготовленные данные.
    Перехватывает все принты (sys.stdout).
    """
    f = io.StringIO()
    try:
        # Подменяем input и перехватываем print
        with patch('builtins.input', side_effect=mock_inputs):
            with redirect_stdout(f):
                # Запускаем код в изолированном пространстве (без доступа к глобальным переменным приложения)
                exec(code, {"__builtins__": __builtins__})
        
        output = f.getvalue()
        return True, output
    except Exception as e:
        # Если код упал с ошибкой (например SyntaxError или закончились inputs)
        return False, str(e)

def save_submission(name, group, task_num, points, code_text, is_passed):
    status = "Успешно" if is_passed else "Требует ручной проверки / Ошибка"
    new_data = pd.DataFrame({
        "Время": [datetime.datetime.now().strftime('%H:%M:%S')],
        "Имя": [name.strip()],
        "Группа": [group],
        "Задача": [task_num],
        "Баллы": [points if is_passed else 0],
        "Статус": [status],
        "Код": [code_text]
    })
    
    if not os.path.exists(DATA_FILE):
        new_data.to_csv(DATA_FILE, index=False)
    else:
        new_data.to_csv(DATA_FILE, mode='a', header=False, index=False)

# --- Боковая панель: Таблица лидеров ---
st.sidebar.header("Таблица лидеров 🏆")
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
    leaderboard = df.groupby("Имя")["Баллы"].sum().sort_values(ascending=False).reset_index()
    st.sidebar.dataframe(leaderboard, hide_index=True, use_container_width=True)
else:
    st.sidebar.info("Пока нет сданных задач. Будь первым!")

# --- Словари задач (Название, Баллы, Условие, Тестовые данные для input) ---
tasks_beginner = {
    1: ("Умное приветствие", 5, "Запросить имя, запросить возраст. Вывести приветствие и возраст + 1.", ["Алихан", "15"]),
    2: ("Калькулятор", 5, "Ввод: цена 1 кг, вес. Вывод: стоимость и сдача с 1000.", ["200", "2.5"]),
    3: ("Дележ яблок", 5, "Ввод: N (школьников), K (яблок). Вывести сколько каждому и остаток.", ["6", "50"]),
    4: ("Электронные часы", 10, "Ввод: N минут с начала суток. Вывод: Часы и Минуты (через принт).", ["150"]),
    5: ("Парты", 10, "Ввод: a, b, c учеников (3 раза input). Сколько парт нужно? Формула `(n+1)//2`.", ["20", "21", "22"]),
    6: ("Площадь и периметр", 5, "Ввод: a, b (стороны). Вывод: площадь и периметр.", ["4", "5"]),
    7: ("Обмен значениями", 5, "Ввод: x, y. Поменять местами и вывести.", ["10", "99"]),
    8: ("Последняя цифра", 5, "Ввод: целое число. Вывод: его последняя цифра.", ["123456789"]),
    9: ("Сумма цифр", 10, "Ввод: трехзначное число. Вывод: сумма цифр.", ["456"]),
    10: ("Автопробег", 10, "Ввод: N км/день, M км маршрут. Вывод: сколько дней.", ["700", "750"]),
    # Новые задачи
    11: ("Разделение времени", 10, "Пользователь вводит количество секунд. Перевести в часы, минуты и секунды.", ["3665"]),
    12: ("Соседи числа", 5, "Ввод: число. Вывести строку: 'Для числа N соседи N-1 и N+1'.", ["15"]),
    13: ("Гипотенуза", 5, "Ввод: катеты a и b. Найти гипотенузу по теореме Пифагора (возведение в степень `**0.5`).", ["3", "4"]),
    14: ("Сумма прогрессии", 10, "Ввод: число N. Найти сумму всех чисел от 1 до N по формуле `N*(N+1)//2`.", ["100"]),
    15: ("Площадь круга", 10, "Ввод: радиус R. Вывести длину окружности (2*pi*R) и площадь (pi*R**2), считая pi=3.14.", ["10"])
}

# НОВЫЕ задачи для продвинутых (усложненные)
tasks_advanced = {
    1: ("Правильная скобочная последовательность", 15, "Дана строка со скобками '()', '{}', '[]'. Вернуть True/False. (Использовать стек).", []),
    2: ("Одиночное число", 10, "Массив, где все числа встречаются дважды, кроме одного. Найти это число за O(n) (XOR или словарь).", []),
    3: ("Перенос нулей", 15, "Дан массив. Перенести все нули в конец, сохранив порядок остальных чисел (in-place, без доп. памяти).", []),
    4: ("Максимальный подмассив (Кадане)", 20, "Найти непрерывный подмассив с наибольшей суммой и вернуть эту сумму.", []),
    5: ("Пересечение массивов", 15, "Даны 2 массива. Вернуть массив их общих элементов (без дубликатов).", []),
    6: ("Группировка анаграмм", 20, "Дан массив строк (слов). Сгруппировать их так, чтобы анаграммы оказались в одном списке.", [])
}

# --- Основной интерфейс ---
st.title("Практикум по Python 🐍")

group = st.selectbox("Выберите вашу группу:", ["Начинающие", "Олимпиадники"])

st.divider()

col1, col2 = st.columns([1, 1])

with col1:
    st.header("Условия задач")
    current_tasks = tasks_beginner if group == "Начинающие" else tasks_advanced
    
    if group == "Начинающие":
        st.info("⚠️ Не используйте `if/else`, циклы и списки. Только переменные, `input()`, `print()` и математика (`+`, `-`, `*`, `/`, `//`, `%`, `**`).")
    else:
        st.info("⚡ Олимпиадникам: пишите код в виде функций. В проверяющую систему отправляйте только сам алгоритм.")
        
    for k, v in current_tasks.items():
        st.markdown(f"**{k}. {v[0]} (+{v[1]} баллов)**<br>{v[2]}", unsafe_allow_html=True)
        st.write("---")

with col2:
    st.header("Сдача решения")
    student_name = st.text_input("Ваше имя:")
    
    task_options = [f"Задача {k}: {v[0]}" for k, v in current_tasks.items()]
    selected_task_str = st.selectbox("Какую задачу вы сдаете?", task_options)
    
    task_num = int(selected_task_str.split(":")[0].replace("Задача ", ""))
    points_for_task = current_tasks[task_num][1]
    
    submission_type = st.radio("Как будете сдавать?", ["Вставить код (с автопроверкой)", "Загрузить фото/скриншот"])
    
    code_content = ""
    if submission_type == "Вставить код (с автопроверкой)":
        st.caption("Скопируйте ваш код сюда. Мы попытаемся запустить его с тестовыми данными!")
        code_content = st.text_area("Ваш код:", height=200)
    else:
        photo_input = st.file_uploader("Сделайте фото кода", type=['jpg', 'png'])
        if photo_input:
            code_content = f"Фото загружено: {photo_input.name}"

    if st.button("Проверить и отправить", type="primary"):
        if not student_name:
            st.error("Пожалуйста, введите ваше имя!")
        elif not code_content.strip():
            st.error("Код или фото не предоставлены!")
        else:
            # Логика сохранения и проверки
            is_passed = True # По умолчанию, если фото, считаем отправленным на ручную проверку
            
            if submission_type == "Вставить код (с автопроверкой)":
                if group == "Начинающие":
                    test_inputs = current_tasks[task_num][3]
                    st.write(f"🏃 **Запуск с тестовыми данными:** {test_inputs}")
                    
                    success, output = run_student_code(code_content, test_inputs)
                    
                    if success:
                        st.success("Код выполнен успешно!")
                        st.code(f"Вывод программы:\n{output}", language="text")
                        is_passed = True
                    else:
                        st.error("Ошибка при выполнении кода (возможно, не хватает input() или синтаксическая ошибка):")
                        st.code(output, language="python")
                        is_passed = False
                else:
                    # Для олимпиадников сложно проверять через input, так как они пишут функции.
                    # Просто сохраняем.
                    st.info("Код алгоритма принят на ручную проверку.")

            if is_passed:
                save_submission(student_name, group, task_num, points_for_task, code_content, is_passed=True)
                st.balloons()
                st.success(f"Решение отправлено! Предварительно начислено {points_for_task} баллов.")
            else:
                save_submission(student_name, group, task_num, 0, code_content, is_passed=False)
                st.warning("Код упал с ошибкой. Попробуйте исправить и отправить снова (попытка сохранена с 0 баллов).")
