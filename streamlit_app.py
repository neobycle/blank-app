import streamlit as st
import pandas as pd

st.title("📊 스터디 참석 현황 분석")

# 파일 업로드
uploaded_file = st.file_uploader("회의 참석자 파일을 업로드하세요 (xlsx 또는 csv)", type=["xlsx", "csv"])

if uploaded_file is not None:
    # 파일 불러오기
    if uploaded_file.name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file)
    else:
        df = pd.read_csv(uploaded_file)

    st.subheader("📋 업로드한 데이터")
    st.dataframe(df, use_container_width=True)

    # ✅ 주차 컬럼 찾기
    week_cols = [col for col in df.columns if "주차" in col]

    # ✅ 사람별 참석/불참 횟수 + 출석률 + 불참 주차
    result = df.copy()
    result["참석 횟수"] = (result[week_cols] == "참석").sum(axis=1)
    result["불참 횟수"] = (result[week_cols] == "불참").sum(axis=1)
    result["출석률(%)"] = round(result["참석 횟수"] / len(week_cols) * 100, 1)
    result["불참 주차"] = result[week_cols].apply(
        lambda row: ", ".join([week for week in week_cols if row[week] == "불참"]),
        axis=1
    )

    # ✅ 결과 표시
    st.subheader("👤 사람별 참석 현황 요약")
    st.dataframe(
        result[["이름", "부서", "이메일", "참석 횟수", "불참 횟수", "출석률(%)", "불참 주차"]],
        use_container_width=True
    )

    # ✅ 그래프 표시 (출석률)
    st.subheader("📈 개인별 출석률 그래프")
    chart_df = result.set_index("이름")["출석률(%)"]
    st.bar_chart(chart_df)
