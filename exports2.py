import pandas as pd
import pickle as pkl

annees = [2024, 2025, 2026, 2027]

annees_update = pkl.load(open("annees_update.p","rb"))

combis_a_installer = pkl.load(open("combis_a_installer.p","rb"))

print(combis_a_installer)
print(annees_update)
print(len(combis_a_installer))
print(len(annees_update))