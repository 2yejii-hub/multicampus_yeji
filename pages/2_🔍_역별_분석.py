# -*- coding: utf-8 -*-
"""
서울 지하철 혼잡도 대시보드 - 역별 상세 분석 페이지 (Phase 3)
"""

import streamlit as st
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.data_loader import load_processed_data
from utils.data_processor import (
    get_line_list,
    get_station_list,
    get_station_stats,
    get_station_direction_comparison,
    get_station_day_comparison,
    get_station_heatmap_data,
    generate_station_insights,
)
from utils.visualization import (
    create_direction_comparison_chart,
    create_direction_bar_chart,
    create_comparison_chart,
    create_station_heatmap,
)


# 페이지 설정
st.set_page_config(
    page_title="역별 분석 - 서울 지하철 혼잡도",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)


def render_sidebar(df):
    """사이드바 필터 렌더링"""
    with st.sidebar:
        st.header("🔍 역 선택")
        
        # 호선 선택
        all_lines = get_line_list(df)
        selected_line = st.selectbox(
            "호선 선택",
            all_lines,
            index=0,
            help="분석할 호선을 선택하세요"
        )
        
        # 선택된 호선의 역 목록
        stations = get_station_list(df, selected_line)
        selected_station = st.selectbox(
            "역 선택",
            stations,
            index=0,
            help="분석할 역을 선택하세요"
        )
        
        st.divider()
        
        # 분석 옵션
        st.subheader("📊 분석 옵션")
        
        # 방향 선택
        direction_option = st.radio(
            "방향",
            ["전체", "상행", "하행", "내선", "외선"],
            horizontal=True,
            help="분석할 방향을 선택하세요"
        )
        
        # 요일 선택
        day_option = st.radio(
            "요일",
            ["전체", "평일", "토요일", "일요일"],
            horizontal=True,
            help="분석할 요일을 선택하세요"
        )
        
        st.divider()
        
        # 히트맵 기준 선택
        st.subheader("🗺️ 히트맵 설정")
        heatmap_pivot = st.radio(
            "히트맵 Y축",
            ["방향", "요일구분"],
            horizontal=True
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
        st.caption("Phase 3 - 역별 분석 ✅")
        
    return selected_line, selected_station, direction_option, day_option, heatmap_pivot


def render_metrics(stats, station, line):
    """메트릭 카드 렌더링"""
    st.subheader(f"📊 {line} {station}역 핵심 지표")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        avg_congestion = stats['평균_혼잡도']
        # 혼잡도 레벨에 따른 이모지
        if avg_congestion < 50:
            emoji = "🟢"
        elif avg_congestion < 70:
            emoji = "🟡"
        else:
            emoji = "🔴"
        
        st.metric(
            label=f"{emoji} 평균 혼잡도",
            value=f"{avg_congestion:.1f}%",
            help="선택된 조건의 평균 혼잡도"
        )
    
    with col2:
        st.metric(
            label="⏰ 피크 시간대",
            value=stats['피크_시간'],
            delta=f"{stats['피크_혼잡도']:.1f}%",
            delta_color="inverse",
            help="가장 혼잡한 시간대"
        )
    
    with col3:
        st.metric(
            label="😊 여유 시간대",
            value=stats['여유_시간'],
            delta=f"{stats['여유_혼잡도']:.1f}%",
            delta_color="off",
            help="가장 여유로운 시간대"
        )


def render_charts(df, station, line, heatmap_pivot):
    """차트 렌더링"""
    
    # 1. 방향별 시간대 혼잡도 비교
    st.subheader("🚇 방향별 시간대 혼잡도")
    direction_data = get_station_direction_comparison(df, station, line)
    
    if not direction_data.empty:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            fig_direction_line = create_direction_comparison_chart(
                direction_data,
                x='시간대',
                y='혼잡도',
                direction_col='방향',
                title="",
                height=350
            )
            st.plotly_chart(fig_direction_line, use_container_width=True)
        
        with col2:
            fig_direction_bar = create_direction_bar_chart(
                direction_data,
                direction_col='방향',
                value_col='혼잡도',
                title="방향별 평균",
                height=350
            )
            st.plotly_chart(fig_direction_bar, use_container_width=True)
    else:
        st.warning("방향별 데이터가 없습니다.")
    
    st.divider()
    
    # 2. 요일별 혼잡도 비교
    st.subheader("📅 요일별 혼잡도 비교")
    day_data = get_station_day_comparison(df, station, line)
    
    if not day_data.empty:
        fig_day = create_comparison_chart(
            day_data,
            x='시간대',
            y='혼잡도',
            group='요일구분',
            title="",
            height=350
        )
        st.plotly_chart(fig_day, use_container_width=True)
    else:
        st.warning("요일별 데이터가 없습니다.")
    
    st.divider()
    
    # 3. 히트맵
    st.subheader(f"🗺️ 시간대별 혼잡도 히트맵 ({heatmap_pivot} 기준)")
    heatmap_data = get_station_heatmap_data(df, station, line, pivot_by=heatmap_pivot)
    
    if not heatmap_data.empty:
        y_label = "방향" if heatmap_pivot == "방향" else "요일"
        fig_heatmap = create_station_heatmap(
            heatmap_data,
            title="",
            height=250,
            x_label="시간대",
            y_label=y_label
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)
    else:
        st.warning("히트맵 데이터가 없습니다.")


def render_insights(df, station, line):
    """인사이트 렌더링"""
    st.subheader("💡 자동 분석 인사이트")
    
    insights = generate_station_insights(df, station, line)
    
    insight_text = "\n\n".join([f"- {insight}" for insight in insights])
    st.info(insight_text)


def main():
    """메인 페이지"""
    
    # 타이틀
    st.title("🔍 역별 상세 분석")
    st.markdown("특정 역의 시간대별 혼잡도를 상세히 분석합니다.")
    
    st.divider()
    
    # 데이터 로드
    try:
        with st.spinner('데이터를 불러오는 중...'):
            df = load_processed_data()
        
        # 사이드바 필터
        selected_line, selected_station, direction_option, day_option, heatmap_pivot = render_sidebar(df)
        
        # 데이터 필터링 (선택된 역 데이터)
        df_filtered = df[(df['역명'] == selected_station) & (df['호선'] == selected_line)].copy()
        
        # 방향 필터 적용
        if direction_option != "전체":
            df_filtered = df_filtered[df_filtered['방향'] == direction_option]
        
        # 요일 필터 적용
        if day_option != "전체":
            df_filtered = df_filtered[df_filtered['요일구분'] == day_option]
        
        # 필터링된 데이터 확인
        if df_filtered.empty:
            st.warning("⚠️ 선택된 조건에 해당하는 데이터가 없습니다. 필터를 조정해주세요.")
            return
        
        # 필터 정보 표시
        filter_info = f"📋 **분석 대상**: {selected_line} {selected_station}역"
        if direction_option != "전체":
            filter_info += f" | {direction_option}"
        if day_option != "전체":
            filter_info += f" | {day_option}"
        filter_info += f" | 데이터 {len(df_filtered):,}건"
        st.info(filter_info)
        
        # 통계 계산
        stats = get_station_stats(df, selected_station, selected_line)
        
        # 메트릭 카드
        render_metrics(stats, selected_station, selected_line)
        
        st.divider()
        
        # 차트 영역
        render_charts(df, selected_station, selected_line, heatmap_pivot)
        
        st.divider()
        
        # 인사이트
        render_insights(df, selected_station, selected_line)
        
        st.divider()
        
        # 원본 데이터 미리보기
        with st.expander("📋 원본 데이터 미리보기"):
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

