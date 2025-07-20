import matplotlib.pyplot as plt
import numpy as np  # cycle_count와 capacity_list가 numpy 배열로 가정

# 저널 스타일 설정 (이전 답변에서 제공한 설정 재사용)
plt.rcParams['figure.figsize'] = [6.4, 4.8]  # 적당한 그림 크기 (인치 단위)
plt.rcParams['font.family'] = 'Times New Roman'  # 저널 선호 폰트
plt.rcParams['font.size'] = 10  # 폰트 크기 (10pt, 저널 표준)
plt.rcParams['axes.linewidth'] = 0.8  # 축 선 두께
plt.rcParams['axes.titlesize'] = 12  # 제목 폰트 크기
plt.rcParams['axes.labelsize'] = 10  # 축 라벨 폰트 크기
plt.rcParams['xtick.labelsize'] = 8  # x축 눈금 라벨 크기
plt.rcParams['ytick.labelsize'] = 8  # y축 눈금 라벨 크기
plt.rcParams['xtick.major.size'] = 4  # x축 주요 눈금 길이
plt.rcParams['xtick.major.width'] = 0.8  # x축 주요 눈금 두께
plt.rcParams['ytick.major.size'] = 4  # y축 주요 눈금 길이
plt.rcParams['ytick.major.width'] = 0.8  # y축 주요 눈금 두께
plt.rcParams['xtick.minor.size'] = 2  # x축 보조 눈금 길이
plt.rcParams['xtick.minor.width'] = 0.6  # x축 보조 눈금 두께
plt.rcParams['ytick.minor.size'] = 2  # y축 보조 눈금 길이
plt.rcParams['ytick.minor.width'] = 0.6  # y축 보조 눈금 두께
plt.rcParams['xtick.direction'] = 'in'  # 눈금 안쪽으로
plt.rcParams['ytick.direction'] = 'in'  # 눈금 안쪽으로
plt.rcParams['lines.linewidth'] = 1.5  # 선 두께
plt.rcParams['legend.fontsize'] = 8  # 범례 폰트 크기
plt.rcParams['figure.dpi'] = 300  # 고해상도 출력

# 산점도 플롯
plt.scatter(
    cycle_count,
    capacity_list,
    s=30,  # 마커 크기 (저널에서 적당히 작고 명확한 크기)
    marker='o',  # 원형 마커 (저널에서 선호)
    color='black',  # 기본 색상 (흑백 호환성 고려)
    edgecolors='none',  # 마커 테두리 제거 (깔끔한 외관)
    alpha=0.7,  # 약간의 투명도 (중첩 시 가독성 향상)
    linewidths=0  # 테두리 선 두께 제거
)

# 축 범위 설정 (이전 코드에서 제공된 값 유지)
plt.xlim([-100, 2100])
plt.ylim([-0.02, 1.1])

# 축 라벨 추가 (저널 스타일에 맞게 간결하고 명확)
plt.xlabel('Cycle Count', fontsize=10)
plt.ylabel('Capacity', fontsize=10)

# 그림 저장 (저널 제咯
plt.savefig('figure.eps', format='eps', dpi=300, bbox_inches='tight')