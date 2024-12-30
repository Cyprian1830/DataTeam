import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

gminy_shp = gpd.read_file("C:\\Users\\cypri\\Desktop\\Python_projects\\PrzyrostNaturalny_Polityka\\A02_Granice_powiatow.shp")
print(gminy_shp.head())

fig, ax = plt.subplots(figsize=(10, 10))
gminy_shp.boundary.plot(ax=ax, color='black', linewidth=1)
plt.show()