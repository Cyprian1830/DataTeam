import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


gminy_shp = gpd.read_file("C:\\Users\\cypri\\Desktop\\Python_projects\\"
                          "PrzyrostNaturalny_Polityka\\A02_Granice_powiatow.shp")

data = pd.read_excel("C:\\Users\\cypri\\Desktop\\Python_projects\\PrzyrostNaturalny_Polityka\\Tabela_III.xls")
data = data.iloc[9:, [1, 18]]
data.columns = ['JPT_KOD_JE', 'Przyrost naturalny']

# konwertuje dane z kodami terytorialnymi na typ string
data['JPT_KOD_JE'] = data['JPT_KOD_JE'].astype(str)

data['Przyrost naturalny'] = pd.to_numeric(data['Przyrost naturalny'], errors='coerce')
# Konwertuje wartości w kolumnie Przyrost naturalny na wartości numeryczne.
# Jeśli napotka jakiekolwiek błędy (np. puste lub nieprawidłowe dane),
# te wartości zostaną zamienione na NaN (Not a Number)

gminy_joined = gminy_shp.merge(data, on='JPT_KOD_JE', how='left')
# Łączy dane z pliku shapefile (gminy_shp) z danymi o przyroście naturalnym (data) na podstawie wspólnej
# kolumny JPT_KOD_JE.
# Używamy metody merge w Pandas, która jest podobna do operacji JOIN w bazach danych:
print(gminy_joined)

przyrost_naturalny = gminy_joined

bins = [-np.inf, -20, -15, -13, -10, -8, -5, -3, -1, 0, 1, 2, 3, 4, 5, 7, 8, 9, 11, 12, np.inf]
labels = ['<-20', '-20 do -15', '-15 do -13', '-13 do -10', '-10 do -8', '-8 to -5', '-5 do -3', '-3 do -1', '-1 do 0',
          '0 do 1', '1 do 2', '2 do 3', '3 do 4', '4 do 5', '5 do 7', '7 do 8', '8 do 9', '9 do 11', '11 do 12', '>12']
gminy_joined['Przyrost naturalny przedział'] = pd.cut(gminy_joined['Przyrost naturalny'], bins=bins, labels=labels)
# Funkcja ta służy do przypisania wartości z kolumny Przyrost naturalny do odpowiednich
# przedziałów zdefiniowanych w bins i oznaczenia ich etykietami z labels.
# Efektem jest nowa kolumna Przyrost naturalny przedział, która zawiera etykiety przedziałów.
print(gminy_joined)

fig, ax = plt.subplots(figsize=(12, 12))
gminy_joined.plot(column='Przyrost naturalny przedział', ax=ax, legend=True, cmap='coolwarm',
                  legend_kwds={'title': "Przyrost naturalny na 1000 mieszkańców", 'bbox_to_anchor': (1, 0.5),
                               'loc': 'center left', 'borderpad': 1})


plt.title("Mapa przyrostu naturalnego w powiatach, rok 2023")
plt.show()
