import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
import os
# ===================== 新增：中文显示配置（关键） =====================
# 1. 设置全局字体，适配不同系统
plt.rcParams["font.family"] = ["SimHei", "DejaVu Sans"]
# 2. 解决负号显示问题（可选）
plt.rcParams["axes.unicode_minus"] = False
# ===================== 配置项 =====================
nc_file_path = "ice_conc_nh_ease2-250_icdr-v3p0_202201011200.nc"  # 你的NC文件路径
output_img_path = "sea_ice_20220101.png"  # 输出图片路径（支持.png/.jpg/.bmp）
img_dpi = 300  # 图片分辨率（越高越清晰，300为印刷级）
# ==================================================

# 1. 检查文件是否存在
if not os.path.exists(nc_file_path):
    print(f"错误：找不到NC文件！路径：{os.path.abspath(nc_file_path)}")
    exit(1)

# 2. 读取NC数据
print("正在读取NC文件...")
ds = xr.open_dataset(nc_file_path)

# 提取核心数据（确认变量名与你的NC文件一致，不一致需修改）
lat = ds["lat"].values  # 纬度数组
lon = ds["lon"].values  # 经度数组
ice_conc = ds["ice_conc"].values[0]  # 海冰密集度（取第一个时间维度）

# 处理无效值（将-9999/NaN替换为np.nan，绘图时会透明显示）
ice_conc = np.where((ice_conc < 0) | (ice_conc > 100), np.nan, ice_conc)

# 3. 设置绘图投影（北半球极地立体投影，适配海冰数据）
print("正在绘制图片...")
fig = plt.figure(figsize=(10, 10), dpi=img_dpi)  # 画布大小：10x10英寸
# 北半球极地立体投影（中心经度0°，纬度60°N以上）
ax = plt.axes(projection=ccrs.NorthPolarStereo(central_longitude=0))
ax.set_extent([-180, 180, 60, 90], crs=ccrs.PlateCarree())  # 只显示60°N以北区域

# 4. 添加地图要素（关键：先加陆地，设置为黑色）
# 4.1 陆地填充为黑色（核心修改）
ax.add_feature(
    cfeature.LAND,
    facecolor="black",  # 陆地填充色：黑色
    edgecolor="black",  # 陆地边框色：黑色（可选，增强边界）
    alpha=1.0           # 陆地不透明
)
# 4.2 海岸线、国界线（在陆地之上，更清晰）
ax.add_feature(cfeature.COASTLINE, linewidth=0.5, color="white")  # 海岸线设为白色，对比黑色陆地
ax.add_feature(cfeature.BORDERS, linewidth=0.3, color="gray")
ax.gridlines(draw_labels=True, linewidth=0.5, color="gray", alpha=0.5)

# 5. 绘制海冰密集度热力图
# 配色方案：cmap选择冰蓝系（Blues_r），100%=白色，0%=深蓝
im = ax.pcolormesh(
    lon, lat, ice_conc,
    transform=ccrs.PlateCarree(),  # 原始数据的坐标系（WGS84）
    cmap="Blues_r",  # 配色方案（可改为viridis/coolwarm/Reds）
    vmin=0, vmax=100,  # 颜色值域（0-100%密集度）
    alpha=0.9  # 透明度
)

# 6. 添加颜色条（图例）
cbar = plt.colorbar(
    im, ax=ax, orientation="horizontal", pad=0.05, aspect=50, shrink=0.8
)
cbar.set_label("海冰密集度 (%)", fontsize=12, fontweight="bold")
cbar.ax.tick_params(labelsize=10)

# 7. 添加标题
plt.title(
    f"2022-01-01 北半球海冰密集度\n(OSI SAF ICDR v3.0)",
    fontsize=14, fontweight="bold", pad=20
)

# 8. 保存图片（去除白边，提高清晰度）
plt.tight_layout()
plt.savefig(
    output_img_path,
    dpi=img_dpi,
    bbox_inches="tight",  # 去除画布白边
    pad_inches=0.1  # 少量内边距
)
plt.close()  # 关闭画布，释放内存

print(f"\n转换完成！")
print(f"输出图片：{os.path.abspath(output_img_path)}")
print(f"图片分辨率：{img_dpi} DPI")
print(f"可视化区域：60°N以北（北半球极地投影）")