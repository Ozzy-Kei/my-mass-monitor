import streamlit as st
import calendar
from datetime import datetime, date


# ============================================================
# データ
# ============================================================
# ここは現在使っている data をそのまま利用してください。
#
# data の例:
# data = [
#     {
#         "measurement_date": "2026-09-01",
#         "measurement_time": "07:30",
#         "weight": 65.2,
#         "exercise": "ウォーキング30分",
#         "eating": "○",
#         "sleep": "7時間",
#     },
#     ...
# ]


# ============================================================
# スタンプ用データを作成
# ============================================================
def create_stamp_data(data):
    stamp_data = {}

    for d in data:
        measurement_date = d["measurement_date"]

        # 日付を date 型に変換
        if isinstance(measurement_date, datetime):
            day = measurement_date.date()
        elif isinstance(measurement_date, date):
            day = measurement_date
        else:
            day = datetime.strptime(
                str(measurement_date), "%Y-%m-%d"
            ).date()

        # 記録されている項目数をカウント
        count = 0

        if d.get("weight") is not None:
            count += 1

        if d.get("exercise") is not None:
            count += 1

        if d.get("eating") is not None:
            count += 1

        if d.get("sleep") is not None:
            count += 1

        # 同じ日に複数レコードがある場合は、
        # より多く記録されている方を採用
        if day not in stamp_data or count > stamp_data[day]["count"]:
            stamp_data[day] = {
                "count": count,
                "data": d,
            }

    return stamp_data


# ============================================================
# カレンダー表示
# ============================================================
def show_stamp_calendar(data, year, month):
    stamp_data = create_stamp_data(data)

    # 月初・月末
    _, last_day = calendar.monthrange(year, month)

    # 曜日
    weekdays = ["月", "火", "水", "木", "金", "土", "日"]

    # CSS
    st.markdown(
        """
        <style>
        .stamp-calendar {
            width: 100%;
        }

        .weekday-row {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 6px;
            margin-bottom: 6px;
        }

        .weekday {
            text-align: center;
            font-weight: bold;
            padding: 6px 0;
            color: #666;
        }

        .calendar-row {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 6px;
            margin-bottom: 6px;
        }

        .day-cell {
            min-height: 85px;
            border: 1px solid #e5e5e5;
            border-radius: 10px;
            padding: 6px;
            background: #fafafa;
        }

        .empty-cell {
            min-height: 85px;
        }

        .day-number {
            font-size: 13px;
            color: #666;
            text-align: left;
        }

        .stamp {
            text-align: center;
            font-size: 30px;
            margin-top: 8px;
        }

        .stamp-label {
            text-align: center;
            font-size: 11px;
            color: #777;
        }

        .complete {
            background: #fff7d6;
            border-color: #f0c94b;
        }

        .partial {
            background: #f4f8ff;
            border-color: #a9c7f5;
        }

        .recorded {
            background: #f3fff5;
            border-color: #9ed5a7;
        }

        .today {
            box-shadow: 0 0 0 2px #ff8a65 inset;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # 曜日
    cols = st.columns(7)

    for i, weekday in enumerate(weekdays):
        cols[i].markdown(
            f"<div style='text-align:center; font-weight:bold;'>{weekday}</div>",
            unsafe_allow_html=True,
        )

    # 月初の曜日
    first_weekday = date(year, month, 1).weekday()

    # 日付を並べる
    cells = [None] * first_weekday + list(range(1, last_day + 1))

    # 週単位で表示
    for week_start in range(0, len(cells), 7):
        week = cells[week_start:week_start + 7]

        cols = st.columns(7)

        for i, day_number in enumerate(week):

            if day_number is None:
                cols[i].markdown(
                    "<div style='height:85px'></div>",
                    unsafe_allow_html=True,
                )
                continue

            current_day = date(year, month, day_number)

            info = stamp_data.get(current_day)

            # 今日かどうか
            today_class = "today" if current_day == date.today() else ""

            # ------------------------------------------------
            # 記録あり
            # ------------------------------------------------
            if info:

                count = info["count"]

                if count >= 4:
                    stamp = "🏆"
                    label = "コンプリート！"
                    css_class = "complete"

                elif count >= 2:
                    stamp = "🟢"
                    label = f"{count}項目記録"
                    css_class = "recorded"

                else:
                    stamp = "🔵"
                    label = "記録あり"
                    css_class = "partial"

            # ------------------------------------------------
            # 未記録
            # ------------------------------------------------
            else:
                stamp = "⚪"
                label = "未記録"
                css_class = ""

            # セル表示
            cols[i].markdown(
                f"""
                <div class="day-cell {css_class} {today_class}">
                    <div class="day-number">{day_number}</div>
                    <div class="stamp">{stamp}</div>
                    <div class="stamp-label">{label}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ============================================================
# 詳細表示
# ============================================================
def show_day_detail(data, selected_date):

    selected = None

    for d in data:
        measurement_date = d["measurement_date"]

        if isinstance(measurement_date, datetime):
            measurement_date = measurement_date.date()

        elif not isinstance(measurement_date, date):
            measurement_date = datetime.strptime(
                str(measurement_date),
                "%Y-%m-%d"
            ).date()

        if measurement_date == selected_date:
            selected = d
            break

    if selected is None:
        st.info("この日は記録がありません。")
        return

    st.markdown(
        f"### {selected_date.strftime('%Y年%m月%d日')} の記録"
    )

    col1, col2 = st.columns(2)

    with col1:
        weight = selected.get("weight")

        if weight is not None:
            st.metric(
                "⚖️ 体重",
                f"{weight:.1f} kg"
            )
        else:
            st.metric("⚖️ 体重", "—")

        st.write(
            "🏃 **運動**　",
            selected.get("exercise") or "—"
        )

    with col2:
        st.write(
            "🍽️ **飲食**　",
            selected.get("eating") or "—"
        )

        st.write(
            "😴 **睡眠**　",
            selected.get("sleep") or "—"
        )

        st.write(
            "⏰ **測定時刻**　",
            selected.get("measurement_time") or "—"
        )
