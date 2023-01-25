'''Première version de dimensionnement_complet.py, qui ne prenanit en compte la 5G que dans la bande 3500 MHz'''

import pickle as pkl
import datetime

coeffs_secteurs = pkl.load(open("coeffs.p", "rb"))
capacites_secteurs = pkl.load(open("capacites.p", "rb"))
etats_secteurs = pkl.load(open("etats.p", "rb"))


x_debut = "2017-06-19"

# Prévisions de 2024 à 2027

previsions = {}

for secteur in coeffs_secteurs.keys():
    a = coeffs_secteurs[secteur][0][0]
    b = coeffs_secteurs[secteur][0][1]

    def prediction(date_pred):
        date_pred = datetime.date.fromisoformat(date_pred)
        date_pred_days = (date_pred-datetime.date.fromisoformat(x_debut)).days
        trafic_pred = a*date_pred_days + b
        return trafic_pred

    previsions[secteur] = {
        2023: prediction("2023-01-01"),
        2024: prediction("2024-01-01"),
        2025: prediction("2025-01-01"),
        2026: prediction("2026-01-01"),
        2027: prediction("2027-01-01")
    }

# print(previsions)

rho = 0.8  # choix arbitraire de charge de la cellule

dic_rho = {}
annees = [2023, 2024, 2025, 2026, 2027]

for secteur in previsions.keys():
    dic_rho[secteur] = {}
    for annee in annees:
        dic_rho[secteur][annee] = previsions[secteur][annee] / \
            (capacites_secteurs[secteur]/10**6)

# print(dic_rho)

pkl.dump(dic_rho, open("dic_rho.p", "wb"))

# identification des ajouts

ajouts = {}

# Identification des secteurs devant évoluer, en quelle année et à quel point

for secteur in dic_rho.keys():
    for annee in annees:
        if secteur not in ajouts.keys():
            if dic_rho[secteur][annee] > rho:
                ajouts[secteur] = {
                    "annee": annee,
                    "rho 2027": dic_rho[secteur][2027],
                    "besoin de debit" : previsions[secteur][2027]/rho - capacites_secteurs[secteur]/10**6
                }

# print(ajouts)

## Recherche des évolutions possibles

largeurs = {
    "700 MHz" : 5*10**6,
    "800 MHz" : 10*10**6,
    "1800 MHz" : 20*10**6,
    "2100 MHz" : 15*10**6,
    "2600 MHz" : 15*10**6,
    "3500 MHz" : 70*10**6
}

# Enumérer pour chaque secteur les antennes non encore présentes

bandes_dispos = {}

for secteur in ajouts.keys():
    bandes_dispos[secteur]=[]
    for freq in largeurs.keys():
        if not etats_secteurs[secteur][freq]:
            bandes_dispos[secteur].append(freq)

# print(bandes_dispos)

# Enumérer les combinaisons, sans discrimination sur le débit apporté

def all_combis(candidates):
    combis=[]
    n = len(candidates)
    for i in range(2**n):
        combi = []
        for j in range(n):
            if i & 2**j != 0:
                combi.append(candidates[j])
        combis.append(combi)
    return combis

# print(all_combis(list(largeurs.keys())))

# Pour une combinaison, vérifier qu'elle fonctionne pour augmenter le débit

def combi_valable(combi, debit):
    length=0
    for freq in combi:
        length += largeurs[freq]/10**6
    return (length*1.43 >= debit)

# Pour une combinaison donnée, calculer le coût d'installation

freq_prix = {
    "700 MHz" : 7000,
    "800 MHz" : 10000,
    "1800 MHz" : 14000,
    "2100 MHz" : 12000,
    "2600 MHz" : 12000,
    "3500 MHz" : 35000
}

def combi_prix(combi):
    prix = 0
    for freq in combi:
        prix += freq_prix[freq]
    return prix

# Application aux secteurs

combis_choisies = {}

for secteur in bandes_dispos.keys():
    combis_choisies[secteur]= {}
    candidates = bandes_dispos[secteur]
    combis_possibles = all_combis(candidates)
    debit = ajouts[secteur]["besoin de debit"]

    combis_valables = []
    for combi in combis_possibles:
        if combi != []:
            if combi_valable(combi,debit):
                combis_valables.append(combi)
    if combis_valables == []:
        combis_choisies[secteur]["choix"] = "Aucune combinaison ne convient"
    else:
        choix = min(combis_valables, key=lambda s: combi_prix(s))
        combis_choisies[secteur]["choix"] = choix
        combis_choisies[secteur]["prix"] = combi_prix(choix)

print(combis_choisies)