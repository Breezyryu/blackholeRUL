import os
import pandas as pd
from pathlib import Path
from tqdm import tqdm
import re

def preprocess_toyo_data(src_dir: str, dst_dir: str):
    """
    Toyo 충방전기에서 생성된 원시 데이터를 읽어와 전처리하고,
    채널별로 사이클 데이터와 용량 데이터를 분리하여 저장합니다.

    Args:
        src_dir (str): 원시 데이터가 있는 상위 폴더 경로.
        dst_dir (str): 전처리된 데이터를 저장할 폴더 경로.
    """
    # --- 1. 경로 설정 및 출력 폴더 생성 ---
    src_path = Path(src_dir)
    dst_path = Path(dst_dir)
    
    # 출력 폴더가 없으면 생성
    dst_path.mkdir(parents=True, exist_ok=True)
    print(f"Source directory: {src_path.resolve()}")
    print(f"Destination directory: {dst_path.resolve()}")

    # 소스 디렉토리에서 채널 폴더 목록 가져오기
    # is_dir()를 통해 폴더만 필터링하고, 이름이 숫자로만 구성된 폴더를 채널로 간주
    channel_dirs = [d for d in src_path.iterdir() if d.is_dir() and d.name.isdigit()]
    
    if not channel_dirs:
        print(f"No channel directories found in {src_path}. Please check the directory structure.")
        return

    print(f"Found {len(channel_dirs)} channel(s): {[d.name for d in channel_dirs]}")

    # --- 2. 각 채널 폴더에 대해 순차적으로 처리 ---
    for channel_path in tqdm(channel_dirs, desc="Processing Channels"):
        channel_name = channel_path.name
        print(f"\n--- Processing Channel: {channel_name} ---")

        # --- 3. 사이클 상세 데이터 처리 (000001, 000002, ...) ---
        try:
            # 채널 폴더 내의 모든 파일을 가져와 숫자로 된 파일 이름만 필터링
            cycle_files = sorted([
                f for f in channel_path.iterdir() 
                if f.is_file() and f.name.isdigit()
            ])

            if not cycle_files:
                print(f"  - No cycle data files found in channel {channel_name}. Skipping cycle data processing.")
            else:
                all_cycle_dfs = []
                for f in tqdm(cycle_files, desc=f"  - Reading cycle files for Ch {channel_name}", leave=False):
                    try:
                        # 파일의 헤더 시작 위치를 찾아 skiprows 값으로 사용 (보통 8번째 줄 이후)
                        # 인코딩은 'cp949' 또는 'euc-kr'을 시도하여 한글 깨짐 방지
                        df = pd.read_csv(f, skiprows=8, encoding='cp949', low_memory=False)
                        all_cycle_dfs.append(df)
                    except Exception as e:
                        print(f"    - Warning: Could not read file {f.name}. Error: {e}")

                # 모든 사이클 데이터프레임을 하나로 합치기
                if all_cycle_dfs:
                    full_cycle_df = pd.concat(all_cycle_dfs, ignore_index=True)
                    
                    # 불필요한 공백 및 특수문자 제거 후 컬럼 이름 정리
                    # 예: 'Voltage[V]' -> 'Voltage_V'
                    cleaned_columns = {col: re.sub(r'\[|\]', '', col).replace(' ', '') for col in full_cycle_df.columns}
                    full_cycle_df = full_cycle_df.rename(columns=cleaned_columns)

                    # 필요한 컬럼만 선택
                    # Temp1Deg가 두 번 나타나므로, iloc을 사용하여 위치 기반으로 선택
                    # 첫 번째 Temp1Deg는 8번째 컬럼, 두 번째는 16번째 컬럼
                    # 여기서는 첫 번째 온도 센서 값을 사용
                    cycle_df_processed = full_cycle_df.iloc[:, [0, 1, 2, 3, 4, 7, 12, 13, 14]].copy()
                    cycle_df_processed.columns = [
                        'Date', 'Time', 'PassTime_s', 'Voltage_V', 'Current_mA', 
                        'Temperature_C', 'Mode', 'Cycle', 'TotalCycle'
                    ]

                    # 데이터 타입 변환
                    numeric_cols = ['PassTime_s', 'Voltage_V', 'Current_mA', 'Temperature_C', 'Cycle', 'TotalCycle']
                    for col in numeric_cols:
                        cycle_df_processed[col] = pd.to_numeric(cycle_df_processed[col], errors='coerce')
                    
                    # 전처리된 데이터 저장
                    output_filename = dst_path / f"{channel_name}_cycle_detail.csv"
                    cycle_df_processed.to_csv(output_filename, index=False, encoding='utf-8-sig')
                    print(f"  - Successfully processed and saved cycle detail data to {output_filename.name}")

        except Exception as e:
            print(f"  - Error processing cycle data for channel {channel_name}: {e}")

        # --- 4. 사이클 요약 데이터 처리 (CAPACITY.LOG) ---
        try:
            capacity_log_path = channel_path / "CAPACITY.LOG"
            if not capacity_log_path.exists():
                print(f"  - CAPACITY.LOG not found in channel {channel_name}. Skipping capacity data processing.")
            else:
                cap_df = pd.read_csv(capacity_log_path, encoding='cp949')
                
                # 컬럼 이름 정리
                cleaned_columns = {col: re.sub(r'\[|\]', '', col).replace(' ', '') for col in cap_df.columns}
                cap_df = cap_df.rename(columns=cleaned_columns)

                # 필요한 컬럼 선택
                cap_df_processed = cap_df[[
                    'Date', 'Time', 'Condition', 'Mode', 'Cycle', 
                    'CapmAh', 'PowmWh', 'AveVoltV', 'PeakTempDeg'
                ]].copy()

                # 데이터 타입 변환
                numeric_cols = ['Cycle', 'CapmAh', 'PowmWh', 'AveVoltV', 'PeakTempDeg']
                for col in numeric_cols:
                    cap_df_processed[col] = pd.to_numeric(cap_df_processed[col], errors='coerce')

                # 전처리된 데이터 저장
                output_filename = dst_path / f"{channel_name}_capacity_summary.csv"
                cap_df_processed.to_csv(output_filename, index=False, encoding='utf-8-sig')
                print(f"  - Successfully processed and saved capacity summary data to {output_filename.name}")

        except Exception as e:
            print(f"  - Error processing capacity log for channel {channel_name}: {e}")

    print("\nAll processing complete.")


if __name__ == '__main__':
    # --- 사용자 설정 영역 ---
    # 원시 데이터와 전처리된 데이터를 저장할 경로를 지정합니다.
    # 스크립트 파일 위치를 기준으로 상대 경로를 사용합니다.
    # 예: C:/Users/MyUser/Desktop/data/raw
    
    # 현재 스크립트 파일의 위치를 기준으로 경로 설정
    BASE_DIR = Path(__file__).resolve().parent
    
    # ../../data/raw 와 같이 상대 경로를 사용하거나 절대 경로를 직접 입력
    SOURCE_DIRECTORY = BASE_DIR / '../../data/raw'
    DESTINATION_DIRECTORY = BASE_DIR / '../../data/processed'

    # --- 전처리 함수 실행 ---
    preprocess_toyo_data(str(SOURCE_DIRECTORY), str(DESTINATION_DIRECTORY))

