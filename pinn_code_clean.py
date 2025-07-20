import matplotlib.pyplot as plt

# 저널 스타일 설정
plt.rcParams['figure.figsize'] = [6.4, 4.8]  # 적당한 그림 크기 (인치 단위, APS/Nature 권장)
plt.rcParams['font.family'] = 'Times New Roman'  # 저널에서 선호하는 폰트
plt.rcParams['font.size'] = 10  # 저널에서 일반적인 폰트 크기 (10-12pt)
plt.rcParams['axes.linewidth'] = 0.8  # 축 선 두께 (얇고 깔끔)
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
plt.rcParams['lines.linewidth'] = 1.5  # 선 두께 (저널에서 선호하는 얇은 선)
plt.rcParams['legend.fontsize'] = 8  # 범례 폰트 크기
plt.rcParams['figure.dpi'] = 300  # 고해상도 출력 (저널 요구사항)

# 축 범위 설정
plt.xlim([-100, 2100])
plt.ylim([-0.02, 1.1])