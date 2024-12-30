import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

poparcie_polityczne = pd.read_excel("C:\\Users\\cypri\\Desktop\\Python_projects\\PrzyrostNaturalny_Polityka\\wyniki_gl_na_listy_po_powiatach_proc_sejm_utf8.xlsx", dtype={'JPT_KOD_JE': str})
mapa_polski = gpd.read_file("C:\\Users\\cypri\\Desktop\\Python_projects\\PrzyrostNaturalny_Polityka\\A02_Granice_powiatow.shp")
poparcie_polityczne = poparcie_polityczne.iloc[0:, [0, 17]]
poparcie_polityczne.columns = ['JPT_KOD_JE', 'Poparcie polityczne']
poparcie_polityczne['JPT_KOD_JE'] = sorted(poparcie_polityczne['JPT_KOD_JE'].astype(str).str.zfill(4))
mapa_polski['JPT_KOD_JE'] = sorted(mapa_polski['JPT_KOD_JE'])


poparcie_polityczne['Poparcie polityczne'] = poparcie_polityczne['Poparcie polityczne'].str.replace(',', '.', regex=False)

# Konwersja na wartości numeryczne
poparcie_polityczne['Poparcie polityczne'] = pd.to_numeric(poparcie_polityczne['Poparcie polityczne'], errors='coerce')

poparcie_polityczne['Poparcie polityczne'] = pd.to_numeric(poparcie_polityczne['Poparcie polityczne'])
gminy_joined = mapa_polski.merge(poparcie_polityczne, on='JPT_KOD_JE', how='left')

bins = np.linspace(0, 60, 13)
print(bins)

# Etykiety dla przedziałów
labels = ['0 do 5', '5 do 10', '10 do 15', '15 do 20', '20 do 25', '25 do 30',
          '30 do 35', '35 do 40', '40 do 45', '45 do 50', '50 do 55',
          '55 do 60']

# Przypisz kolumnę 'Poparcie polityczne' do przedziałów
gminy_joined['Poparcie polityczne przedziały'] = pd.cut(gminy_joined['Poparcie polityczne'], bins=bins, labels=labels)

# Wyświetl wynik
print(gminy_joined)

# Tworzenie wykresu
fig, ax = plt.subplots(figsize=(12, 12))

# Rysowanie mapy z odpowiednimi kolorami na podstawie przedziałów poparcia politycznego
gminy_joined.plot(column='Poparcie polityczne przedziały', ax=ax, legend=True,
                  cmap='coolwarm',  # Możesz zmienić mapę kolorów
                  legend_kwds={'title': "Poparcie polityczne w procentach", 'bbox_to_anchor': (1, 0.5),
                               'loc': 'center left', 'borderpad': 1})

# Dodanie tytułu do wykresu
plt.title("Mapa poparcia politycznego dla Koalicji Obywatelska, 2023")
plt.show()
