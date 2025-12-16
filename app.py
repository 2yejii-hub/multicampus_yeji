# -*- coding: utf-8 -*-
"""
서울 지하철 혼잡도 대시보드 - 메인 페이지 (Phase 2)
"""

import streamlit as st
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.data_loader import load_processed_data
from utils.data_processor import (
    get_statistics,
    get_congestion_by_line,
    get_congestion_by_time,
    get_top_stations,
    get_congestion_by_day_time,
    get_peak_info,
    get_line_list,
    filter_data,
)
from utils.visualization import (
    create_line_bar_chart,
    create_time_series_chart,
    create_comparison_chart,
)


# 페이지 설정
st.set_page_config(
    page_title="서울 지하철 혼잡도 대시보드",
    page_icon="🚇",
    layout="wide",
    initial_sidebar_state="expanded"
)


def render_sidebar(df):
    """사이드바 필터 렌더링"""
    with st.sidebar:
        st.header("🔍 필터")
        
        # 요일 선택
        day_type = st.radio(
            "요일 선택",
            ["전체", "평일", "토요일", "일요일"],
            horizontal=True
        )
        
        st.divider()
        
        # 시간대 범위
        st.subheader("⏰ 시간대 범위")
        time_range = st.slider(
            "시간대 선택",
            min_value=5,
            max_value=24,
            value=(5, 24),
            format="%d시"
        )
        
        st.divider()
        
        # 호선 선택
        st.subheader("🚇 호선 선택")
        all_lines = get_line_list(df)
        
        # 전체 선택/해제 버튼
        col1, col2 = st.columns(2)
        with col1:
            if st.button("전체 선택", use_container_width=True):
                st.session_state.selected_lines = all_lines
        with col2:
            if st.button("전체 해제", use_container_width=True):
                st.session_state.selected_lines = []
        
        # 호선 멀티셀렉트
        if 'selected_lines' not in st.session_state:
            st.session_state.selected_lines = all_lines
        
        selected_lines = st.multiselect(
            "호선을 선택하세요",
            all_lines,
            default=st.session_state.selected_lines,
            label_visibility="collapsed"
        )
        
        st.divider()
        
        # 혼잡도 기준 안내
        with st.expander("📖 혼잡도 기준 안내"):
            st.markdown("""
            - 🟢 **여유** (0-50%): 앉아서 이동 가능
            - 🟡 **보통** (50-70%): 서서 이동 가능  
            - 🔴 **혼잡** (70-100%+): 매우 혼잡
            """)
        
        st.divider()
        st.caption("Phase 2 완료 ✅")
        
    return day_type, time_range, selected_lines


def render_metrics(stats, peak_info):
    """메트릭 카드 렌더링"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📊 전체 평균 혼잡도",
            value=f"{stats['평균_혼잡도']:.1f}%",
            help="선택된 조건의 평균 혼잡도"
        )
    
    with col2:
        st.metric(
            label="⏰ 피크 시간대",
            value=peak_info['피크_시간'],
            delta=f"{peak_info['피크_혼잡도']:.1f}%",
            delta_color="inverse",
            help="가장 혼잡한 시간대"
        )
    
    with col3:
        st.metric(
            label="🚉 분석 역 수",
            value=f"{stats['역_수']}개",
            help="분석 대상 지하철역 수"
        )
    
    with col4:
        st.metric(
            label="😊 여유 시간대",
            value=peak_info['여유_시간'],
            delta=f"{peak_info['여유_혼잡도']:.1f}%",
            delta_color="off",
            help="가장 여유로운 시간대"
        )


def render_charts(df_filtered):
    """차트 렌더링"""
    
    # 1. 호선별 평균 혼잡도 차트
    st.subheader("📊 호선별 평균 혼잡도")
    line_data = get_congestion_by_line(df_filtered)
    
    if not line_data.empty:
        fig_line = create_line_bar_chart(
            line_data,
            x='호선',
            y='평균_혼잡도',
            title="",
            color_by_value=True,
            height=350
        )
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.warning("선택된 조건에 해당하는 데이터가 없습니다.")
    
    st.divider()
    
    # 2. 시간대별 혼잡도 추이
    st.subheader("📈 시간대별 혼잡도 추이")
    time_data = get_congestion_by_time(df_filtered)
    
    if not time_data.empty:
        fig_time = create_time_series_chart(
            time_data,
            x='시간대',
            y='혼잡도',
            title="",
            height=350
        )
        st.plotly_chart(fig_time, use_container_width=True)
    else:
        st.warning("선택된 조건에 해당하는 데이터가 없습니다.")
    
    st.divider()
    
    # 3. 평일 vs 휴일 비교 차트
    st.subheader("📅 요일별 혼잡도 비교")
    day_time_data = get_congestion_by_day_time(df_filtered)
    
    if not day_time_data.empty:
        fig_comparison = create_comparison_chart(
            day_time_data,
            x='시간대',
            y='혼잡도',
            group='요일구분',
            title="",
            height=350
        )
        st.plotly_chart(fig_comparison, use_container_width=True)
    else:
        st.warning("선택된 조건에 해당하는 데이터가 없습니다.")


def render_top_tables(df_filtered):
    """TOP 10 테이블 렌더링"""
    st.subheader("🏆 혼잡도 TOP 10 역")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔴 가장 혼잡한 역")
        top_congested = get_top_stations(df_filtered, n=10, ascending=False)
        
        if not top_congested.empty:
            # 데이터 포맷팅
            display_df = top_congested.copy()
            display_df['평균_혼잡도'] = display_df['평균_혼잡도'].round(1).astype(str) + '%'
            display_df['최대_혼잡도'] = display_df['최대_혼잡도'].round(1).astype(str) + '%'
            
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                height=400
            )
        else:
            st.info("데이터가 없습니다.")
    
    with col2:
        st.markdown("#### 🟢 가장 여유로운 역")
        top_quiet = get_top_stations(df_filtered, n=10, ascending=True)
        
        if not top_quiet.empty:
            # 데이터 포맷팅
            display_df = top_quiet.copy()
            display_df['평균_혼잡도'] = display_df['평균_혼잡도'].round(1).astype(str) + '%'
            display_df['최대_혼잡도'] = display_df['최대_혼잡도'].round(1).astype(str) + '%'
            
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                height=400
            )
        else:
            st.info("데이터가 없습니다.")


def main():
    """메인 페이지"""
    
    # 타이틀
    st.title("🚇 서울 지하철 혼잡도 대시보드")
    st.markdown("서울 지하철의 시간대별, 호선별 혼잡도를 분석하고 최적의 이동 시간을 찾아보세요!")
    
    st.divider()
    
    # 데이터 로드
    try:
        with st.spinner('데이터를 불러오는 중...'):
            df = load_processed_data()
        
        # 사이드바 필터
        day_type, time_range, selected_lines = render_sidebar(df)
        
        # 데이터 필터링
        df_filtered = filter_data(
            df,
            day_type=day_type,
            lines=selected_lines if selected_lines else None,
            time_range=time_range
        )
        
        # 필터링된 데이터 확인
        if df_filtered.empty:
            st.warning("⚠️ 선택된 조건에 해당하는 데이터가 없습니다. 필터를 조정해주세요.")
            return
        
        # 통계 계산
        stats = get_statistics(df_filtered)
        peak_info = get_peak_info(df_filtered)
        
        # 필터 정보 표시
        filter_info = f"📋 **현재 필터**: {day_type}"
        if selected_lines and len(selected_lines) < 8:
            filter_info += f" | {', '.join(selected_lines)}"
        filter_info += f" | {time_range[0]}시~{time_range[1]}시"
        filter_info += f" | 데이터 {len(df_filtered):,}건"
        st.info(filter_info)
        
        # 메트릭 카드
        render_metrics(stats, peak_info)
        
        st.divider()
        
        # 차트 영역
        render_charts(df_filtered)
        
        st.divider()
        
        # TOP 10 테이블
        render_top_tables(df_filtered)
        
        st.divider()
        
        # 데이터 미리보기 (접을 수 있는 섹션)
        with st.expander("📋 데이터 미리보기"):
            st.dataframe(df_filtered.head(100), use_container_width=True)
            st.caption(f"전체 {len(df_filtered):,}건 중 상위 100건 표시")
        
    except FileNotFoundError:
        st.error("""
        ❌ 전처리된 데이터 파일을 찾을 수 없습니다.
        
        먼저 데이터 전처리를 실행해주세요:
        ```bash
        python preprocess.py
        ```
        """)
    except Exception as e:
        st.error(f"❌ 오류가 발생했습니다: {str(e)}")
        st.info("페이지를 새로고침하거나 관리자에게 문의하세요.")
        
        # 디버그 정보 (개발 중에만)
        with st.expander("🔧 디버그 정보"):
            import traceback
            st.code(traceback.format_exc())


if __name__ == "__main__":
    main()
