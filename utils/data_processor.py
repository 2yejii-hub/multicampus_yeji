"""
데이터 전처리 모듈
"""

import pandas as pd
import numpy as np
from typing import Dict, List


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    컬럼명을 정리합니다.
    
    Args:
        df: 원본 데이터프레임
        
    Returns:
        pd.DataFrame: 컬럼명이 정리된 데이터프레임
    """
    df_clean = df.copy()
    
    # CSV 실제 컬럼 구조:
    # 0: 요일구분 (평일, 토요일, 일요일)
    # 1: 호선
    # 2: 역번호
    # 3: 출발역 (역명)
    # 4: 상하구분 (평일, 휴일, 내선, 외선) -> 방향 정보
    
    cols = list(df_clean.columns)
    
    # 첫 5개 컬럼 이름 표준화
    new_cols = ['요일구분', '호선', '역번호', '역명', '방향'] + cols[5:]
    df_clean.columns = new_cols
    
    return df_clean


def convert_time_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    시간대 컬럼을 표준 형식으로 변환합니다.
    
    Args:
        df: 데이터프레임
        
    Returns:
        pd.DataFrame: 시간대 컬럼이 변환된 데이터프레임
    """
    df_clean = df.copy()
    
    # 시간대 컬럼 매핑 (원본 -> 표준 형식)
    time_mapping = {}
    
    # 시간대 패턴: "5시30분", "6시00분" 등
    for col in df.columns:
        if '시' in col and '분' in col:
            # "5시30분" -> "05:30"
            col_clean = col.replace('시', ':').replace('분', '').strip()
            
            # 시간 파싱
            parts = col_clean.split(':')
            if len(parts) == 2:
                hour = int(parts[0])
                minute = int(parts[1])
                
                # 0시는 24:00으로 표시
                if hour == 0:
                    hour = 24
                
                time_str = f"{hour:02d}:{minute:02d}"
                time_mapping[col] = time_str
    
    # 컬럼명 변경
    df_clean.rename(columns=time_mapping, inplace=True)
    
    return df_clean


def clean_congestion_values(df: pd.DataFrame, time_columns: List[str]) -> pd.DataFrame:
    """
    혼잡도 값을 정리합니다 (문자열 -> float 변환, 공백 제거).
    
    Args:
        df: 데이터프레임
        time_columns: 시간대 컬럼 리스트
        
    Returns:
        pd.DataFrame: 혼잡도 값이 정리된 데이터프레임
    """
    df_clean = df.copy()
    
    for col in time_columns:
        if col in df_clean.columns:
            # 문자열 공백 제거 후 float 변환
            df_clean[col] = pd.to_numeric(df_clean[col].astype(str).str.strip(), errors='coerce')
            
            # 음수 값을 0으로 처리
            df_clean[col] = df_clean[col].clip(lower=0)
            
            # 결측치를 0으로 채움
            df_clean[col] = df_clean[col].fillna(0)
    
    return df_clean


def melt_to_long_format(df: pd.DataFrame) -> pd.DataFrame:
    """
    Wide format을 Long format으로 변환합니다.
    
    Args:
        df: Wide format 데이터프레임
        
    Returns:
        pd.DataFrame: Long format 데이터프레임
    """
    # 시간대 컬럼 추출 (HH:MM 형식)
    time_columns = [col for col in df.columns if ':' in str(col)]
    
    # 기본 컬럼 (시간대가 아닌 컬럼)
    id_columns = [col for col in df.columns if col not in time_columns]
    
    # Melt 수행
    df_long = pd.melt(
        df,
        id_vars=id_columns,
        value_vars=time_columns,
        var_name='시간대',
        value_name='혼잡도'
    )
    
    # 시간대를 시간 순으로 정렬하기 위한 시간 값 생성
    df_long['시간_정렬용'] = df_long['시간대'].apply(lambda x: 
        int(x.split(':')[0]) * 60 + int(x.split(':')[1])
    )
    
    # 정렬
    df_long = df_long.sort_values(['호선', '역명', '방향', '요일구분', '시간_정렬용'])
    
    # 인덱스 리셋
    df_long = df_long.reset_index(drop=True)
    
    return df_long


def add_derived_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    파생 컬럼을 추가합니다.
    
    Args:
        df: 데이터프레임
        
    Returns:
        pd.DataFrame: 파생 컬럼이 추가된 데이터프레임
    """
    df_derived = df.copy()
    
    # 혼잡도 레벨 (여유/보통/혼잡)
    def get_congestion_level(congestion: float) -> str:
        if congestion < 50:
            return '여유'
        elif congestion < 70:
            return '보통'
        else:
            return '혼잡'
    
    df_derived['혼잡도_레벨'] = df_derived['혼잡도'].apply(get_congestion_level)
    
    # 시간대 구분 (새벽/오전/오후/저녁/심야)
    def get_time_period(time_str: str) -> str:
        hour = int(time_str.split(':')[0])
        if 5 <= hour < 9:
            return '출근시간'
        elif 9 <= hour < 12:
            return '오전'
        elif 12 <= hour < 14:
            return '점심시간'
        elif 14 <= hour < 18:
            return '오후'
        elif 18 <= hour < 21:
            return '퇴근시간'
        elif 21 <= hour < 24:
            return '저녁'
        else:
            return '심야'
    
    df_derived['시간대_구분'] = df_derived['시간대'].apply(get_time_period)
    
    # 호선 번호 (정렬용)
    df_derived['호선_번호'] = df_derived['호선'].str.extract(r'(\d+)').astype(int)
    
    return df_derived


def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    전체 데이터 전처리 파이프라인을 실행합니다.
    
    Args:
        df: 원본 데이터프레임
        
    Returns:
        pd.DataFrame: 전처리된 데이터프레임
    """
    print("\n[데이터 전처리 시작...]")
    print(f"   원본 데이터: {df.shape}")
    
    # 1. 컬럼명 정리
    print("\n[1] 컬럼명 정리 중...")
    df = clean_column_names(df)
    
    # 2. 시간대 컬럼 변환
    print("[2] 시간대 컬럼 변환 중...")
    df = convert_time_columns(df)
    
    # 3. 시간대 컬럼 리스트 추출
    time_columns = [col for col in df.columns if ':' in str(col)]
    print(f"   시간대 컬럼 수: {len(time_columns)}")
    
    # 4. 혼잡도 값 정리
    print("[3] 혼잡도 값 정리 중...")
    df = clean_congestion_values(df, time_columns)
    
    # 5. Long format으로 변환
    print("[4] Long format으로 변환 중...")
    df_long = melt_to_long_format(df)
    print(f"   변환 후 데이터: {df_long.shape}")
    
    # 6. 파생 컬럼 추가
    print("[5] 파생 컬럼 추가 중...")
    df_final = add_derived_columns(df_long)
    
    print(f"\n[완료] 전처리 완료: {df_final.shape}")
    print(f"   컬럼: {list(df_final.columns)}")
    
    return df_final


def get_statistics(df: pd.DataFrame) -> Dict:
    """
    데이터의 기본 통계를 계산합니다.
    
    Args:
        df: 데이터프레임
        
    Returns:
        dict: 통계 정보
    """
    stats = {
        '총_데이터_수': len(df),
        '호선_수': df['호선'].nunique(),
        '역_수': df['역명'].nunique(),
        '평균_혼잡도': df['혼잡도'].mean(),
        '최대_혼잡도': df['혼잡도'].max(),
        '최소_혼잡도': df['혼잡도'].min(),
        '혼잡도_표준편차': df['혼잡도'].std(),
    }
    
    # 가장 혼잡한 역/시간대
    if len(df) > 0:
        max_idx = df['혼잡도'].idxmax()
        stats['가장_혼잡한_역'] = df.loc[max_idx, '역명']
        stats['가장_혼잡한_시간'] = df.loc[max_idx, '시간대']
        stats['가장_혼잡한_혼잡도'] = df.loc[max_idx, '혼잡도']
    
    return stats


def validate_data(df: pd.DataFrame) -> bool:
    """
    데이터 유효성을 검증합니다.
    
    Args:
        df: 데이터프레임
        
    Returns:
        bool: 유효성 검증 결과
    """
    print("\n[데이터 유효성 검증...]")
    
    # 필수 컬럼 확인
    required_columns = ['호선', '역명', '방향', '요일구분', '시간대', '혼잡도']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        print(f"[오류] 필수 컬럼 누락: {missing_columns}")
        return False
    
    print("[완료] 필수 컬럼 확인 완료")
    
    # 데이터 타입 확인
    if not pd.api.types.is_numeric_dtype(df['혼잡도']):
        print("[오류] 혼잡도 컬럼이 숫자형이 아닙니다")
        return False
    
    print("[완료] 데이터 타입 확인 완료")
    
    # 혼잡도 범위 확인
    if df['혼잡도'].min() < 0:
        print("[경고] 음수 혼잡도 값이 있습니다")
    
    if df['혼잡도'].max() > 200:
        print("[경고] 비정상적으로 높은 혼잡도 값이 있습니다 (200% 이상)")
    
    print("[완료] 혼잡도 범위 확인 완료")
    
    # 결측치 확인
    null_counts = df[required_columns].isnull().sum()
    if null_counts.sum() > 0:
        print(f"[경고] 결측치 발견:\n{null_counts[null_counts > 0]}")
    else:
        print("[완료] 결측치 없음")
    
    return True


if __name__ == "__main__":
    # 테스트용 코드
    from data_loader import load_raw_data, save_processed_data
    
    print("=" * 60)
    print("데이터 전처리 테스트")
    print("=" * 60)
    
    # 원본 데이터 로드
    df_raw = load_raw_data()
    
    # 전처리 실행
    df_processed = preprocess_data(df_raw)
    
    # 유효성 검증
    is_valid = validate_data(df_processed)
    
    if is_valid:
        # 통계 출력
        print("\n" + "=" * 60)
        print("데이터 통계")
        print("=" * 60)
        stats = get_statistics(df_processed)
        for key, value in stats.items():
            print(f"{key}: {value}")
        
        # 샘플 데이터 출력
        print("\n" + "=" * 60)
        print("샘플 데이터 (첫 10행)")
        print("=" * 60)
        print(df_processed.head(10))
        
        # 저장
        print("\n" + "=" * 60)
        save_processed_data(df_processed)
    else:
        print("\n❌ 데이터 유효성 검증 실패")

