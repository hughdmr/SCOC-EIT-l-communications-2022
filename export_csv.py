import csv
import pickle as pkl
import pandas as pd

annee = 2023
df = pd.read_csv("secteurs.csv")
dic_rho = pkl.load(open("dic_rho.p", "rb"))
rho = pkl.load(open("rho.p", "rb"))
etats = pkl.load(open("etats.p", "rb"))
previsions = pkl.load(open("previsions.p", "rb"))

count = 0
with open("exports/initialement.csv".format(annee), 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    # colonnes
    writer.writerow(('secteur', 'site', 'X lambert', 'Y lambert', 'debit_prevu', 'sature', 'rho', "700 MHz",
                    "800 MHz", "1800 MHz", "2100 MHz", "2600 MHz", "3500 MHz"))
    # lignes
    for secteur in etats:
        if dic_rho[secteur][annee] > rho:
            sature = 1
        else:
            sature = 0
        etat = []
        freq = ["700 MHz", "800 MHz", "1800 MHz",
                "2100 MHz", "2600 MHz", "3500 MHz"]
        for i in range(len(freq)-1):
            if etats[secteur][freq[i]]:
                etat.append("4G")
            else:
                etat.append(0)
        if etats[secteur]["3500 MHz"]:
            etat.append("5G")
        else:
            etat.append(0)
        X = df["X (lambert 2 étendu)"][count]
        Y = df["Y (Lambert 2  étendu)"][count]
        count += 1
        writer.writerow((secteur, secteur[0:6], X, Y, previsions[secteur][annee],
                        sature, dic_rho[secteur][annee], etat[0], etat[1], etat[2], etat[3], etat[4], etat[5]))
