# -*- coding: utf-8 -*-
"""
데이터 전처리 실행 스크립트
"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.data_loader import load_raw_data, save_processed_data, check_data_files
from utils.data_processor import preprocess_data, get_statistics, validate_data


def main():
    """메인 전처리 실행 함수"""
    print("=" * 70)
    print("[서울 지하철 혼잡도 데이터 전처리]")
    print("=" * 70)
    
    # 1. 파일 존재 여부 확인
    print("\n[파일 확인 중...]")
    file_info = check_data_files()
    
    if not file_info['raw_exists']:
        print(f"[오류] 원본 CSV 파일을 찾을 수 없습니다: {file_info['raw_path']}")
        return
    
    print(f"[완료] 원본 CSV 파일 확인: {file_info['raw_path']}")
    
    # 2. 원본 데이터 로드
    print("\n[원본 데이터 로드 중...]")
    try:
        df_raw = load_raw_data()
        print(f"[완료] 로드 완료: {df_raw.shape[0]}행 x {df_raw.shape[1]}컬럼")
    except Exception as e:
        print(f"[오류] 데이터 로드 실패: {str(e)}")
        return
    
    # 3. 데이터 전처리
    try:
        df_processed = preprocess_data(df_raw)
    except Exception as e:
        print(f"[오류] 전처리 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        return
    
    # 4. 데이터 유효성 검증
    is_valid = validate_data(df_processed)
    
    if not is_valid:
        print("\n[오류] 데이터 유효성 검증 실패")
        return
    
    # 5. 통계 출력
    print("\n" + "=" * 70)
    print("[데이터 통계]")
    print("=" * 70)
    stats = get_statistics(df_processed)
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")
    
    # 6. 샘플 데이터 출력
    print("\n" + "=" * 70)
    print("[샘플 데이터 (첫 5행)]")
    print("=" * 70)
    print(df_processed.head(5).to_string())
    
    # 7. 전처리된 데이터 저장
    print("\n" + "=" * 70)
    print("[전처리된 데이터 저장 중...]")
    print("=" * 70)
    try:
        save_processed_data(df_processed)
        print("\n[완료] 전처리 완료!")
        print(f"   저장 위치: {file_info['processed_path']}")
    except Exception as e:
        print(f"\n[오류] 저장 실패: {str(e)}")
        return
    
    print("\n" + "=" * 70)
    print("[모든 작업이 완료되었습니다!]")
    print("=" * 70)


if __name__ == "__main__":
    main()
