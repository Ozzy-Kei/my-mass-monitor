from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st
from supabase import create_client


japan = ZoneInfo("Asia/Tokyo")


supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

def _restore_session():
    """Supabase Auth Sessionを復元する"""
    supabase.auth.set_session(
        st.session_state["access_token"],
        st.session_state["refresh_token"],
    )

# Show today's data
def show_data():
    _restore_session()
    today = datetime.now(japan).date().isoformat()
    response = (
        supabase
        .table("health_records")
        .select("*")
        .eq("measurement_date", today)
        .execute()
    )

    data = response.data

    data_summary = []

    for d in data:
        data_summary.append(
            {
                "測定日": d["measurement_date"],
                "測定時刻": d["measurement_time"],
                "体重 (kg)": f'{d["weight"]:.1f}',
                "運動": d["exercise"] if d["exercise"] is not None else "—",
                "飲食": d["eating"] if d["eating"] is not None else "—",
                "睡眠": d["sleep"] if d["sleep"] is not None else "—",
            }
        )

    df = pd.DataFrame(data_summary)
    st.dataframe(df)


def insert_data(
    user_id,
    date_,
    time_,
    weight,
    exercise,
    eating,
    sleep_time,
):
    """health_recordsにデータをINSERTする"""

    _restore_session()

    data = {
        "user_id": user_id,
        "measurement_date": str(date_),
        "measurement_time": str(time_),
        "weight": weight,
        "exercise": exercise,
        "eating": eating,
        "sleep": sleep_time,
    }

    response = (
        supabase
        .table("health_records")
        .insert(data)
        .execute()
    )

    return response.data


def select_data(user_id):
    _restore_session()
    response = (
        supabase
        .table("health_records")
        .select("*")
        .eq("user_id", user_id)
        .order("measurement_date")
        .order("measurement_time")
        .execute()
    )

    return response.data

def make_weight_data(records):
    return {
        "day": [
            record["measurement_date"]
            for record in records
        ],
        "weight": [
            record["weight"]
            for record in records
        ],
    }