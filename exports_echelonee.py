import csv
import pickle as pkl
import pandas as pd

df = pd.read_csv("secteurs.csv")
dic_rho = pkl.load(open("dic_rho.p", "rb"))
rho = pkl.load(open("rho.p", "rb"))
etats = pkl.load(open("etats.p", "rb"))
previsions = pkl.load(open("previsions.p", "rb"))
config = pkl.load(open("config_echelonee", 'rb'))


print(config)

for annee in [2023, 2024, 2025, 2026, 2027]:
    count = 0
    with open("export2/export_{}.csv".format(annee), 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # colonnes
        writer.writerow(('secteur', 'site', 'X lambert', 'Y lambert', 'debit_prevu', 'sature', 'rho', "700 MHz",
                        "800 MHz", "1800 MHz", "2100 MHz", "2600 MHz", "3500 MHz"))
        # lignes
        for secteur in list(config[annee].keys()):
            if dic_rho[secteur][annee] > rho:
                sature = 1
            else:
                sature = 0
            etat = [0]*6
            freq = ["700 MHz", "800 MHz", "1800 MHz",
                    "2100 MHz", "2600 MHz", "3500 MHz"]
            for frequence in list(config[annee][secteur].keys()):
                if config[annee][secteur][frequence]:
                    pos_z = frequence.index("z")
                    freq_reduite = frequence[0:pos_z+1]
                    indexation = freq.index(freq_reduite)
                    if frequence == freq_reduite + " 4G":
                        etat[indexation] = "4G"
                    elif frequence == freq_reduite + " 5G":
                        etat[indexation] = "5G"
                    elif frequence == freq_reduite + " update":
                        etat[indexation] = "5G"
                    else:
                        etat[indexation] = "5G"
                else:
                    etat.append(0)
            X = df["X (lambert 2 étendu)"][count]
            Y = df["Y (Lambert 2  étendu)"][count]
            count += 1
            writer.writerow((secteur, secteur[0:6], X, Y, previsions[secteur][annee],
                            sature, dic_rho[secteur][annee], etat[0], etat[1], etat[2], etat[3], etat[4], etat[5]))
