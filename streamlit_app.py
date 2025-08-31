import streamlit as st
import pandas as pd

st.title("📊 회의 참석 현황 분석")

# 파일 업로드
uploaded_file = st.file_uploader("회의 참석자 엑셀 파일을 업로드하세요", type=["xlsx"])

if uploaded_file is not None:
    # 데이터 불러오기
    df = pd.read_excel(uploaded_file)
    st.subheader("📋 업로드한 데이터")
    st.dataframe(df, use_container_width=True)

    # 참석 현황 집계
    weeks = [col for col in df.columns if "주차" in col]
    summary = {}
    for week in weeks:
        attend_count = (df[week] == "참석").sum()
        absent_count = (df[week] == "불참").sum()
        summary[week] = {"참석": attend_count, "불참": absent_count}

    summary_df = pd.DataFrame(summary).T
    st.subheader("✅ 주차별 참석 현황 요약")
    st.dataframe(summary_df)

    # Streamlit 내장 바 차트
    st.subheader("📈 주차별 참석/불참 그래프")
    st.bar_chart(summary_df)
