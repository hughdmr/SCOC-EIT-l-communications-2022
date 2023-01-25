import pandas as pd
import pickle as pkl

largeurs = {
    "700 MHz": 5*10**6,
    "800 MHz": 10*10**6,
    "1800 MHz": 20*10**6,
    "2100 MHz": 15*10**6,
    "2600 MHz": 15*10**6,
    "3500 MHz": 70*10**6
}

data = pd.read_csv("secteurs.csv", delimiter=",")
data_secteurs = data["Secteur"]

etat_secteurs = {}


for i in range(len(data_secteurs)):
    etat_secteurs[data_secteurs[i]] = {}
    for freq in ["700 MHz", "800 MHz", "1800 MHz", "2100 MHz", "2600 MHz", "3500 MHz"]:
        if data[freq][i] == "oui":
            etat_secteurs[data_secteurs[i]][freq] = True
        else:
            etat_secteurs[data_secteurs[i]][freq] = False

pkl.dump(etat_secteurs, open("etats.p", "wb"))

# print(etat_secteurs)

debits_ecoulables = {}

for secteur in etat_secteurs:
    length = 0
    for freq in ["700 MHz", "800 MHz", "1800 MHz", "2100 MHz", "2600 MHz"]:
        if etat_secteurs[secteur][freq]:
            length += largeurs[freq]
    if etat_secteurs[secteur]["3500 MHz"]:
        length += largeurs["3500 MHz"]*1.2
    debits_ecoulables[secteur] = 1.43*length

pkl.dump(debits_ecoulables, open("capacites.p", "wb"))

print(debits_ecoulables)
