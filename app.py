import streamlit as st
import datetime
import pandas as pd
import os

# Настройка страницы
st.set_page_config(page_title="Задачи по Python", page_icon="🐍")

# --- Функция для сохранения результатов ---
DATA_FILE = "results.csv"

def save_submission(name, group, task_num, points, code_text):
    # Создаем строку с данными
    new_data = pd.DataFrame({
        "Время": [datetime.datetime.now().strftime('%H:%M:%S')],
        "Имя": [name.strip()],
        "Группа": [group],
        "Задача": [task_num],
        "Баллы": [points],
        "Код": [code_text]
    })
    
    # Если файл есть, дописываем в конец, если нет - создаем
    if not os.path.exists(DATA_FILE):
        new_data.to_csv(DATA_FILE, index=False)
    else:
        new_data.to_csv(DATA_FILE, mode='a', header=False, index=False)

# --- Боковая панель: Таблица лидеров ---
st.sidebar.header("Таблица лидеров 🏆")
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
    # Группируем по имени и суммируем баллы
    leaderboard = df.groupby("Имя")["Баллы"].sum().sort_values(ascending=False).reset_index()
    # Выводим красивую таблицу без индексов
    st.sidebar.dataframe(leaderboard, hide_index=True, use_container_width=True)
else:
    st.sidebar.info("Пока нет сданных задач. Будь первым!")

# --- Основной интерфейс ---
st.title("Практикум по Python 🐍")

# Выбор группы
group = st.selectbox("Выберите вашу группу:", ["Начинающие", "Олимпиадники"])

# Словари с задачами и баллами
tasks_beginner = {
    1: ("Умное приветствие", 5),
    2: ("Калькулятор покупок", 5),
    3: ("Дележ яблок", 5),
    4: ("Электронные часы", 10),
    5: ("Парты", 10),
    6: ("Площадь и периметр", 5),
    7: ("Обмен значениями", 5),
    8: ("Последняя цифра", 5),
    9: ("Сумма цифр", 10),
    10: ("Автопробег", 10)
}

tasks_advanced = {
    1: ("Сжатие строки (RLE)", 10),
    2: ("Поиск анаграмм", 15),
    3: ("Скользящее окно", 15),
    4: ("Слияние интервалов", 20),
    5: ("Бинарный поиск", 15),
    6: ("Два числа (Two Sum)", 20)
}

st.divider()

if group == "Начинающие":
    st.header("Задачи для начинающих")
    st.markdown("В этих задачах нельзя использовать условия (`if/else`) и циклы. Только переменные, ввод/вывод и математика!")
    for k, v in tasks_beginner.items():
        st.markdown(f"**{k}. {v[0]} (+{v[1]} баллов).**")
else:
    st.header("Задачи для продвинутых")
    st.markdown("Здесь важна не только правильность, но и алгоритмическая сложность!")
    for k, v in tasks_advanced.items():
        st.markdown(f"**{k}. {v[0]} (+{v[1]} баллов).**")

st.divider()

# Форма сдачи решения
st.header("Сдача решения")
student_name = st.text_input("Ваше имя:")

current_tasks = tasks_beginner if group == "Начинающие" else tasks_advanced
task_options = [f"Задача {k}: {v[0]} ({v[1]} баллов)" for k, v in current_tasks.items()]
selected_task_str = st.selectbox("Какую задачу вы сдаете?", task_options)

task_num = int(selected_task_str.split(":")[0].replace("Задача ", ""))
points_for_task = current_tasks[task_num][1]

submission_type = st.radio("Как будете сдавать?", ["Вставить код текстом", "Загрузить фото экрана"])

code_content = ""
if submission_type == "Вставить код текстом":
    code_content = st.text_area("Вставьте ваш код сюда:", height=150)
else:
    photo_input = st.file_uploader("Сделайте фото кода или прикрепите скриншот", type=['jpg', 'jpeg', 'png'])
    if photo_input is not None:
        code_content = f"Фото загружено: {photo_input.name}"

if st.button("Отправить решение", type="primary"):
    if not student_name:
        st.error("Пожалуйста, введите ваше имя!")
    elif submission_type == "Вставить код текстом" and not code_content.strip():
         st.error("Пожалуйста, вставьте код!")
    elif submission_type == "Загрузить фото экрана" and not code_content:
         st.error("Пожалуйста, загрузите фотографию!")
    else:
        # Сохраняем в CSV
        save_submission(student_name, group, task_num, points_for_task, code_content)
        
        st.success(f"Отлично, {student_name}! Ваше решение отправлено.")
        st.info(f"Вам начислено **{points_for_task} баллов**! Посмотрите в таблицу лидеров слева (возможно, понадобится обновить страницу).")
        st.balloons()
