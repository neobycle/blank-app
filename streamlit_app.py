import streamlit as st
import pandas as pd
import altair as alt

st.title("📊 스터디 참석 및 리더 현황 ")

uploaded_file = st.file_uploader("엑셀 또는 CSV 업로드", type=["xlsx", "csv"])

if uploaded_file is not None:
    # 파일 읽기
    if uploaded_file.name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file)
    else:
        df = pd.read_csv(uploaded_file)

    # 회차 컬럼
    week_cols = [col for col in df.columns if "회차" in col and "_리더" not in col]

    # 사람 리스트
    people = df["이름"].tolist()
    num_people = len(people)

    # 4회씩 순환 리더 배정 (NaN/공백 안전 처리)
    for i, week in enumerate(week_cols):
        person_idx = (i // 4) % num_people
        leader_name = people[person_idx]
        df[f"{week}_리더"] = df["이름"].apply(lambda x: "리더" if str(x).strip() == leader_name else "")

    leader_cols = [col for col in df.columns if "_리더" in col]

    # 참석/불참 계산
    def calc_attendance(row):
        attended = (row[week_cols] == "참석").sum()
        absent = (row[week_cols] == "불참").sum()
        total_recorded = row[week_cols].notna().sum()
        attendance_rate = round(attended / total_recorded * 100, 1) if total_recorded > 0 else 0
        absent_weeks = ", ".join([week for week in week_cols if str(row[week]).strip() == "불참"])
        return pd.Series([attended, absent, attendance_rate, absent_weeks])

    result = df.copy()
    result[["참석 횟수","불참 횟수","출석률(%)","불참 회차"]] = result.apply(calc_attendance, axis=1)

    # 리더 횟수 계산 (NaN/공백 안전 처리)
    def calc_leader_count(row):
        return sum(1 for col in leader_cols if str(row[col]).strip() == "리더")

    result["리더 횟수"] = result.apply(calc_leader_count, axis=1)
    MAX_LEADER = 4
    result["남은 리더 횟수"] = MAX_LEADER - result["리더 횟수"]

    # 테이블 표시 (1부터 시작)
    display_df = result[["이름", "참석 횟수", "불참 횟수", "출석률(%)",
                         "불참 회차", "리더 횟수", "남은 리더 횟수"]]
    display_df.index = display_df.index + 1
    display_df.index.name = "번호"
    st.subheader("👤 사람별 참석 및 리더 현황")
    st.dataframe(display_df, use_container_width=True)

    # 개인별 출석률 그래프
    st.subheader("📈 개인별 출석률 그래프")
    chart_attendance = alt.Chart(result).mark_bar().encode(
        x=alt.X('이름', sort=None),
        y=alt.Y('출석률(%)'),
        color=alt.Color('이름', legend=None)
    ).properties(width=600, height=400)
    st.altair_chart(chart_attendance, use_container_width=True)

    # 개인별 리더 횟수 그래프
    st.subheader("📊 개인별 리더 횟수 그래프")
    chart_leader = alt.Chart(result).mark_bar().encode(
        x=alt.X('이름', sort=None),
        y=alt.Y('리더 횟수'),
        color=alt.Color('이름', legend=None)
    ).properties(width=600, height=400)
    st.altair_chart(chart_leader, use_container_width=True)
