"""
데이터 로딩 및 캐싱 모듈
"""

import os
import pandas as pd
import streamlit as st
from pathlib import Path


def get_project_root() -> Path:
    """프로젝트 루트 디렉토리 경로 반환"""
    return Path(__file__).parent.parent


def get_raw_data_path() -> Path:
    """원본 CSV 파일 경로 반환"""
    return get_project_root() / "data" / "raw" / "서울교통공사_지하철혼잡도정보_20250930.csv"


def get_processed_data_path() -> Path:
    """전처리된 pickle 파일 경로 반환"""
    return get_project_root() / "data" / "processed" / "subway_congestion.pkl"


@st.cache_data(ttl=3600)
def load_raw_data() -> pd.DataFrame:
    """
    원본 CSV 파일을 로드합니다.
    
    Returns:
        pd.DataFrame: 원본 데이터프레임
    
    Raises:
        FileNotFoundError: CSV 파일을 찾을 수 없는 경우
        UnicodeDecodeError: 인코딩 오류가 발생한 경우
    """
    file_path = get_raw_data_path()
    
    if not file_path.exists():
        raise FileNotFoundError(f"CSV 파일을 찾을 수 없습니다: {file_path}")
    
    try:
        # CP949 인코딩으로 시도
        df = pd.read_csv(file_path, encoding='cp949')
        print(f"[완료] CSV 파일 로드 완료: {len(df)}행")
        return df
    except UnicodeDecodeError:
        # UTF-8-sig 인코딩으로 재시도
        try:
            df = pd.read_csv(file_path, encoding='utf-8-sig')
            print(f"[완료] CSV 파일 로드 완료 (UTF-8): {len(df)}행")
            return df
        except Exception as e:
            raise UnicodeDecodeError(
                'encoding',
                b'',
                0,
                1,
                f"인코딩 오류 발생: {str(e)}"
            )


@st.cache_data(ttl=3600)
def load_processed_data() -> pd.DataFrame:
    """
    전처리된 pickle 파일을 로드합니다.
    
    Returns:
        pd.DataFrame: 전처리된 데이터프레임
        
    Raises:
        FileNotFoundError: pickle 파일을 찾을 수 없는 경우
    """
    file_path = get_processed_data_path()
    
    if not file_path.exists():
        raise FileNotFoundError(
            f"전처리된 파일을 찾을 수 없습니다: {file_path}\n"
            "먼저 데이터 전처리를 실행해주세요."
        )
    
    df = pd.read_pickle(file_path)
    print(f"[완료] 전처리된 데이터 로드 완료: {len(df)}행")
    return df


def save_processed_data(df: pd.DataFrame) -> None:
    """
    전처리된 데이터를 pickle 파일로 저장합니다.
    
    Args:
        df: 저장할 데이터프레임
    """
    file_path = get_processed_data_path()
    
    # 디렉토리가 없으면 생성
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # pickle 파일로 저장
    df.to_pickle(file_path)
    print(f"[완료] 전처리된 데이터 저장 완료: {file_path}")
    print(f"   - 행 수: {len(df)}")
    print(f"   - 파일 크기: {file_path.stat().st_size / 1024:.2f} KB")


def check_data_files() -> dict:
    """
    데이터 파일 존재 여부 확인
    
    Returns:
        dict: 파일 존재 여부 및 정보
    """
    raw_path = get_raw_data_path()
    processed_path = get_processed_data_path()
    
    return {
        'raw_exists': raw_path.exists(),
        'raw_path': str(raw_path),
        'processed_exists': processed_path.exists(),
        'processed_path': str(processed_path),
    }


if __name__ == "__main__":
    # 테스트용 코드
    print("=" * 50)
    print("데이터 로더 테스트")
    print("=" * 50)
    
    # 파일 존재 여부 확인
    file_info = check_data_files()
    print(f"\n📁 원본 CSV: {file_info['raw_exists']}")
    print(f"   경로: {file_info['raw_path']}")
    print(f"\n📁 전처리 데이터: {file_info['processed_exists']}")
    print(f"   경로: {file_info['processed_path']}")
    
    # 원본 데이터 로드 테스트
    if file_info['raw_exists']:
        print("\n" + "=" * 50)
        print("원본 데이터 로드 테스트")
        print("=" * 50)
        df = load_raw_data()
        print(f"\n데이터 형태: {df.shape}")
        print(f"\n컬럼: {list(df.columns)}")
        print(f"\n첫 5행:")
        print(df.head())

