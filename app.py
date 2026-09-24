from datetime import datetime, date
from zoneinfo import ZoneInfo
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from streamlit_js_eval import streamlit_js_eval

import module.module_db as m_db
import module.module_show_plot as m_sp
import module.module_calendar_stamp as m_cs

from supabase import create_client, ClientOptions

st.markdown(
        """
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
        """,
        unsafe_allow_html=True
    )

japan = ZoneInfo("Asia/Tokyo")
# time info
current = datetime.now(japan)
current_time = current.strftime('%Y-%m-%d %H:%M:%S')
now = datetime.now(japan)
today = now.date()
current_time_now = now.time()

supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"],
    options=ClientOptions(flow_type="pkce")
)

if "password_recovery" not in st.session_state:
    st.session_state["password_recovery"] = False

if "access_token" in st.session_state and "refresh_token" in st.session_state:
    supabase.auth.set_session(
        st.session_state["access_token"],
        st.session_state["refresh_token"]
    )
    supabase.postgrest.auth(st.session_state["access_token"])

# Calendar Stamp表示用
if "show_stamp" not in st.session_state:
    st.session_state.show_stamp = False

# ============================================================
# パスワード再設定用：ブラウザURLからトークンを取得
# ============================================================

if "reset_authenticated" not in st.session_state:
    st.session_state["reset_authenticated"] = False
current_url = streamlit_js_eval(
    js_expressions="window.parent.location.href",
    want_output=True,
    key="get_url"
)

access_token = None
refresh_token = None
if current_url and "#" in current_url:
    try:
        hash_query = current_url.split("#", 1)[1]
        params = {}
        for item in hash_query.split("&"):
            if "=" in item:
                key, value = item.split("=", 1)
                params[key] = value
        access_token = params.get("access_token")
        refresh_token = params.get("refresh_token")
    except Exception as e:
        st.error(f"URLの解析中にエラーが発生しました: {e}")


# ============================================================
# パスワード再設定セッションを確立
# ============================================================

if (
    access_token
    and refresh_token
    and not st.session_state["reset_authenticated"]
):
    try:
        supabase.auth.set_session(
            access_token,
            refresh_token
        )
        st.session_state["reset_authenticated"] = True
        st.rerun()
    except Exception as e:
        st.error(f"認証に失敗しました: {e}")

# ============================================================ #
# 画面表示
# ============================================================ #
#if st.session_state.reset_authenticated:
#else:
#    st.info("パスワードリセットメールのリンクからアクセスしてください。")

if "user_id" not in st.session_state:
    if st.session_state["reset_authenticated"]:
        st.subheader("パスワード リセット/再設定")
        st.success("認証に成功しました。新しいパスワードを設定してください。")

        with st.form("new_password_form"):
            re_password = st.text_input("新しいパスワード", type="password", placeholder="パスワードを入力してください.")
            re_password_confirm = st.text_input("新しいパスワード(確認用)", type="password", placeholder="もう一度、パスワードを入力してください.")
            submit = st.form_submit_button("パスワードを更新")

            if submit:
                if not re_password:
                    st.error("新しいパスワードを入力してください。")
                elif re_password != re_password_confirm:
                    st.error("パスワードが一致していません。")
                else:
                    try:
                        supabase.auth.update_user({"password": re_password})
                        st.success("パスワードが正常に更新されました！")
                        if st.button("ログイン画面に戻る"):
                            st.session_state["reset_authenticated"] = False
                            st.rerun()
                    except Exception as e:
                        st.error(f"パスワードの更新に失敗しました: {e}")

    elif st.session_state.get("reset_password", False):
        st.subheader("パスワード再設定")
        reset_email = st.text_input("メールアドレス", placeholder="example@domain.com")
        if st.button("再設定メールを送信"):
            if not reset_email:
                st.error("メールアドレスを入力してください。")
            else:
                try:
                    supabase.auth.reset_password_for_email(
                        reset_email,
                        options={
                            #"redirect_to": "http://localhost:8501" # streamlitでは違うURL
                            "redirect_to": "https://weight-health-tracker.streamlit.app" # streamlitでは違うURL
                        }
                    )

                    st.success(
                        "パスワード再設定用のメールを送信しました。"
                        "メールをご確認ください。"
                    )
                except Exception as e:
                    st.error("メールの送信に失敗しました。")
                    st.exception(e)
        if st.button("ログイン画面に戻る"):
            st.session_state["reset_password"] = False
            st.rerun()
    #elif 
    else:
        st.subheader("ログイン")

        mode = st.radio(
            "操作を選択",
            ["ログイン", "アカウント作成"],
            horizontal=True
        )

        if mode == "ログイン":
            email = st.text_input("メールアドレス", placeholder="name@example.com")
            password = st.text_input("パスワード", type="password", placeholder="パスワードを入力")

            if st.button("ログイン"):
                try:
                    response = supabase.auth.sign_in_with_password({
                        "email": email,
                        "password": password,
                    })
                    if response.session is None:
                        st.error("Sessionが取得できませんでした")
                    else:
                        st.session_state["user_id"] = response.user.id
                        st.session_state["access_token"] = (
                            response.session.access_token
                        )
                        st.session_state["refresh_token"] = (
                            response.session.refresh_token
                        )
                        st.success("ログイン成功")
                        st.rerun()

                except Exception as e:
                    st.error("ログインに失敗しました")
                    st.exception(e)

            st.write("パスワードをお忘れですか?")
            if st.button("パスワードを忘れた"):
                st.session_state["reset_password"] = True
                st.rerun()

        elif mode == "アカウント作成":
            email = st.text_input("メールアドレス", placeholder="name@example.com")
            user_name = st.text_input("アカウント名", placeholder="account name")
            password = st.text_input("パスワード", type="password", placeholder="パスワードを入力してください.")
            password_confirm = st.text_input("パスワード（確認）", type="password", placeholder="もう一度、パスワードを入力してください.")
            if st.button("アカウント作成"):
                # 入力チェック
                if not email or not password or not user_name:
                    st.error("メールアドレスとパスワード、アカウント名を入力してください。")
                elif password != password_confirm:
                    st.error("パスワードが一致していません。")
                else:
                    try:
                        # Supabase Authにユーザー登録
                        response = supabase.auth.sign_up({
                            "email": email,
                            "password": password,
                            "options": {
                                "data": {
                                    "user_name": user_name
                                }
                            }
                        })
                        # 登録成功
                        if response.user is not None:
                            st.success("アカウント登録が完了しました！")
                            st.write(f"User ID: {response.user.id}")
                    except Exception as e:
                        st.error(f"登録に失敗しました: {e}")

if "user_id" in st.session_state:
    st.title("健康管理/モニター")
    m_db.show_data()

    st.write(f"現在時刻: {current_time}")

    st.divider()
    if st.button("ログアウト"):
        supabase.auth.sign_out()
        st.session_state.pop("user_id", None)
        st.session_state.pop("access_token", None)
        st.session_state.pop("refresh_token", None)
        st.success("ログアウトしました")
        st.rerun()

    st.subheader("パスワード変更")

    new_password = st.text_input("新しいパスワード", type="password", placeholder="パスワードを入力してください.")

    new_password_confirm = st.text_input("新しいパスワード（確認）", type="password", placeholder="もう一度、パスワードを入力してください.")

    if st.button("パスワードを変更"):
        if not new_password:
            st.error("新しいパスワードを入力してください。")
        elif new_password != new_password_confirm:
            st.error("パスワードが一致していません。")
        else:
            try:
                supabase.auth.update_user({
                    "password": new_password
                })
                st.success("パスワードを変更しました！")
            except Exception as e:
                st.error("パスワードの変更に失敗しました。")
                st.exception(e)

    st.subheader("データ記録")
    user_id = st.session_state["user_id"]

    response = (
        supabase
        .table("profiles")
        .select("user_name")
        .eq("id", user_id)
        .single()
        .execute()
    )

    user_name = response.data["user_name"]

    st.write("現在のUser:")
    st.code(user_name)

    #st.write("現在のUser ID:")
    #st.code(st.session_state["user_id"])

    date_ = st.date_input("測定日", value=today)
    time_ = st.time_input("測定時刻", value=current_time_now)
    weight = st.number_input("Weight", value=90.0)

    with st.expander("追加の記録を入力する."):
        excer_window = st.toggle("運動度合い")
        if excer_window:
            excercise = st.slider('運動度合いを入力してください.', 0, 100, 50, key='excercise')
        else:
            excercise = None
        eat_window = st.toggle("飲食量")
        if eat_window:
            eating = st.slider('飲食量の度合いを入力してください.', 0, 100, 50, key='eating')
        else:
            eating = None
        sleep_window = st.toggle("睡眠の度合い")
        if sleep_window:
            sleep_time = st.slider('睡眠の度合いを入力してください.(default: 6h=50)', 0, 100, 50, key='sleep')
        else:
            sleep_time = None


    if st.button('Add data'):
        user_id = st.session_state["user_id"]
        try:
            result = m_db.insert_data(user_id, date_, time_, weight, excercise, eating, sleep_time)
            st.success("データ追加完了!!")
            st.json(result)
            ########
            ########
            # stamp rally
            ########
            ########
        except Exception as e:
            st.error("INSERTに失敗しました")
            st.exception(e)

    #if st.button("📅 Stump"):
    if st.button("Stump"):
        st.session_state.show_stamp = not st.session_state.show_stamp
    if st.session_state.show_stamp:
        user_id = st.session_state["user_id"]
        records = m_db.select_data(user_id)
        if not records:
            st.info("まだ健康記録がありません。")
        else:
            # data から最初の日付を取得
            dates = []

            for d in records:
                value = d["measurement_date"]

                if isinstance(value, datetime):
                    value = value.date()

                elif not isinstance(value, date):
                    value = datetime.strptime(
                        str(value),
                        "%Y-%m-%d"
                    ).date()

                dates.append(value)

            min_date = min(dates)
            max_date = max(dates)
            # セッションに現在表示中の月を保存
            if "calendar_year" not in st.session_state:
                st.session_state.calendar_year = max_date.year
            if "calendar_month" not in st.session_state:
                st.session_state.calendar_month = max_date.month
            # 月移動
            col1, col2, col3 = st.columns([1, 3, 1])
            with col1:
                if st.button("◀ 前月"):
                    if st.session_state.calendar_month == 1:
                        st.session_state.calendar_year -= 1
                        st.session_state.calendar_month = 12
                    else:
                        st.session_state.calendar_month -= 1
                    st.rerun()
            with col2:
                st.markdown(
                    f"<h2 style='text-align:center;'>"
                    f"{st.session_state.calendar_year}年"
                    f"{st.session_state.calendar_month}月"
                    f"</h2>",
                    unsafe_allow_html=True,
                )
            with col3:
                if st.button("翌月 ▶"):
                    if st.session_state.calendar_month == 12:
                        st.session_state.calendar_year += 1
                        st.session_state.calendar_month = 1
                    else:
                        st.session_state.calendar_month += 1
                    st.rerun()
            # ------------------------------------------------------------
            # スタンプの説明
            # ------------------------------------------------------------
            st.markdown(
                """
                **スタンプの意味**
                🏆 コンプリート　　🟢 2項目以上　　🔵 記録あり　　⚪ 未記録
                """
            )
            # ------------------------------------------------------------
            # カレンダー
            # ------------------------------------------------------------
            m_cs.show_stamp_calendar(
                records,
                st.session_state.calendar_year,
                st.session_state.calendar_month,
            )
            # ------------------------------------------------------------
            # 日付選択
            # ------------------------------------------------------------
            st.divider()
            st.subheader("🔎 日付を選んで詳細を見る")
            selected_date = st.date_input(
                "日付",
                value=date(
                    st.session_state.calendar_year,
                    st.session_state.calendar_month,
                    1,
                ),
            )
            m_cs.show_day_detail(records, selected_date)

    if st.button("Check"):
        user_id = st.session_state["user_id"]
        records = m_db.select_data(user_id)
        data = m_db.make_weight_data(records)
        
        fig_ = m_sp.show_plot(data)
        st.pyplot(fig_)

    if st.button("Analysis"):
        st.write("Preparing now.")
        st.write("Coming soon...")
