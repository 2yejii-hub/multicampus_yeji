# -*- coding: utf-8 -*-
"""
서울 지하철 혼잡도 대시보드 - 메인 페이지
"""

import streamlit as st
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.data_loader import load_processed_data, check_data_files
from utils.data_processor import get_statistics


# 페이지 설정
st.set_page_config(
    page_title="서울 지하철 혼잡도 대시보드",
    page_icon="🚇",
    layout="wide",
    initial_sidebar_state="expanded"
)


def main():
    """메인 페이지"""
    
    # 타이틀
    st.title("🚇 서울 지하철 혼잡도 대시보드")
    st.markdown("실시간 지하철 혼잡도를 확인하고 최적의 이동 시간을 찾아보세요!")
    
    st.divider()
    
    # 데이터 로드
    try:
        with st.spinner('데이터를 불러오는 중...'):
            df = load_processed_data()
        
        st.success(f"✅ 데이터 로드 완료: {len(df):,}개의 데이터")
        
        # 기본 통계
        st.subheader("📊 전체 통계")
        
        stats = get_statistics(df)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="전체 평균 혼잡도",
                value=f"{stats['평균_혼잡도']:.1f}%"
            )
        
        with col2:
            st.metric(
                label="분석 역 수",
                value=f"{stats['역_수']}개"
            )
        
        with col3:
            st.metric(
                label="가장 혼잡한 역",
                value=stats['가장_혼잡한_역']
            )
        
        with col4:
            st.metric(
                label="피크 시간대",
                value=stats['가장_혼잡한_시간']
            )
        
        # 샘플 데이터 표시
        st.divider()
        st.subheader("📋 데이터 미리보기")
        st.dataframe(df.head(20), use_container_width=True)
        
        # 데이터 정보
        with st.expander("ℹ️ 데이터 정보"):
            st.write(f"**전체 데이터 수**: {len(df):,}행")
            st.write(f"**컬럼 수**: {len(df.columns)}개")
            st.write(f"**컬럼**: {', '.join(df.columns)}")
            st.write(f"**호선**: {', '.join(sorted(df['호선'].unique()))}")
        
    except FileNotFoundError as e:
        st.error(f"""
        ❌ 전처리된 데이터 파일을 찾을 수 없습니다.
        
        먼저 데이터 전처리를 실행해주세요:
        ```bash
        python preprocess.py
        ```
        """)
    except Exception as e:
        st.error(f"❌ 오류가 발생했습니다: {str(e)}")
        st.info("페이지를 새로고침하거나 관리자에게 문의하세요.")
    
    # 사이드바
    with st.sidebar:
        st.header("📖 사용 방법")
        st.markdown("""
        1. **대시보드**: 전체 혼잡도 통계 확인
        2. **역별 분석**: 특정 역의 상세 분석
        3. **시간대 분석**: 시간대별 혼잡도 패턴
        4. **추천**: 최적 이동 시간 추천
        
        *(Phase 2 이후 추가 예정)*
        """)
        
        st.divider()
        
        st.info("""
        **Phase 1 완료** ✅
        - 데이터 전처리
        - 기본 구조 설정
        """)


if __name__ == "__main__":
    main()
