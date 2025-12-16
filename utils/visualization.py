# -*- coding: utf-8 -*-
"""
시각화 모듈 - Plotly 기반 차트 생성 함수
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import List, Optional


# 혼잡도 색상 스케일 (초록 -> 노랑 -> 빨강)
CONGESTION_COLORS = {
    '여유': '#2ecc71',  # 초록
    '보통': '#f39c12',  # 노랑/주황
    '혼잡': '#e74c3c',  # 빨강
}

# 호선별 색상
LINE_COLORS = {
    '1호선': '#0052A4',
    '2호선': '#00A84D',
    '3호선': '#EF7C1C',
    '4호선': '#00A5DE',
    '5호선': '#996CAC',
    '6호선': '#CD7C2F',
    '7호선': '#747F00',
    '8호선': '#E6186C',
}


def get_congestion_color(value: float) -> str:
    """혼잡도 값에 따른 색상 반환"""
    if value < 50:
        return CONGESTION_COLORS['여유']
    elif value < 70:
        return CONGESTION_COLORS['보통']
    else:
        return CONGESTION_COLORS['혼잡']


def create_line_bar_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str = "",
    color_by_value: bool = True,
    height: int = 400
) -> go.Figure:
    """
    호선별 평균 혼잡도 막대 차트 생성
    
    Args:
        df: 데이터프레임
        x: x축 컬럼명
        y: y축 컬럼명 (혼잡도)
        title: 차트 제목
        color_by_value: 값에 따라 색상 변경 여부
        height: 차트 높이
        
    Returns:
        go.Figure: Plotly Figure 객체
    """
    if color_by_value:
        colors = [get_congestion_color(val) for val in df[y]]
    else:
        colors = [LINE_COLORS.get(line, '#3498db') for line in df[x]]
    
    fig = go.Figure(data=[
        go.Bar(
            x=df[x],
            y=df[y],
            marker_color=colors,
            text=df[y].round(1),
            texttemplate='%{text}%',
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>혼잡도: %{y:.1f}%<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=18)),
        xaxis_title=None,
        yaxis_title="혼잡도 (%)",
        height=height,
        template='plotly_white',
        showlegend=False,
        margin=dict(t=50, b=50, l=50, r=30),
        yaxis=dict(range=[0, max(df[y].max() * 1.15, 100)])
    )
    
    return fig


def create_time_series_chart(
    df: pd.DataFrame,
    x: str = '시간대',
    y: str = '혼잡도',
    color: Optional[str] = None,
    title: str = "",
    height: int = 400
) -> go.Figure:
    """
    시간대별 혼잡도 선 차트 생성
    
    Args:
        df: 데이터프레임
        x: x축 컬럼명 (시간대)
        y: y축 컬럼명 (혼잡도)
        color: 색상 구분 컬럼 (예: 호선, 방향)
        title: 차트 제목
        height: 차트 높이
        
    Returns:
        go.Figure: Plotly Figure 객체
    """
    if color:
        fig = px.line(
            df, x=x, y=y, color=color,
            title=title,
            color_discrete_map=LINE_COLORS,
            markers=True
        )
    else:
        fig = px.line(
            df, x=x, y=y,
            title=title,
            markers=True
        )
        fig.update_traces(line_color='#3498db', marker_color='#3498db')
    
    fig.update_layout(
        xaxis_title="시간대",
        yaxis_title="혼잡도 (%)",
        height=height,
        template='plotly_white',
        hovermode='x unified',
        margin=dict(t=50, b=50, l=50, r=30),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # x축 라벨 회전
    fig.update_xaxes(tickangle=-45)
    
    return fig


def create_comparison_chart(
    df: pd.DataFrame,
    x: str = '시간대',
    y: str = '혼잡도',
    group: str = '요일구분',
    title: str = "평일 vs 휴일 혼잡도 비교",
    height: int = 400
) -> go.Figure:
    """
    평일/휴일 비교 이중 선 차트 생성
    
    Args:
        df: 데이터프레임
        x: x축 컬럼명
        y: y축 컬럼명
        group: 그룹 컬럼명
        title: 차트 제목
        height: 차트 높이
        
    Returns:
        go.Figure: Plotly Figure 객체
    """
    # 그룹별 색상
    day_colors = {
        '평일': '#3498db',
        '토요일': '#9b59b6',
        '일요일': '#e74c3c',
        '휴일': '#e74c3c',
    }
    
    fig = px.line(
        df, x=x, y=y, color=group,
        title=title,
        color_discrete_map=day_colors,
        markers=True
    )
    
    fig.update_layout(
        xaxis_title="시간대",
        yaxis_title="혼잡도 (%)",
        height=height,
        template='plotly_white',
        hovermode='x unified',
        margin=dict(t=50, b=50, l=50, r=30),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            title=None
        )
    )
    
    fig.update_xaxes(tickangle=-45)
    
    return fig


def create_heatmap(
    df: pd.DataFrame,
    x: str,
    y: str,
    z: str,
    title: str = "",
    height: int = 500
) -> go.Figure:
    """
    히트맵 차트 생성
    
    Args:
        df: 피벗된 데이터프레임
        x: x축 컬럼명 (시간대)
        y: y축 컬럼명 (역명 또는 호선)
        z: 값 컬럼명 (혼잡도)
        title: 차트 제목
        height: 차트 높이
        
    Returns:
        go.Figure: Plotly Figure 객체
    """
    fig = px.imshow(
        df,
        labels=dict(x=x, y=y, color="혼잡도"),
        color_continuous_scale="RdYlGn_r",  # 빨강(혼잡) -> 노랑 -> 초록(여유)
        aspect="auto",
        title=title
    )
    
    fig.update_layout(
        height=height,
        template='plotly_white',
        margin=dict(t=50, b=50, l=100, r=30),
    )
    
    return fig


def create_gauge_chart(
    value: float,
    title: str = "현재 혼잡도",
    max_value: float = 100
) -> go.Figure:
    """
    게이지 차트 생성
    
    Args:
        value: 현재 값
        title: 차트 제목
        max_value: 최대 값
        
    Returns:
        go.Figure: Plotly Figure 객체
    """
    # 색상 결정
    if value < 50:
        bar_color = CONGESTION_COLORS['여유']
    elif value < 70:
        bar_color = CONGESTION_COLORS['보통']
    else:
        bar_color = CONGESTION_COLORS['혼잡']
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title},
        number={'suffix': '%'},
        gauge={
            'axis': {'range': [0, max_value]},
            'bar': {'color': bar_color},
            'steps': [
                {'range': [0, 50], 'color': '#e8f8f5'},
                {'range': [50, 70], 'color': '#fef9e7'},
                {'range': [70, 100], 'color': '#fdedec'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 70
            }
        }
    ))
    
    fig.update_layout(
        height=250,
        margin=dict(t=50, b=20, l=20, r=20)
    )
    
    return fig


def style_dataframe(df: pd.DataFrame, congestion_col: str = '혼잡도'):
    """
    데이터프레임에 혼잡도 기반 스타일 적용
    
    Args:
        df: 데이터프레임
        congestion_col: 혼잡도 컬럼명
        
    Returns:
        Styler: 스타일이 적용된 데이터프레임
    """
    def color_congestion(val):
        if val < 50:
            return f'background-color: {CONGESTION_COLORS["여유"]}; color: white'
        elif val < 70:
            return f'background-color: {CONGESTION_COLORS["보통"]}; color: white'
        else:
            return f'background-color: {CONGESTION_COLORS["혼잡"]}; color: white'
    
    if congestion_col in df.columns:
        return df.style.applymap(color_congestion, subset=[congestion_col])
    return df.style


# ============================================================
# Phase 3: 역별 분석 차트 함수
# ============================================================

# 방향별 색상
DIRECTION_COLORS = {
    '상행': '#3498db',
    '하행': '#e74c3c',
    '내선': '#9b59b6',
    '외선': '#2ecc71',
}


def create_direction_comparison_chart(
    df: pd.DataFrame,
    x: str = '시간대',
    y: str = '혼잡도',
    direction_col: str = '방향',
    title: str = "방향별 시간대 혼잡도 비교",
    height: int = 400
) -> go.Figure:
    """
    상행/하행 방향별 비교 선 차트 생성
    
    Args:
        df: 데이터프레임 (방향, 시간대, 혼잡도 컬럼 필요)
        x: x축 컬럼명
        y: y축 컬럼명
        direction_col: 방향 컬럼명
        title: 차트 제목
        height: 차트 높이
        
    Returns:
        go.Figure: Plotly Figure 객체
    """
    fig = px.line(
        df, x=x, y=y, color=direction_col,
        title=title,
        color_discrete_map=DIRECTION_COLORS,
        markers=True
    )
    
    fig.update_layout(
        xaxis_title="시간대",
        yaxis_title="혼잡도 (%)",
        height=height,
        template='plotly_white',
        hovermode='x unified',
        margin=dict(t=50, b=50, l=50, r=30),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            title=None
        )
    )
    
    fig.update_xaxes(tickangle=-45)
    
    return fig


def create_direction_bar_chart(
    df: pd.DataFrame,
    direction_col: str = '방향',
    value_col: str = '혼잡도',
    title: str = "방향별 평균 혼잡도",
    height: int = 300
) -> go.Figure:
    """
    방향별 평균 혼잡도 막대 차트 생성
    
    Args:
        df: 데이터프레임
        direction_col: 방향 컬럼명
        value_col: 값 컬럼명
        title: 차트 제목
        height: 차트 높이
        
    Returns:
        go.Figure: Plotly Figure 객체
    """
    # 방향별 평균 계산
    direction_avg = df.groupby(direction_col)[value_col].mean().reset_index()
    direction_avg.columns = ['방향', '평균_혼잡도']
    
    # 색상 설정
    colors = [DIRECTION_COLORS.get(d, '#3498db') for d in direction_avg['방향']]
    
    fig = go.Figure(data=[
        go.Bar(
            x=direction_avg['방향'],
            y=direction_avg['평균_혼잡도'],
            marker_color=colors,
            text=direction_avg['평균_혼잡도'].round(1),
            texttemplate='%{text}%',
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>평균 혼잡도: %{y:.1f}%<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=16)),
        xaxis_title=None,
        yaxis_title="혼잡도 (%)",
        height=height,
        template='plotly_white',
        showlegend=False,
        margin=dict(t=50, b=50, l=50, r=30),
        yaxis=dict(range=[0, max(direction_avg['평균_혼잡도'].max() * 1.2, 100)])
    )
    
    return fig


def create_station_heatmap(
    pivot_df: pd.DataFrame,
    title: str = "시간대별 혼잡도 히트맵",
    height: int = 300,
    x_label: str = "시간대",
    y_label: str = "구분"
) -> go.Figure:
    """
    역별 시간대 x 요일/방향 히트맵 생성
    
    Args:
        pivot_df: 피벗된 데이터프레임 (인덱스: 요일/방향, 컬럼: 시간대)
        title: 차트 제목
        height: 차트 높이
        x_label: x축 레이블
        y_label: y축 레이블
        
    Returns:
        go.Figure: Plotly Figure 객체
    """
    fig = px.imshow(
        pivot_df,
        labels=dict(x=x_label, y=y_label, color="혼잡도 (%)"),
        color_continuous_scale="RdYlGn_r",  # 빨강(혼잡) -> 노랑 -> 초록(여유)
        aspect="auto",
        title=title
    )
    
    fig.update_layout(
        height=height,
        template='plotly_white',
        margin=dict(t=60, b=50, l=100, r=30),
        coloraxis_colorbar=dict(
            title="혼잡도 (%)",
            ticksuffix="%"
        )
    )
    
    # x축 라벨 회전
    fig.update_xaxes(tickangle=-45)
    
    return fig


# ============================================================
# Phase 4: 시간대별 분석 차트 함수
# ============================================================

def create_time_slot_bar_chart(
    df: pd.DataFrame,
    x: str = '역명',
    y: str = '혼잡도',
    title: str = "시간대별 역 혼잡도",
    top_n: int = 20,
    height: int = 600
) -> go.Figure:
    """
    특정 시간대의 역별 혼잡도 막대 차트 생성 (상위 N개)
    
    Args:
        df: 데이터프레임
        x: x축 컬럼명 (역명)
        y: y축 컬럼명 (혼잡도)
        title: 차트 제목
        top_n: 표시할 역 개수
        height: 차트 높이
        
    Returns:
        go.Figure: Plotly Figure 객체
    """
    # 상위 N개만 선택
    df_plot = df.head(top_n).copy()
    
    # 호선별 색상 적용
    colors = [LINE_COLORS.get(line, '#3498db') for line in df_plot['호선']]
    
    # 역명 + 호선 라벨 생성
    df_plot['역_라벨'] = df_plot['역명'] + '\n(' + df_plot['호선'] + ')'
    
    fig = go.Figure(data=[
        go.Bar(
            x=df_plot['역_라벨'],
            y=df_plot[y],
            marker_color=colors,
            text=df_plot[y].round(1),
            texttemplate='%{text}%',
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>혼잡도: %{y:.1f}%<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=18)),
        xaxis_title=None,
        yaxis_title="혼잡도 (%)",
        height=height,
        template='plotly_white',
        showlegend=False,
        margin=dict(t=60, b=120, l=50, r=30),
        yaxis=dict(range=[0, max(df_plot[y].max() * 1.1, 100)])
    )
    
    # x축 라벨 회전
    fig.update_xaxes(tickangle=-45)
    
    return fig


def create_time_comparison_chart(
    df: pd.DataFrame,
    time1_col: str,
    time2_col: str,
    time1_label: str,
    time2_label: str,
    title: str = "시간대 비교",
    top_n: int = 15,
    height: int = 500
) -> go.Figure:
    """
    두 시간대 비교 그룹 막대 차트 생성
    
    Args:
        df: 비교 데이터프레임
        time1_col: 첫 번째 시간대 컬럼명
        time2_col: 두 번째 시간대 컬럼명
        time1_label: 첫 번째 시간대 라벨
        time2_label: 두 번째 시간대 라벨
        title: 차트 제목
        top_n: 표시할 역 개수
        height: 차트 높이
        
    Returns:
        go.Figure: Plotly Figure 객체
    """
    # 상위 N개만 선택
    df_plot = df.head(top_n).copy()
    
    # 역명 + 호선 라벨
    df_plot['역_라벨'] = df_plot['역명'] + '\n(' + df_plot['호선'] + ')'
    
    fig = go.Figure(data=[
        go.Bar(
            name=time1_label,
            x=df_plot['역_라벨'],
            y=df_plot[time1_col],
            marker_color='#3498db',
            text=df_plot[time1_col].round(1),
            texttemplate='%{text}%',
            textposition='outside',
        ),
        go.Bar(
            name=time2_label,
            x=df_plot['역_라벨'],
            y=df_plot[time2_col],
            marker_color='#e74c3c',
            text=df_plot[time2_col].round(1),
            texttemplate='%{text}%',
            textposition='outside',
        )
    ])
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=18)),
        xaxis_title=None,
        yaxis_title="혼잡도 (%)",
        barmode='group',
        height=height,
        template='plotly_white',
        margin=dict(t=80, b=120, l=50, r=30),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # x축 라벨 회전
    fig.update_xaxes(tickangle=-45)
    
    return fig


def create_peak_pattern_chart(
    df: pd.DataFrame,
    x: str = '시간대',
    y: str = '혼잡도',
    title: str = "출퇴근 시간대 혼잡도 패턴",
    morning_range: tuple = (7, 9),
    evening_range: tuple = (17, 19),
    height: int = 400
) -> go.Figure:
    """
    출퇴근 시간대 패턴 선 차트 생성 (피크 구간 하이라이트)
    
    Args:
        df: 시간대별 혼잡도 데이터프레임
        x: x축 컬럼명
        y: y축 컬럼명
        title: 차트 제목
        morning_range: 오전 피크 시간 범위 (시작시, 종료시)
        evening_range: 오후 피크 시간 범위 (시작시, 종료시)
        height: 차트 높이
        
    Returns:
        go.Figure: Plotly Figure 객체
    """
    fig = px.line(
        df, x=x, y=y,
        title=title,
        markers=True
    )
    
    # 선 색상 변경
    fig.update_traces(
        line_color='#3498db',
        marker_color='#3498db',
        line_width=3
    )
    
    # 오전 피크 영역 하이라이트
    if morning_range:
        morning_start, morning_end = morning_range
        fig.add_vrect(
            x0=morning_start - 0.5,
            x1=morning_end + 0.5,
            fillcolor="red",
            opacity=0.1,
            layer="below",
            line_width=0,
            annotation_text="오전 피크",
            annotation_position="top left"
        )
    
    # 오후 피크 영역 하이라이트
    if evening_range:
        evening_start, evening_end = evening_range
        fig.add_vrect(
            x0=evening_start - 0.5,
            x1=evening_end + 0.5,
            fillcolor="orange",
            opacity=0.1,
            layer="below",
            line_width=0,
            annotation_text="오후 피크",
            annotation_position="top left"
        )
    
    fig.update_layout(
        xaxis_title="시간대",
        yaxis_title="혼잡도 (%)",
        height=height,
        template='plotly_white',
        hovermode='x unified',
        margin=dict(t=50, b=50, l=50, r=30)
    )
    
    # x축 라벨 회전
    fig.update_xaxes(tickangle=-45)
    
    return fig


def create_hourly_heatmap(
    df: pd.DataFrame,
    title: str = "시간대 x 호선 혼잡도 히트맵",
    height: int = 500
) -> go.Figure:
    """
    시간대 x 호선 히트맵 생성
    
    Args:
        df: 데이터프레임 (호선, 시간대, 혼잡도 컬럼 필요)
        title: 차트 제목
        height: 차트 높이
        
    Returns:
        go.Figure: Plotly Figure 객체
    """
    # 피벗 테이블 생성
    pivot = df.pivot_table(
        values='혼잡도',
        index='호선',
        columns='시간대',
        aggfunc='mean'
    )
    
    # 호선 순으로 정렬
    line_order = sorted(pivot.index, key=lambda x: int(x.replace('호선', '').strip()))
    pivot = pivot.reindex(line_order)
    
    fig = px.imshow(
        pivot,
        labels=dict(x="시간대", y="호선", color="혼잡도 (%)"),
        color_continuous_scale="RdYlGn_r",
        aspect="auto",
        title=title
    )
    
    fig.update_layout(
        height=height,
        template='plotly_white',
        margin=dict(t=60, b=100, l=80, r=30),
        coloraxis_colorbar=dict(
            title="혼잡도 (%)",
            ticksuffix="%"
        )
    )
    
    # x축 라벨 회전
    fig.update_xaxes(tickangle=-45)
    
    return fig


if __name__ == "__main__":
    # 테스트용 코드
    print("Visualization 모듈 테스트")
    
    # 테스트 데이터
    test_data = pd.DataFrame({
        '호선': ['1호선', '2호선', '3호선', '4호선', '5호선'],
        '혼잡도': [45.2, 72.3, 55.8, 48.1, 68.5]
    })
    
    fig = create_line_bar_chart(test_data, x='호선', y='혼잡도', title='테스트 차트')
    print("막대 차트 생성 완료")
    print(f"Figure type: {type(fig)}")

