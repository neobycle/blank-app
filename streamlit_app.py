import streamlit as st
import pandas as pd
import altair as alt
import numpy as np

st.title("📊 사람별 회의 참석 및 리더 현황")

# 파일 업로드
uploaded_file = st.file_uploader("엑셀 또는 CSV 업로드", type=["xlsx", "csv"])

if uploaded_file is not None:
    # 파일 불러오기
    if uploaded_file.name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file)
    else:
        df = pd.read_csv(uploaded_file)

    st.subheader("📋 업로드한 데이터")
    st.dataframe(df, use_container_width=True)

    # 주차 컬럼 찾기
    week_cols = [col for col in df.columns if "회차" in col]

    # 참석/불참 계산 함수
    def calc_attendance(row):
        attended = (row[week_cols] == "참석").sum()
        absent = (row[week_cols] == "불참").sum()
        total_recorded = row[week_cols].notna().sum()  # 등록된 주차만 계산
        attendance_rate = round(attended / total_recorded * 100, 1) if total_recorded > 0 else 0
        absent_weeks = ", ".join([week for week in week_cols if str(row[week]).strip() == "불참"])
        return pd.Series([attended, absent, attendance_rate, absent_weeks])

    result = df.copy()
    result[["참석 횟수","불참 횟수","출석률(%)","불참 주차"]] = result.apply(calc_attendance, axis=1)

    # 리더 현황
    MAX_LEADER = 4
    np.random.seed(42)  # 테스트용 랜덤 배정
    result["리더 횟수"] = np.random.randint(0, MAX_LEADER+1, size=len(result))
    result["남은 리더 횟수"] = MAX_LEADER - result["리더 횟수"]

    # 숫자형 보장
    result["출석률(%)"] = pd.to_numeric(result["출석률(%)"], errors='coerce')

    # 테이블: 1부터 시작하는 인덱스
    st.subheader("👤 사람별 참석 및 리더 현황")
    display_df = result[["이름", "참석 횟수", "불참 횟수", "출석률(%)", "불참 주차", "리더 횟수", "남은 리더 횟수"]]
    display_df.index = display_df.index + 1
    display_df.index.name = "번호"
    st.dataframe(display_df, use_container_width=True)

    # 개인별 출석률 그래프
    st.subheader("📈 개인별 출석률 그래프")
    chart_attendance = alt.Chart(result).mark_bar().encode(
        x=alt.X('이름', sort=None, title='이름'),
        y=alt.Y('출석률(%)', title='출석률 (%)'),
        color=alt.Color('이름', legend=None)
    ).properties(width=600, height=400, title="개인별 출석률")
    st.altair_chart(chart_attendance, use_container_width=True)

    # 개인별 리더 횟수 그래프
    st.subheader("📊 개인별 리더 횟수 그래프")
    chart_leader = alt.Chart(result).mark_bar().encode(
        x=alt.X('이름', sort=None, title='이름'),
        y=alt.Y('리더 횟수', title='리더 횟수'),
        color=alt.Color('이름', legend=None)
    ).properties(width=600, height=400, title="개인별 리더 횟수")
    st.altair_chart(chart_leader, use_container_width=True)
