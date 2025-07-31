import os
import pandas as pd
from pathlib import Path
import re
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class DataProcessorApp(tk.Tk):
    """
    Toyo 충방전기 데이터 처리를 위한 GUI 애플리케이션
    """
    def __init__(self):
        super().__init__()
        self.title("Toyo 데이터 전처리기")
        self.geometry("1000x750")

        # --- 변수 설정 ---
        self.source_dir = tk.StringVar()
        self.dest_dir = tk.StringVar()

        # --- UI 구성 ---
        self.create_widgets()

    def create_widgets(self):
        # 메인 프레임
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- 1. 경로 설정 프레임 ---
        path_frame = ttk.LabelFrame(main_frame, text="경로 설정", padding="10")
        path_frame.pack(fill=tk.X, pady=5)

        # 소스 경로
        ttk.Label(path_frame, text="원본 폴더:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(path_frame, textvariable=self.source_dir, width=60).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(path_frame, text="찾아보기", command=self.select_source_dir).grid(row=0, column=2, padx=5, pady=5)

        # 목적지 경로
        ttk.Label(path_frame, text="저장 폴더:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(path_frame, textvariable=self.dest_dir, width=60).grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(path_frame, text="찾아보기", command=self.select_dest_dir).grid(row=1, column=2, padx=5, pady=5)
        
        path_frame.grid_columnconfigure(1, weight=1)

        # --- 2. 실행 버튼 ---
        self.run_button = ttk.Button(main_frame, text="처리 시작", command=self.start_processing)
        self.run_button.pack(fill=tk.X, pady=10)

        # --- 3. 결과 표시 프레임 (로그와 데이터 뷰) ---
        results_pane = ttk.PanedWindow(main_frame, orient=tk.VERTICAL)
        results_pane.pack(fill=tk.BOTH, expand=True, pady=5)

        # 로그 프레임
        log_frame = ttk.LabelFrame(results_pane, text="처리 로그", padding="5")
        self.log_text = tk.Text(log_frame, height=10, wrap=tk.WORD, state=tk.DISABLED)
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.config(yscrollcommand=log_scrollbar.set)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        results_pane.add(log_frame, weight=1)

        # 데이터 뷰 프레임
        data_view_frame = ttk.LabelFrame(results_pane, text="처리 결과 보기", padding="5")
        
        data_view_pane = ttk.PanedWindow(data_view_frame, orient=tk.HORIZONTAL)
        data_view_pane.pack(fill=tk.BOTH, expand=True)

        # 파일 목록
        file_list_frame = ttk.Frame(data_view_pane)
        ttk.Label(file_list_frame, text="생성된 파일 목록").pack(anchor="w")
        self.file_tree = ttk.Treeview(file_list_frame, columns=("filename",), show="headings", height=15)
        self.file_tree.heading("filename", text="파일 이름")
        self.file_tree.pack(fill=tk.BOTH, expand=True)
        self.file_tree.bind("<<TreeviewSelect>>", self.on_file_select)
        data_view_pane.add(file_list_frame, weight=1)

        # 데이터 테이블
        data_table_frame = ttk.Frame(data_view_pane)
        ttk.Label(data_table_frame, text="파일 내용").pack(anchor="w")
        self.data_tree = ttk.Treeview(data_table_frame, show="headings")
        
        # 데이터 테이블 스크롤바
        data_x_scrollbar = ttk.Scrollbar(data_table_frame, orient=tk.HORIZONTAL, command=self.data_tree.xview)
        data_y_scrollbar = ttk.Scrollbar(data_table_frame, orient=tk.VERTICAL, command=self.data_tree.yview)
        self.data_tree.configure(xscrollcommand=data_x_scrollbar.set, yscrollcommand=data_y_scrollbar.set)

        data_y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        data_x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.data_tree.pack(fill=tk.BOTH, expand=True)
        data_view_pane.add(data_table_frame, weight=3)

        results_pane.add(data_view_frame, weight=2)

    def log(self, message):
        """로그 텍스트 위젯에 메시지를 추가합니다."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.update_idletasks()

    def select_source_dir(self):
        """소스 폴더 선택 대화상자를 엽니다."""
        dir_path = filedialog.askdirectory(title="원본 데이터 폴더를 선택하세요")
        if dir_path:
            self.source_dir.set(dir_path)
            # 목적지 폴더가 비어있으면 자동으로 'processed' 폴더를 제안
            if not self.dest_dir.get():
                self.dest_dir.set(os.path.join(dir_path, '..', 'processed'))

    def select_dest_dir(self):
        """저장 폴더 선택 대화상자를 엽니다."""
        dir_path = filedialog.askdirectory(title="처리된 파일을 저장할 폴더를 선택하세요")
        if dir_path:
            self.dest_dir.set(dir_path)

    def start_processing(self):
        """데이터 처리 스레드를 시작합니다."""
        src = self.source_dir.get()
        dst = self.dest_dir.get()

        if not src or not dst:
            messagebox.showerror("오류", "원본 폴더와 저장 폴더를 모두 지정해야 합니다.")
            return

        # UI 비활성화
        self.run_button.config(state=tk.DISABLED, text="처리 중...")
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete('1.0', tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        # 결과 뷰 초기화
        for i in self.file_tree.get_children():
            self.file_tree.delete(i)
        for i in self.data_tree.get_children():
            self.data_tree.delete(i)
        self.data_tree["columns"] = []


        # 별도의 스레드에서 처리 함수 실행 (GUI 멈춤 방지)
        thread = threading.Thread(target=self.run_preprocessing_task, args=(src, dst))
        thread.daemon = True
        thread.start()

    def run_preprocessing_task(self, src_dir, dst_dir):
        """실제 데이터 처리 로직을 실행하는 함수."""
        try:
            self.preprocess_toyo_data(src_dir, dst_dir)
            self.log("\n✅ 모든 처리가 완료되었습니다.")
            messagebox.showinfo("완료", "데이터 처리가 성공적으로 완료되었습니다.")
            self.update_result_files(dst_dir)
        except Exception as e:
            self.log(f"\n❌ 처리 중 오류 발생: {e}")
            messagebox.showerror("오류", f"처리 중 오류가 발생했습니다:\n{e}")
        finally:
            # UI 활성화
            self.run_button.config(state=tk.NORMAL, text="처리 시작")

    def update_result_files(self, directory):
        """처리된 파일 목록을 UI에 업데이트합니다."""
        for i in self.file_tree.get_children():
            self.file_tree.delete(i)
        
        try:
            files = [f for f in os.listdir(directory) if f.endswith('.csv')]
            for f in sorted(files):
                self.file_tree.insert("", "end", values=(f,))
        except Exception as e:
            self.log(f"결과 파일 목록을 불러오는 데 실패했습니다: {e}")

    def on_file_select(self, event):
        """파일 목록에서 파일을 선택했을 때 내용을 표시합니다."""
        selected_items = self.file_tree.selection()
        if not selected_items:
            return
        
        selected_file = self.file_tree.item(selected_items[0])['values'][0]
        file_path = Path(self.dest_dir.get()) / selected_file

        try:
            df = pd.read_csv(file_path)
            
            # 이전 데이터 테이블 지우기
            for i in self.data_tree.get_children():
                self.data_tree.delete(i)

            # 새 데이터 테이블 설정
            self.data_tree["columns"] = list(df.columns)
            self.data_tree["show"] = "headings"

            for col in df.columns:
                self.data_tree.heading(col, text=col)
                self.data_tree.column(col, width=100, anchor='center')

            for index, row in df.head(200).iterrows(): # 성능을 위해 최대 200개 행만 표시
                self.data_tree.insert("", "end", values=list(row))

        except Exception as e:
            messagebox.showerror("파일 읽기 오류", f"파일을 읽는 중 오류가 발생했습니다:\n{e}")

    def preprocess_toyo_data(self, src_dir: str, dst_dir: str):
        """
        Toyo 충방전기 원시 데이터를 전처리하고 결과를 저장하는 핵심 로직.
        GUI와 연동되도록 print 대신 self.log()를 사용합니다.
        """
        src_path = Path(src_dir)
        dst_path = Path(dst_dir)
        
        dst_path.mkdir(parents=True, exist_ok=True)
        self.log(f"Source directory: {src_path.resolve()}")
        self.log(f"Destination directory: {dst_path.resolve()}")

        # 범용성을 위해 이름 규칙을 더 유연하게 변경
        # 이름이 'CH'로 시작하거나, 숫자로만 구성된 폴더를 채널로 간주
        channel_dirs = [
            d for d in src_path.iterdir() 
            if d.is_dir() and (d.name.isdigit() or d.name.upper().startswith('CH'))
        ]
        
        if not channel_dirs:
            self.log(f"경고: {src_path}에서 채널 폴더를 찾을 수 없습니다. (폴더 이름이 'CH'로 시작하거나 숫자인지 확인하세요)")
            return

        self.log(f"총 {len(channel_dirs)}개의 채널을 찾았습니다: {[d.name for d in channel_dirs]}")

        for channel_path in sorted(channel_dirs, key=lambda p: p.name):
            channel_name = channel_path.name
            self.log(f"\n--- 채널 처리 시작: {channel_name} ---")

            # --- 사이클 상세 데이터 처리 ---
            try:
                # 확장자를 제외한 파일명이 숫자인 파일들을 대상으로 함 (.csv, .txt 등 포함)
                cycle_files = sorted([
                    f for f in channel_path.iterdir() 
                    if f.is_file() and f.stem.isdigit()
                ])

                if not cycle_files:
                    self.log(f"  - 채널 {channel_name}에서 사이클 데이터 파일을 찾지 못했습니다.")
                else:
                    all_cycle_dfs = []
                    self.log(f"  - 채널 {channel_name}에서 {len(cycle_files)}개의 사이클 파일을 읽는 중...")
                    for f in cycle_files:
                        try:
                            # 헤더 위치를 동적으로 찾기
                            skiprows = 0
                            with open(f, 'r', encoding='cp949', errors='ignore') as temp_f:
                                for i, line in enumerate(temp_f):
                                    if 'Pass/Fail' in line or 'Step' in line:
                                        skiprows = i
                                        break
                            
                            df = pd.read_csv(f, skiprows=skiprows, encoding='cp949', low_memory=False)
                            all_cycle_dfs.append(df)
                        except Exception as e:
                            self.log(f"    - 경고: 파일 {f.name}을 읽지 못했습니다. 오류: {e}")

                    if all_cycle_dfs:
                        full_cycle_df = pd.concat(all_cycle_dfs, ignore_index=True)
                        
                        cleaned_columns = {col: re.sub(r'[\[\]\s]', '', col) for col in full_cycle_df.columns}
                        full_cycle_df = full_cycle_df.rename(columns=cleaned_columns)

                        # 필요한 컬럼만 이름으로 선택 (더 안정적인 방법)
                        required_cols = {
                            'Date', 'Time', 'PassTime(s)', 'Voltage(V)', 'Current(mA)', 
                            'Temp1(Deg)', 'Mode', 'Cycle', 'TotalCycle'
                        }
                        
                        # 실제 존재하는 컬럼만 필터링
                        available_cols = [col for col in required_cols if col in full_cycle_df.columns]
                        missing_cols = required_cols - set(available_cols)
                        if missing_cols:
                            self.log(f"    - 경고: 필요한 컬럼 일부를 찾을 수 없습니다: {missing_cols}")
                        
                        cycle_df_processed = full_cycle_df[available_cols].copy()
                        
                        # 새 컬럼 이름 지정
                        rename_map = {
                            'PassTime(s)': 'PassTime_s', 'Voltage(V)': 'Voltage_V', 'Current(mA)': 'Current_mA',
                            'Temp1(Deg)': 'Temperature_C'
                        }
                        cycle_df_processed.rename(columns=rename_map, inplace=True)

                        output_filename = dst_path / f"{channel_name}_cycle_detail.csv"
                        cycle_df_processed.to_csv(output_filename, index=False, encoding='utf-8-sig')
                        self.log(f"  - 사이클 상세 데이터 저장 완료: {output_filename.name}")
            except Exception as e:
                self.log(f"  - 오류: 채널 {channel_name}의 사이클 데이터 처리 중 오류 발생: {e}")

            # --- 사이클 요약 데이터 처리 (CAPACITY.LOG) ---
            try:
                capacity_log_path = channel_path / "CAPACITY.LOG"
                if not capacity_log_path.exists():
                    self.log(f"  - 채널 {channel_name}에서 CAPACITY.LOG 파일을 찾지 못했습니다.")
                else:
                    cap_df = pd.read_csv(capacity_log_path, encoding='cp949')
                    
                    cleaned_columns = {col: re.sub(r'[\[\]\s]', '', col) for col in cap_df.columns}
                    cap_df = cap_df.rename(columns=cleaned_columns)

                    required_cols = [
                        'Date', 'Time', 'Condition', 'Mode', 'Cycle', 
                        'Cap(mAh)', 'Pow(mWh)', 'AveVolt(V)', 'PeakTemp(Deg)'
                    ]
                    cap_df_processed = cap_df[required_cols].copy()
                    
                    rename_map = {
                        'Cap(mAh)': 'Cap_mAh', 'Pow(mWh)': 'Pow_mWh', 
                        'AveVolt(V)': 'AveVolt_V', 'PeakTemp(Deg)': 'PeakTemp_Deg'
                    }
                    cap_df_processed.rename(columns=rename_map, inplace=True)

                    output_filename = dst_path / f"{channel_name}_capacity_summary.csv"
                    cap_df_processed.to_csv(output_filename, index=False, encoding='utf-8-sig')
                    self.log(f"  - 용량 요약 데이터 저장 완료: {output_filename.name}")
            except Exception as e:
                self.log(f"  - 오류: 채널 {channel_name}의 용량 로그 처리 중 오류 발생: {e}")

if __name__ == '__main__':
    app = DataProcessorApp()
    app.mainloop()

