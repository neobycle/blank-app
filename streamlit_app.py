import streamlit as st
import pandas as pd
import altair as alt

# 웹 페이지 제목 설정
st.title('CSV 파일 업로드 및 #인증 메시지 분석')

# 파일 업로드 위젯 생성
uploaded_file = st.file_uploader('CSV 파일을 업로드하세요', type='csv')

if uploaded_file is not None:
    # 업로드된 CSV 파일을 DataFrame으로 읽기
    df = pd.read_csv(uploaded_file, parse_dates=['Date'])  # 'Date' 컬럼이 날짜 형식일 경우

    # '#인증'이 포함된 메시지 필터링
    df_filtered = df[df['Message'].str.contains('#인증', case=False, na=False)]

    # 날짜만 추출하여 'Date' 컬럼을 datetime에서 date 타입으로 변경
    df_filtered['Date'] = pd.to_datetime(df_filtered['Date']).dt.date  # 날짜만 추출

    # 날짜 형식이 제대로 변환되었는지 확인
    st.write(f"날짜 형식 확인: {df_filtered['Date'].head()}")

    # 사용자로부터 시작일과 종료일 선택받기 (날짜만 사용)
    start_date = st.date_input('시작일을 선택하세요', min(df_filtered['Date']), key='start_date')
    end_date = st.date_input('종료일을 선택하세요', max(df_filtered['Date']), key='end_date')

    # 선택된 기간에 해당하는 데이터만 필터링
    df_filtered = df_filtered[(df_filtered['Date'] >= start_date) & (df_filtered['Date'] <= end_date)]

    # 날짜별 및 사용자별로 카운팅
    df_count = df_filtered.groupby(['User']).size().reset_index(name='인증 횟수')

    # 인덱스를 1부터 시작하도록 설정
    df_count.index = df_count.index + 1

    # 결과 표시 (사용자별 인증 횟수)
    st.write(f'{start_date}부터 {end_date}까지의 사용자별 인증 횟수:')
    st.write(df_count)

    # Altair를 사용하여 유저별 인증 횟수 높은 순으로 그래프 생성
    chart = alt.Chart(df_count).mark_bar().encode(
    x=alt.X('User:N', title='User'),  # x축을 User로 설정
    y=alt.Y('sum(인증 횟수):Q', title='인증 횟수', 
            scale=alt.Scale(domain=[0, df_count['인증 횟수'].max()], 
                            nice=True,  # nice는 y축 값의 범위가 자연스럽게 조정되도록 함
                            clamp=True,
                            zero=True),  # y축이 0부터 시작하도록 설정
            axis=alt.Axis(tickCount=4)),  # y축 눈금 개수를 설정 (예: 4개)
    color='User:N',  # 유저별로 색깔을 다르게 설정
    tooltip=['User:N', 'sum(인증 횟수):Q']
    ).properties(
    title=f'{start_date}부터 {end_date}까지의 사용자별 인증 횟수'
    ).configure_mark(
    opacity=0.7
    )

    # Altair 차트 표시
    st.altair_chart(chart, use_container_width=True)

    # 사용자별 미션과 메시지 추출
    df_filtered['미션'] = df_filtered['Message'].str.extract(r'(#\S+)')[0]

    # '#인증'을 메시지에서 제거
    df_filtered['Message'] = df_filtered['Message'].str.replace('#인증', '', regex=False)

    # 사용자별 메시지 내용을 합치기
    df_mission = df_filtered[['User', '미션', 'Message']]

    # 사용자별 미션 현황과 메시지 합침
    df_mission_combined = df_mission.groupby(['User', '미션'])['Message'].apply(' '.join).reset_index()

    # 사용자 닉네임 순으로 정렬
    df_mission_combined = df_mission_combined.sort_values(by=['User', '미션']).reset_index(drop=True)

    # 테이블 순서를 1부터 시작하도록 인덱스 재설정
    df_mission_combined.index = df_mission_combined.index + 1

    # 사용자별 미션 현황 및 메시지 표시
    st.write(f'{start_date}부터 {end_date}까지의 사용자별 미션 현황 (닉네임 순, 메시지 합침):')
    st.write(df_mission_combined)
    
else:
    st.write('업로드된 파일이 없습니다.')
