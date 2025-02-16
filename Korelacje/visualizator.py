import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from DataTeam.utils import dane_mapa_polski, dane_poparcie_polityczne, dane_przyrost_naturalny


class MapaPolski:
    def __init__(self, shp_path, pop_path, przyrost_path, partia):
        """
        Inicjalizacja klasy.

        :param shp_path: Ścieżka do pliku .shp (mapa granic gmin/powiatów)
        :param pop_path: Ścieżka do pliku Excel z danymi o poparciu politycznym
        :param przyrost_path: Ścieżka do pliku Excel z danymi o przyroście naturalnym
        """
        self.shp_path = shp_path
        self.pop_path = pop_path
        self.przyrost_path = przyrost_path
        self.mapa = gpd.read_file(shp_path)
        self.partia = partia

    def map_poparcie(self):
        """
        Tworzy mapę z podziałem według poparcia politycznego dla wybranej partii.

        Parametr 'partia' (string, case-insensitive) może przyjmować następujące wartości:
         - "KO"              : kolumna o indeksie 17
         - "konfederacja"    : kolumna o indeksie 16
         - "Nowa Lewica"     : kolumna o indeksie 14
         - "PiS"             : kolumna o indeksie 15
         - "Trzecia Droga"   : kolumna o indeksie 13

        """
        # Mapa przyporządkowania partii do indeksu kolumny
        column_mapping = {
            "ko": 17,
            "konfederacja": 16,
            "nowa lewica": 14,
            "pis": 15,
            "trzecia droga": 13
        }
        key = self.partia.lower()
        if key not in column_mapping:
            raise ValueError(
                f"Nieznana partia: {self.partia}. Dostępne opcje: KO, konfederacja, Nowa Lewica, PiS, Trzecia Droga.")
        col_index = column_mapping[key]

        # Wczytanie danych o poparciu politycznym
        pop_df = pd.read_excel(self.pop_path, dtype={'JPT_KOD_JE': str})
        # Wybieramy pierwszą kolumnę z kodem oraz wybraną kolumnę z danymi o poparciu
        pop_df = pop_df.iloc[:, [0, col_index]]
        pop_df.columns = ['JPT_KOD_JE', 'Poparcie polityczne']

        # Ujednolicenie formatu kodów (dodanie zer wiodących)
        pop_df['JPT_KOD_JE'] = pop_df['JPT_KOD_JE'].astype(str).str.zfill(4)
        self.mapa['JPT_KOD_JE'] = self.mapa['JPT_KOD_JE'].astype(str).str.zfill(4)

        # Zamiana przecinka na kropkę oraz konwersja do wartości numerycznych
        pop_df['Poparcie polityczne'] = pop_df['Poparcie polityczne'].astype(str).str.replace(',', '.', regex=False)
        pop_df['Poparcie polityczne'] = pd.to_numeric(pop_df['Poparcie polityczne'], errors='coerce')

        # Scalanie danych z mapą
        gdf = self.mapa.merge(pop_df, on='JPT_KOD_JE', how='left')

        # Definicja przedziałów – od 0 do 60, 12 przedziałów
        bins = np.linspace(0, 60, 13)
        labels = ['0 do 5', '5 do 10', '10 do 15', '15 do 20', '20 do 25', '25 do 30',
                  '30 do 35', '35 do 40', '40 do 45', '45 do 50', '50 do 55', '55 do 60']
        gdf['Poparcie polityczne przedziały'] = pd.cut(gdf['Poparcie polityczne'], bins=bins, labels=labels)

        # Rysowanie mapy
        fig, ax = plt.subplots(figsize=(12, 12))
        gdf.plot(column='Poparcie polityczne przedziały', ax=ax, legend=True,
                 cmap='coolwarm',
                 legend_kwds={'title': f"Poparcie polityczne ({self.partia}) w %",
                              'bbox_to_anchor': (1, 0.5),
                              'loc': 'center left',
                              'borderpad': 1})
        plt.title(f"Mapa poparcia politycznego dla {self.partia}, 2023")
        plt.show()

    def map_przyrost(self):
        """Tworzy mapę z podziałem według przyrostu naturalnego."""
        # Wczytanie danych o przyroście naturalnym
        przy_df = pd.read_excel(self.przyrost_path)
        # Zakładamy, że dane zaczynają się od 10-tego wiersza, a interesujące nas kolumny to indeksy 1 oraz 18
        przy_df = przy_df.iloc[9:, [1, 18]]
        przy_df.columns = ['JPT_KOD_JE', 'Przyrost naturalny']

        # Ujednolicenie formatu kodów
        przy_df['JPT_KOD_JE'] = przy_df['JPT_KOD_JE'].astype(str).str.zfill(4)
        self.mapa['JPT_KOD_JE'] = self.mapa['JPT_KOD_JE'].astype(str).str.zfill(4)

        # Konwersja do wartości numerycznych
        przy_df['Przyrost naturalny'] = pd.to_numeric(przy_df['Przyrost naturalny'], errors='coerce')

        # Scalanie danych z mapą
        gdf = self.mapa.merge(przy_df, on='JPT_KOD_JE', how='left')

        # Definicja przedziałów – tutaj używamy przedziałów z wartościami skrajnymi
        bins = [-np.inf, -20, -15, -13, -10, -8, -5, -3, -1, 0, 1, 2, 3, 4, 5, 7, 8, 9, 11, 12, np.inf]
        labels = ['<-20', '-20 do -15', '-15 do -13', '-13 do -10', '-10 do -8', '-8 do -5',
                  '-5 do -3', '-3 do -1', '-1 do 0', '0 do 1', '1 do 2', '2 do 3',
                  '3 do 4', '4 do 5', '5 do 7', '7 do 8', '8 do 9', '9 do 11', '11 do 12', '>12']
        gdf['Przyrost naturalny przedział'] = pd.cut(gdf['Przyrost naturalny'], bins=bins, labels=labels)

        # Rysowanie mapy
        fig, ax = plt.subplots(figsize=(12, 12))
        gdf.plot(column='Przyrost naturalny przedział', ax=ax, legend=True, cmap='coolwarm',
                 legend_kwds={'title': "Przyrost naturalny\nna 1000 mieszkańców",
                              'bbox_to_anchor': (1, 0.5),
                              'loc': 'center left',
                              'borderpad': 1})
        plt.title("Mapa przyrostu naturalnego w gminach, rok 2023")
        plt.show()

    def mapa_korelacja(self):
        """
        Tworzy mapę korelacji między przyrostem naturalnym a poparciem politycznym.

        Argumenty:
        - partia (str): Nazwa partii, możliwe opcje:
            - "KO" -> kolumna 17
            - "Konfederacja" -> kolumna 16
            - "Nowa Lewica" -> kolumna 14
            - "PiS" -> kolumna 15
            - "Trzecia Droga" -> kolumna 13
        """
        # Mapowanie partii na indeksy kolumn
        kolumny_partii = {
            "ko": 17,
            "konfederacja": 16,
            "nowa lewica": 14,
            "pis": 15,
            "trzecia droga": 13
        }
        key = self.partia.lower()
        if key not in kolumny_partii:
            raise ValueError("Niepoprawna nazwa partii. Wybierz jedną z: " + ", ".join(kolumny_partii.keys()))

        # Wczytanie danych
        poparcie_polityczne = pd.read_excel(self.pop_path, dtype={'JPT_KOD_JE': str})
        mapa_polski = gpd.read_file(self.shp_path)
        przyrost_naturalny = pd.read_excel(self.przyrost_path)

        # Przetworzenie danych
        poparcie_polityczne = poparcie_polityczne.iloc[:, [0, kolumny_partii[self.partia]]]
        poparcie_polityczne.columns = ['JPT_KOD_JE', 'Poparcie polityczne']
        poparcie_polityczne['JPT_KOD_JE'] = poparcie_polityczne['JPT_KOD_JE'].astype(str).str.zfill(4)
        poparcie_polityczne['Poparcie polityczne'] = poparcie_polityczne['Poparcie polityczne'].str.replace(',', '.',
                                                                                                            regex=False)
        poparcie_polityczne['Poparcie polityczne'] = pd.to_numeric(poparcie_polityczne['Poparcie polityczne'],
                                                                   errors='coerce')

        przyrost_naturalny = przyrost_naturalny.iloc[9:, [1, 18]]
        przyrost_naturalny.columns = ['JPT_KOD_JE', 'Przyrost naturalny']
        przyrost_naturalny['JPT_KOD_JE'] = przyrost_naturalny['JPT_KOD_JE'].astype(str)
        przyrost_naturalny['Przyrost naturalny'] = pd.to_numeric(przyrost_naturalny['Przyrost naturalny'],
                                                                 errors='coerce')

        # Połączenie danych
        zestaw_danych = poparcie_polityczne.merge(przyrost_naturalny, on='JPT_KOD_JE', how='left')
        mapa_danych = mapa_polski.merge(zestaw_danych, on='JPT_KOD_JE', how='left')

        # Obliczenie korelacji
        mapa_danych['Korelacja'] = mapa_danych['Poparcie polityczne'] * mapa_danych['Przyrost naturalny']

        # Normalizacja wartości korelacji do zakresu -100 do 100
        mapa_danych['Korelacja'] = 200 * (mapa_danych['Korelacja'] - mapa_danych['Korelacja'].min()) / (
                    mapa_danych['Korelacja'].max() - mapa_danych['Korelacja'].min()) - 100

        # Tworzenie mapy korelacji
        fig, ax = plt.subplots(figsize=(12, 12))
        mapa_danych.plot(column='Korelacja', ax=ax, legend=True, cmap='coolwarm',
                         legend_kwds={'label': "Siła korelacji (-100 do 100)"}, edgecolor="black")

        # Dodanie tytułu i etykiet osi
        plt.title(f"Mapa Korelacji: {self.partia} vs. Przyrost naturalny")
        ax.set_xlabel("Długość geograficzna")
        ax.set_ylabel("Szerokość geograficzna")

        plt.show()


if __name__ == "__main__":

    mapa = MapaPolski(dane_mapa_polski, dane_poparcie_polityczne, dane_przyrost_naturalny, "ko")

    # Wywołanie metody tworzącej mapę poparcia politycznego dla konkretnej partii
    mapa.map_poparcie()  # lub "konfederacja", "Nowa Lewica", "PiS", "Trzecia Droga"

    # Wywołanie metody tworzącej mapę przyrostu naturalnego
    mapa.map_przyrost()

    # Wywołanie metody tworzącej mapę korelacji
    mapa.mapa_korelacja()
