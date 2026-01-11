import xarray as xr
import pandas as pd
import geojson
import os

# 1. 配置文件路径（替换为你的nc文件实际路径）
nc_file_path = "ice_conc_nh_ease2-250_icdr-v3p0_202201011200.nc"
output_geojson_path = "sea_ice_20220101.geojson"
if not os.path.exists(nc_file_path):
    print(f"错误：找不到指定的NetCDF文件！")
# 2. 读取NetCDF文件（提取核心字段：经纬度、海冰密集度）
print("正在读取NetCDF文件...")
ds = xr.open_dataset(nc_file_path)

# 注意：不同版本的OSI SAF产品变量名可能略有差异，该文件的变量名通常为：
# - 纬度：lat
# - 经度：lon
# - 海冰密集度：ice_conc（取值范围0-100，-9999为无效值）
lat = ds["lat"].values  # 二维数组（格网纬度）
lon = ds["lon"].values  # 二维数组（格网经度）
ice_conc = ds["ice_conc"].values[0]  # 取第一个时间维度的海冰密集度数据


# 3. 处理数据：展平格网+过滤无效值
print("正在处理数据...")
# 将二维格网展平为一维数组（对应每个格网点）
df = pd.DataFrame({
    "lat": lat.flatten(),
    "lon": lon.flatten(),
    "ice_concentration": ice_conc.flatten()
})

# 过滤无效值（OSI SAF中无效值通常为-9999或NaN）
df = df[(df["ice_concentration"] >= 0) & (df["ice_concentration"] <= 100)]

# # 可选：采样减少数据量（避免GeoJSON过大，Kepler加载卡顿）
# # 示例：每5个格网点取1个（步长越大，数据量越小）
# sample_step = 5
# df = df.iloc[::sample_step]


# 4. 转换为GeoJSON格式
print("正在转换为GeoJSON...")
features = []
for _, row in df.iterrows():
    # 每个格网点作为一个Point空间要素，属性包含海冰密集度
    feature = geojson.Feature(
        geometry=geojson.Point((row["lon"], row["lat"])),
        properties={
            "海冰密集度(%)": round(row["ice_concentration"], 2),
            "数据日期": "2022-01-01"  # 可根据文件名自动提取日期
        }
    )
    features.append(feature)

# 生成GeoJSON FeatureCollection
geojson_data = geojson.FeatureCollection(features)


# 5. 保存为GeoJSON文件
with open(output_geojson_path, "w", encoding="utf-8") as f:
    geojson.dump(geojson_data, f, ensure_ascii=False)

print(f"转换完成！GeoJSON文件已保存至：{os.path.abspath(output_geojson_path)}")
print(f"有效数据点数量：{len(features)}")