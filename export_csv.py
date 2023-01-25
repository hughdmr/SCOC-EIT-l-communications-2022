import csv
import pickle as pkl

annee=2023
dic_rho=pkl.load(open("dic_rho.p", "rb"))
rho=pkl.load(open("rho.p", "rb"))
etats=pkl.load(open("etats.p","rb"))
previsions=pkl.load(open("previsions.p", "rb"))
rho=1

with open("exports/export_{}.csv".format(annee), 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    # colonnes
    writer.writerow(('secteur', 'site', 'debit_prevu','sature',"700 MHz", "800 MHz", "1800 MHz", "2100 MHz", "2600 MHz", "3500 MHz"))
    # lignes
    for secteur in etats:
        if dic_rho[secteur][annee]>rho:
            sature = 1
        else:
            sature=0
        etat=[]
        freq = ["700 MHz", "800 MHz", "1800 MHz", "2100 MHz", "2600 MHz", "3500 MHz"]
        for i in range(len(freq)):
            if etats[secteur][freq[i]]:
                etat.append(1)
            else:
                etat.append(0)

        writer.writerow((secteur, secteur[0:6],previsions[secteur][annee], sature, etat[0], etat[1], etat[2],etat[3],etat[4],etat[5]))

