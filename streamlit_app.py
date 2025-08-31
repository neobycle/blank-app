import streamlit as st
import pandas as pd

st.title("📊 사람별 회의 참석 현황 분석 (열 기반 주차)")

uploaded_file = st.file_uploader("엑셀 또는 CSV 파일 업로드", type=["xlsx", "csv"])

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

    # 사람별 참석/불참 계산 함수
    def calc_attendance(row):
        attended = (row[week_cols] == "참석").sum()
        absent = (row[week_cols] == "불참").sum()
        total_recorded = row[week_cols].notna().sum()  # 등록된 주차만 계산
        attendance_rate = round(attended / total_recorded * 100, 1) if total_recorded > 0 else 0
        absent_weeks = ", ".join([week for week in week_cols if row[week] == "불참"])
        return pd.Series([attended, absent, attendance_rate, absent_weeks])

    result = df.copy()
    result[["참석 횟수", "불참 횟수", "출석률(%)", "불참 주차"]] = result.apply(calc_attendance, axis=1)

    # 숫자형으로 보장
    result["출석률(%)"] = pd.to_numeric(result["출석률(%)"], errors='coerce')

    # 요약 테이블 표시
    st.subheader("👤 사람별 참석 현황 요약")
    st.dataframe(
        result[["이름", "참석 횟수", "불참 횟수", "출석률(%)", "불참 주차"]],
        use_container_width=True
    )

    # 그래프 표시
    st.subheader("📈 개인별 출석률 그래프")
    chart_df = result.set_index("이름")[["출석률(%)"]].dropna()
    st.bar_chart(chart_df)
