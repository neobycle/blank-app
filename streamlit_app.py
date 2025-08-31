import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.title("📊 사람별 회의 참석 현황 분석 (개인별 색상 그래프)")

uploaded_file = st.file_uploader("엑셀 또는 CSV 업로드", type=["xlsx", "csv"])

if uploaded_file is not None:
    if uploaded_file.name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file)
    else:
        df = pd.read_csv(uploaded_file)

    # 주차 컬럼 찾기
    week_cols = [col for col in df.columns if "회차" in col]

    # 참석 현황 계산
    def calc_attendance(row):
        attended = (row[week_cols] == "참석").sum()
        absent = (row[week_cols] == "불참").sum()
        total_recorded = row[week_cols].notna().sum()
        attendance_rate = round(attended / total_recorded * 100, 1) if total_recorded > 0 else 0
        absent_weeks = ", ".join([week for week in week_cols if str(row[week]).strip() == "불참"])
        return pd.Series([attended, absent, attendance_rate, absent_weeks])

    result = df.copy()
    result[["참석 횟수","불참 횟수","출석률(%)","불참 주차"]] = result.apply(calc_attendance, axis=1)

    # 개인별 출석률 그래프
    st.subheader("📈 개인별 출석률 그래프")
    plt.figure(figsize=(10,5))
    
    names = result["이름"]
    attendance = result["출석률(%)"]
    
    # 사람마다 다른 색상 지정
    colors = plt.cm.tab20(np.arange(len(names)))  # 최대 20명까지 다른 색
    plt.bar(names, attendance, color=colors)
    
    plt.ylabel("출석률 (%)")
    plt.ylim(0, 100)
    plt.xticks(rotation=45)
    plt.title("개인별 출석률")
    
    st.pyplot(plt)
