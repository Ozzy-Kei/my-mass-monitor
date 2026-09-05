from datetime import date, datetime, time
import pandas as pd
import streamlit as st
import sqlite3
import matplotlib.pyplot as plt

conn = sqlite3.connect('health_care.db')
c = conn.cursor()


def show_data():
    c.execute('SELECT * FROM users')
    data = c.fetchall()

    for d in data:
        st.write(d)

# Add data
def add_data(u_n, measurement_date, measurement_time, weight, excercise):
    c.execute(
        'INSERT INTO users (user, day, time, weight, excercise) VALUES (?, ?, ?, ?, ?)',
        (u_n, str(measurement_date), str(measurement_time), weight, excercise)
    )
    conn.commit()
    st.write('Data added. Please reload page.')

def get_data(user_name):
    conn = sqlite3.connect('health_care.db')
    query = """
    SELECT day, weight
    FROM users
    WHERE user = ?
    ORDER BY day
    """
    df = pd.read_sql_query(query, conn, params=(user_name,))
    conn.close()
    return df

def show_plot(data, u_name):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(data["day"], data["weight"], marker="o", color="cornflowerblue")
    ax.set_xlabel("Date")
    ax.set_ylabel("Weight [kg]")
    ax.set_title(f"{u_name} の体重変化")
    ax.grid(True)
    plt.xticks(rotation=45)
    fig.tight_layout()
    return fig



st.title("健康管理/モニター")

c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        day TEXT,
        time TEXT,
        weight FLOAT,
        excercise FLOAT
    )
''')

show_data()


# time info.
current = datetime.now()
current_time = current.strftime('%Y-%m-%d %H:%M:%S')
now = datetime.now()

st.write(f"現在時刻: {current_time}")

# entry new data
user_name = st.selectbox(
    "利用者",
    [
        "おじおじ",
        "ひー",
        "OZZY",
    ]
)
date_ = st.date_input("測定日", value=date.today())
time_ = st.time_input("測定時刻",value=time(now.hour, now.minute))
weight = st.number_input("Weight", value=90.0)

st.write("運動度合いを入力してください.")
excercise = st.slider('Select a value', 0, 100, 50)

st.markdown("""
    <style>
    div.stButton > button {
        background-color: #00ff7b;
        color: white;
        border: none;
    }

    div.stButton > button:hover {
        background-color: #0056b3;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)
if st.button('Add data'):
    add_data(user_name, date_, time_, weight, excercise)
    st.success('Data added.')

checker_name = st.selectbox(
    "確認する利用者",
    [
        "おじおじ",
        "ひー",
        "OZZY",
    ]
)

if st.button("Check"):
    df = get_data(checker_name)
    df["day"] = pd.to_datetime(df["day"])

    fig_ = show_plot(df, checker_name)
    st.pyplot(fig_)