# -*- coding: utf-8 -*-
"""
Phase 4: 시간대별 혼잡도 분석 페이지
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# 프로젝트 루트 디렉토리 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.data_loader import load_processed_data
from utils.data_processor import (
    get_time_slots,
    get_congestion_by_specific_time,
    get_top_stations_by_time,
    compare_time_slots,
    get_peak_hours_pattern,
    get_congestion_by_time,
    get_time_range_congestion,
    filter_data
)
from utils.visualization import (
    create_time_slot_bar_chart,
    create_time_comparison_chart,
    create_peak_pattern_chart,
    create_time_series_chart,
)


# 페이지 설정
st.set_page_config(
    page_title="시간대별 분석 - 서울 지하철 혼잡도",
    page_icon="📈",
    layout="wide"
)

st.title("📈 시간대별 혼잡도 분석")
st.markdown("특정 시간대의 전체 노선 혼잡도를 분석하고 비교해보세요.")

# 데이터 로드
try:
    with st.spinner('데이터를 불러오는 중...'):
        df = load_processed_data()
    
    if df.empty:
        st.error("데이터가 비어있습니다.")
        st.stop()
        
except Exception as e:
    st.error(f"데이터 로딩 중 오류가 발생했습니다: {str(e)}")
    st.info("데이터 파일을 확인하거나 관리자에게 문의하세요.")
    st.stop()


# ============================================================
# 사이드바 - 필터 설정
# ============================================================

with st.sidebar:
    st.header("🔍 필터 설정")
    
    # 요일 선택
    day_type = st.radio(
        "요일 구분",
        ["평일", "토요일", "일요일", "전체"],
        index=0,
        help="분석할 요일을 선택하세요"
    )
    
    st.divider()
    
    # 분석 모드 선택
    analysis_mode = st.radio(
        "분석 모드",
        ["단일 시간대 분석", "시간대 비교", "출퇴근 패턴 분석"],
        index=0
    )
    
    st.divider()
    
    # 시간대 목록 가져오기
    time_slots = get_time_slots(df)
    
    # 기본값 인덱스 찾기
    default_time_idx = time_slots.index("08:00") if "08:00" in time_slots else len(time_slots) // 3
    
    if analysis_mode == "단일 시간대 분석":
        # 단일 시간대 선택
        selected_time = st.select_slider(
            "시간대 선택",
            options=time_slots,
            value=time_slots[default_time_idx],
            help="분석할 시간대를 선택하세요"
        )
        
        # 표시할 역 개수
        top_n = st.slider(
            "표시할 역 개수",
            min_value=10,
            max_value=30,
            value=20,
            step=5,
            help="상위 N개 역을 표시합니다"
        )
        
    elif analysis_mode == "시간대 비교":
        # 두 시간대 선택
        col1, col2 = st.columns(2)
        
        with col1:
            time1_idx = time_slots.index("08:00") if "08:00" in time_slots else len(time_slots) // 3
            time_slot1 = st.selectbox(
                "첫 번째 시간대",
                time_slots,
                index=time1_idx,
                help="비교할 첫 번째 시간대"
            )
        
        with col2:
            time2_idx = time_slots.index("18:00") if "18:00" in time_slots else len(time_slots) * 2 // 3
            time_slot2 = st.selectbox(
                "두 번째 시간대",
                time_slots,
                index=time2_idx,
                help="비교할 두 번째 시간대"
            )
        
        # 표시할 역 개수
        top_n = st.slider(
            "표시할 역 개수",
            min_value=10,
            max_value=20,
            value=15,
            step=5,
            help="상위 N개 역을 비교합니다"
        )
    
    else:  # 출퇴근 패턴 분석
        st.info("평일 기준 출퇴근 시간대 패턴을 분석합니다.")


# ============================================================
# 메인 콘텐츠
# ============================================================

if analysis_mode == "단일 시간대 분석":
    st.header(f"🕐 {selected_time} 시간대 분석")
    
    # 해당 시간대 데이터 가져오기
    time_data = get_congestion_by_specific_time(df, selected_time, day_type)
    
    if time_data.empty:
        st.warning(f"선택한 조건({day_type}, {selected_time})에 해당하는 데이터가 없습니다.")
        st.stop()
    
    # 메트릭 카드
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_congestion = time_data['혼잡도'].mean()
        st.metric(
            label="평균 혼잡도",
            value=f"{avg_congestion:.1f}%",
            help=f"{selected_time} 시간대 전체 역의 평균 혼잡도"
        )
    
    with col2:
        max_congestion = time_data['혼잡도'].max()
        max_station = time_data.iloc[0]['역명']
        st.metric(
            label="최고 혼잡도",
            value=f"{max_congestion:.1f}%",
            delta=max_station,
            help=f"가장 혼잡한 역: {max_station}"
        )
    
    with col3:
        min_congestion = time_data['혼잡도'].min()
        st.metric(
            label="최저 혼잡도",
            value=f"{min_congestion:.1f}%",
            help="가장 여유로운 역의 혼잡도"
        )
    
    with col4:
        congested_count = len(time_data[time_data['혼잡도'] >= 70])
        st.metric(
            label="혼잡한 역 수",
            value=f"{congested_count}개",
            help="혼잡도 70% 이상인 역의 개수"
        )
    
    st.divider()
    
    # 차트 섹션
    tab1, tab2, tab3 = st.tabs(["📊 혼잡한 역 TOP", "🟢 여유로운 역 TOP", "📈 전체 시간대 추이"])
    
    with tab1:
        st.subheader(f"🔴 가장 혼잡한 역 TOP {top_n}")
        
        # 막대 차트
        top_congested = time_data.head(top_n)
        fig = create_time_slot_bar_chart(
            top_congested,
            title=f"{selected_time} - 혼잡한 역 TOP {top_n}",
            top_n=top_n,
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # 테이블
        with st.expander("📋 상세 데이터 보기"):
            display_df = top_congested[['역명', '호선', '혼잡도']].copy()
            display_df.insert(0, '순위', range(1, len(display_df) + 1))
            display_df['혼잡도'] = display_df['혼잡도'].round(1).astype(str) + '%'
            st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    with tab2:
        st.subheader(f"🟢 가장 여유로운 역 TOP {top_n}")
        
        # 막대 차트 (오름차순)
        top_relaxed = time_data.sort_values('혼잡도', ascending=True).head(top_n)
        fig = create_time_slot_bar_chart(
            top_relaxed,
            title=f"{selected_time} - 여유로운 역 TOP {top_n}",
            top_n=top_n,
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # 테이블
        with st.expander("📋 상세 데이터 보기"):
            display_df = top_relaxed[['역명', '호선', '혼잡도']].copy()
            display_df.insert(0, '순위', range(1, len(display_df) + 1))
            display_df['혼잡도'] = display_df['혼잡도'].round(1).astype(str) + '%'
            st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    with tab3:
        st.subheader("📈 전체 시간대 평균 혼잡도 추이")
        
        # 전체 시간대 평균 혼잡도 계산
        time_avg = get_congestion_by_time(
            filter_data(df, day_type=day_type)
        )
        
        if not time_avg.empty:
            fig = create_time_series_chart(
                time_avg,
                x='시간대',
                y='혼잡도',
                title=f"{day_type} 시간대별 평균 혼잡도",
                height=400
            )
            
            # 선택한 시간대 하이라이트 (시간대 리스트에서 인덱스 찾기)
            if selected_time in time_avg['시간대'].values:
                time_idx = time_avg[time_avg['시간대'] == selected_time].index[0]
                fig.add_vline(
                    x=time_idx,
                    line_width=3,
                    line_dash="dash",
                    line_color="red",
                    annotation_text=f"현재 선택: {selected_time}",
                    annotation_position="top"
                )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("시간대별 데이터가 없습니다.")
    
    # 인사이트
    st.divider()
    st.subheader("💡 인사이트")
    
    # 혼잡도 레벨 판단
    if avg_congestion < 50:
        level = "여유"
        emoji = "🟢"
        color = "green"
    elif avg_congestion < 70:
        level = "보통"
        emoji = "🟡"
        color = "orange"
    else:
        level = "혼잡"
        emoji = "🔴"
        color = "red"
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        insights = []
        insights.append(f"{emoji} **{selected_time}** 시간대는 전반적으로 **{level}**합니다 (평균 {avg_congestion:.1f}%)")
        
        if congested_count > 0:
            insights.append(f"🚨 혼잡도 70% 이상인 역이 **{congested_count}개**입니다")
        
        # 가장 혼잡한 호선
        line_avg = time_data.groupby('호선')['혼잡도'].mean().sort_values(ascending=False)
        if len(line_avg) > 0:
            most_congested_line = line_avg.index[0]
            most_congested_value = line_avg.iloc[0]
            insights.append(f"🚇 가장 혼잡한 호선: **{most_congested_line}** ({most_congested_value:.1f}%)")
        
        # 가장 여유로운 호선
        if len(line_avg) > 1:
            least_congested_line = line_avg.index[-1]
            least_congested_value = line_avg.iloc[-1]
            insights.append(f"😊 가장 여유로운 호선: **{least_congested_line}** ({least_congested_value:.1f}%)")
        
        for insight in insights:
            st.markdown(f"- {insight}")
    
    with col2:
        # 혼잡도 분포
        st.markdown("**혼잡도 분포**")
        relaxed_count = len(time_data[time_data['혼잡도'] < 50])
        normal_count = len(time_data[(time_data['혼잡도'] >= 50) & (time_data['혼잡도'] < 70)])
        congested_count = len(time_data[time_data['혼잡도'] >= 70])
        
        st.markdown(f"🟢 여유 (0-50%): **{relaxed_count}개**")
        st.markdown(f"🟡 보통 (50-70%): **{normal_count}개**")
        st.markdown(f"🔴 혼잡 (70%+): **{congested_count}개**")


elif analysis_mode == "시간대 비교":
    st.header(f"⚖️ 시간대 비교: {time_slot1} vs {time_slot2}")
    
    if time_slot1 == time_slot2:
        st.warning("⚠️ 동일한 시간대를 선택했습니다. 다른 시간대를 선택해주세요.")
        st.stop()
    
    # 비교 데이터 가져오기
    comparison_df = compare_time_slots(df, time_slot1, time_slot2, day_type, top_n)
    
    if comparison_df.empty:
        st.warning("비교할 데이터가 없습니다.")
        st.stop()
    
    # 메트릭 카드
    col1, col2, col3 = st.columns(3)
    
    time1_col = f'{time_slot1}_혼잡도'
    time2_col = f'{time_slot2}_혼잡도'
    
    avg1 = comparison_df[time1_col].mean()
    avg2 = comparison_df[time2_col].mean()
    diff = avg2 - avg1
    
    with col1:
        st.metric(
            label=f"{time_slot1} 평균",
            value=f"{avg1:.1f}%",
            help=f"{time_slot1} 시간대 평균 혼잡도"
        )
    
    with col2:
        st.metric(
            label=f"{time_slot2} 평균",
            value=f"{avg2:.1f}%",
            delta=f"{diff:+.1f}%p",
            help=f"{time_slot2} 시간대 평균 혼잡도 (vs {time_slot1})"
        )
    
    with col3:
        increase_count = len(comparison_df[comparison_df['차이'] > 0])
        st.metric(
            label="혼잡도 증가한 역",
            value=f"{increase_count}개",
            help=f"{time_slot1} → {time_slot2} 혼잡도가 증가한 역의 수"
        )
    
    st.divider()
    
    # 비교 차트
    st.subheader(f"📊 상위 {top_n}개 역 비교")
    
    fig = create_time_comparison_chart(
        comparison_df,
        time1_col=time1_col,
        time2_col=time2_col,
        time1_label=time_slot1,
        time2_label=time_slot2,
        title=f"시간대 비교: {time_slot1} vs {time_slot2}",
        top_n=top_n,
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # 상세 테이블
    st.subheader("📋 상세 비교 데이터")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # 정렬 옵션
        sort_option = st.radio(
            "정렬 기준",
            ["평균 혼잡도 높은 순", "차이 큰 순 (증가)", "차이 큰 순 (감소)"],
            horizontal=True
        )
    
    with col2:
        show_all = st.checkbox("전체 데이터 보기", value=False)
    
    # 정렬
    if sort_option == "평균 혼잡도 높은 순":
        comparison_df_sorted = comparison_df.sort_values('평균', ascending=False)
    elif sort_option == "차이 큰 순 (증가)":
        comparison_df_sorted = comparison_df.sort_values('차이', ascending=False)
    else:  # 차이 큰 순 (감소)
        comparison_df_sorted = comparison_df.sort_values('차이', ascending=True)
    
    # 표시할 데이터
    display_df = comparison_df_sorted if show_all else comparison_df_sorted.head(top_n)
    
    # 테이블 형식 정리
    table_df = display_df[['역명', '호선', time1_col, time2_col, '차이']].copy()
    table_df.insert(0, '순위', range(1, len(table_df) + 1))
    table_df.columns = ['순위', '역명', '호선', f'{time_slot1}', f'{time_slot2}', '차이']
    
    # 포맷팅
    for col in [f'{time_slot1}', f'{time_slot2}', '차이']:
        table_df[col] = table_df[col].round(1)
    
    st.dataframe(
        table_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            f'{time_slot1}': st.column_config.NumberColumn(
                f'{time_slot1}',
                help=f"{time_slot1} 시간대 혼잡도",
                format="%.1f%%"
            ),
            f'{time_slot2}': st.column_config.NumberColumn(
                f'{time_slot2}',
                help=f"{time_slot2} 시간대 혼잡도",
                format="%.1f%%"
            ),
            '차이': st.column_config.NumberColumn(
                '차이',
                help=f"{time_slot2} - {time_slot1}",
                format="%.1f%%p"
            )
        }
    )
    
    # 인사이트
    st.divider()
    st.subheader("💡 인사이트")
    
    insights = []
    
    if abs(diff) < 5:
        insights.append(f"📊 두 시간대의 평균 혼잡도 차이가 작습니다 ({abs(diff):.1f}%p)")
    elif diff > 0:
        insights.append(f"📈 **{time_slot2}**가 **{time_slot1}**보다 평균 **{diff:.1f}%p** 더 혼잡합니다")
    else:
        insights.append(f"📉 **{time_slot2}**가 **{time_slot1}**보다 평균 **{abs(diff):.1f}%p** 덜 혼잡합니다")
    
    # 가장 차이가 큰 역
    max_increase = comparison_df.loc[comparison_df['차이'].idxmax()]
    max_decrease = comparison_df.loc[comparison_df['차이'].idxmin()]
    
    if max_increase['차이'] > 10:
        insights.append(
            f"🔺 **{max_increase['역명']}({max_increase['호선']})**의 혼잡도가 "
            f"가장 크게 증가했습니다 (+{max_increase['차이']:.1f}%p)"
        )
    
    if max_decrease['차이'] < -10:
        insights.append(
            f"🔻 **{max_decrease['역명']}({max_decrease['호선']})**의 혼잡도가 "
            f"가장 크게 감소했습니다 ({max_decrease['차이']:.1f}%p)"
        )
    
    for insight in insights:
        st.markdown(f"- {insight}")


else:  # 출퇴근 패턴 분석
    st.header("🚆 출퇴근 시간대 패턴 분석")
    
    # 패턴 분석 (평일 기준)
    pattern_day = day_type if day_type != "전체" else "평일"
    peak_info = get_peak_hours_pattern(df, pattern_day)
    
    if not peak_info:
        st.warning(f"{pattern_day} 데이터가 없습니다.")
        st.stop()
    
    # 메트릭 카드
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🌅 오전 피크 (07:00-09:00)")
        if '오전_피크_시간' in peak_info:
            metric_col1, metric_col2 = st.columns(2)
            with metric_col1:
                st.metric(
                    "피크 시간",
                    peak_info['오전_피크_시간'],
                    help="오전 시간대 중 가장 혼잡한 시간"
                )
            with metric_col2:
                st.metric(
                    "피크 혼잡도",
                    f"{peak_info['오전_피크_혼잡도']:.1f}%",
                    help="오전 피크 시간의 혼잡도"
                )
            st.info(f"오전 평균 혼잡도: {peak_info['오전_평균_혼잡도']:.1f}%")
    
    with col2:
        st.markdown("### 🌆 오후 피크 (17:00-19:00)")
        if '오후_피크_시간' in peak_info:
            metric_col1, metric_col2 = st.columns(2)
            with metric_col1:
                st.metric(
                    "피크 시간",
                    peak_info['오후_피크_시간'],
                    help="오후 시간대 중 가장 혼잡한 시간"
                )
            with metric_col2:
                st.metric(
                    "피크 혼잡도",
                    f"{peak_info['오후_피크_혼잡도']:.1f}%",
                    help="오후 피크 시간의 혼잡도"
                )
            st.info(f"오후 평균 혼잡도: {peak_info['오후_평균_혼잡도']:.1f}%")
    
    st.divider()
    
    # 전체 시간대 패턴 차트
    st.subheader("📈 하루 전체 혼잡도 패턴")
    
    # 시간대별 평균 혼잡도
    time_pattern = get_congestion_by_time(
        filter_data(df, day_type=pattern_day)
    )
    
    if not time_pattern.empty:
        # 시간 인덱스 추가 (피크 구간 하이라이트용)
        time_pattern['시간_숫자'] = time_pattern['시간_정렬용'] / 60
        
        fig = create_peak_pattern_chart(
            time_pattern,
            x='시간_숫자',
            y='혼잡도',
            title=f"{pattern_day} 시간대별 혼잡도 패턴",
            morning_range=(7, 9),
            evening_range=(17, 19),
            height=450
        )
        
        # x축을 시간대 문자열로 변경
        fig.update_xaxes(
            tickvals=list(range(5, 25)),
            ticktext=[f"{h:02d}:00" for h in range(5, 25)],
            title="시간대"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # 오전/오후 피크 상세 분석
    st.divider()
    
    tab1, tab2 = st.tabs(["🌅 오전 피크 분석", "🌆 오후 피크 분석"])
    
    with tab1:
        st.subheader("오전 출근 시간대 (07:00-09:00)")
        
        # 오전 시간대 역별 혼잡도
        morning_data = get_time_range_congestion(df, "07:00", "09:00", pattern_day)
        
        if not morning_data.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**🔴 혼잡한 역 TOP 10**")
                top_morning = morning_data.head(10)
                for idx, row in top_morning.iterrows():
                    st.markdown(
                        f"{idx+1}. **{row['역명']}** ({row['호선']}) - {row['평균_혼잡도']:.1f}%"
                    )
            
            with col2:
                st.markdown("**🟢 여유로운 역 TOP 10**")
                bottom_morning = morning_data.tail(10).sort_values('평균_혼잡도')
                for idx, row in enumerate(bottom_morning.itertuples(), 1):
                    st.markdown(
                        f"{idx}. **{row.역명}** ({row.호선}) - {row.평균_혼잡도:.1f}%"
                    )
    
    with tab2:
        st.subheader("오후 퇴근 시간대 (17:00-19:00)")
        
        # 오후 시간대 역별 혼잡도
        evening_data = get_time_range_congestion(df, "17:00", "19:00", pattern_day)
        
        if not evening_data.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**🔴 혼잡한 역 TOP 10**")
                top_evening = evening_data.head(10)
                for idx, row in top_evening.iterrows():
                    st.markdown(
                        f"{idx+1}. **{row['역명']}** ({row['호선']}) - {row['평균_혼잡도']:.1f}%"
                    )
            
            with col2:
                st.markdown("**🟢 여유로운 역 TOP 10**")
                bottom_evening = evening_data.tail(10).sort_values('평균_혼잡도')
                for idx, row in enumerate(bottom_evening.itertuples(), 1):
                    st.markdown(
                        f"{idx}. **{row.역명}** ({row.호선}) - {row.평균_혼잡도:.1f}%"
                    )
    
    # 인사이트
    st.divider()
    st.subheader("💡 인사이트")
    
    insights = []
    
    if '오전_평균_혼잡도' in peak_info and '오후_평균_혼잡도' in peak_info:
        morning_avg = peak_info['오전_평균_혼잡도']
        evening_avg = peak_info['오후_평균_혼잡도']
        diff = evening_avg - morning_avg
        
        if abs(diff) < 5:
            insights.append("📊 오전과 오후의 평균 혼잡도가 비슷합니다")
        elif diff > 0:
            insights.append(f"📈 오후 퇴근 시간이 오전 출근 시간보다 평균 **{diff:.1f}%p** 더 혼잡합니다")
        else:
            insights.append(f"📉 오전 출근 시간이 오후 퇴근 시간보다 평균 **{abs(diff):.1f}%p** 더 혼잡합니다")
    
    if '오전_피크_시간' in peak_info:
        insights.append(f"🌅 오전 피크 시간은 **{peak_info['오전_피크_시간']}**입니다")
    
    if '오후_피크_시간' in peak_info:
        insights.append(f"🌆 오후 피크 시간은 **{peak_info['오후_피크_시간']}**입니다")
    
    insights.append("💡 출퇴근 시간을 피하면 더 쾌적하게 이동할 수 있습니다")
    
    for insight in insights:
        st.markdown(f"- {insight}")


# ============================================================
# 푸터
# ============================================================

st.divider()

with st.expander("📖 사용 가이드"):
    st.markdown("""
    ### 시간대별 분석 페이지 사용법
    
    #### 1. 단일 시간대 분석
    - 특정 시간대의 전체 역 혼잡도를 확인할 수 있습니다
    - 가장 혼잡한 역과 여유로운 역을 TOP N으로 확인하세요
    - 전체 시간대 추이에서 선택한 시간의 위치를 확인할 수 있습니다
    
    #### 2. 시간대 비교
    - 두 시간대의 혼잡도를 직접 비교할 수 있습니다
    - 어느 시간대가 더 혼잡한지, 어느 역의 변화가 큰지 확인하세요
    
    #### 3. 출퇴근 패턴 분석
    - 오전/오후 피크 시간대의 패턴을 분석합니다
    - 하루 전체의 혼잡도 추이를 한눈에 확인할 수 있습니다
    
    #### 혼잡도 기준
    - 🟢 **여유** (0-50%): 앉아서 이동 가능
    - 🟡 **보통** (50-70%): 서서 이동 가능
    - 🔴 **혼잡** (70-100%): 매우 혼잡, 승하차 어려움
    """)

st.caption("데이터 출처: 서울교통공사 지하철 혼잡도 정보 (2025년 9월 30일 기준)")

