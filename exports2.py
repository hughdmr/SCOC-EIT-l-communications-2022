import pandas as pd
import pickle as pkl
import shutil
pd.options.mode.chained_assignment = None  # default='warn'

annees = [2023, 2024, 2025, 2026, 2027]

annees_update = pkl.load(open("annees_update.p", "rb"))
combis_a_installer = pkl.load(open("combis_a_installer.p", "rb"))
dic_rho = pkl.load(open("dic_rho.p", "rb"))
previsions = pkl.load(open("previsions.p", "rb"))
rho = pkl.load(open("rho.p", "rb"))

# print(combis_a_installer)
# print(annees_update)
print(dic_rho)

annee_et_ajout = {}

for annee in annees:
    annee_et_ajout[annee] = []
    sites = list(annees_update.keys())
    for site in sites:
        if annees_update[site] == annee:
            annee_et_ajout[annee].append([site, combis_a_installer[site+"A"]])

for annee in annees:
    if annee == 2023:
        df2 = pd.read_csv("exports/initialement.csv")
        L = annee_et_ajout[annee]
        for k in range(len(L)):
            a = list(df2['site'])
            ind = a.index(L[k][0])
            sect1 = str((L[k][0]) + "A")
            sect2 = str((L[k][0]) + "B")
            sect3 = str((L[k][0]) + "C")
            if sect1 in list(df2['secteur']):
                for freq in L[k][1]:
                    if freq == "3500 MHz":
                        df2[freq][ind] = "5G"
                    else:
                        df2[freq][ind] = "4G"
                df2['debit_prevu'][ind] = previsions[sect1][annee]
                if dic_rho[sect1][annee] > rho:
                    sature = 1
                else:
                    sature = 0
                df2['sature'][ind] = sature
            if sect2 in list(df2['secteur']):
                for freq in L[k][1]:
                    if freq == "3500 MHz":
                        df2[freq][ind+1] = "5G"
                    else:
                        df2[freq][ind+1] = "4G"
                df2['debit_prevu'][ind+1] = previsions[sect2][annee]
                if dic_rho[sect2][annee] > rho:
                    sature = 1
                else:
                    sature = 0
                df2['sature'][ind+1] = sature
            if sect3 in list(df2['secteur']):
                for freq in L[k][1]:
                    if freq == "3500 MHz":
                        df2[freq][ind+2] = "5G"
                    else:
                        df2[freq][ind+2] = "4G"
                df2['debit_prevu'][ind+3] = previsions[sect3][annee]
                if dic_rho[sect3][annee] > rho:
                    sature = 1
                else:
                    sature = 0
                df2['sature'][ind+2] = sature
        df2.to_csv('exports/export_2023.csv')
    if annee != 2023:
        shutil.copyfile("exports/export_"+str((annee-1))+".csv",
                        "exports/export_"+str(annee)+".csv")
        df3 = pd.read_csv("exports/export_"+str(annee)+".csv")
        secteurs = list(dic_rho.keys())
        b = list(df3['secteur'])
        for secteur in secteurs:
            inde = b.index(secteur)
            if dic_rho[secteur][annee] > rho:
                sature = 1
            else:
                sature = 0
            df3['sature'][inde] = sature
            df3['debit_prevu'][inde] = previsions[secteur][annee]
            df3['rho'][inde] = dic_rho[secteur][annee]
        L = annee_et_ajout[annee]
        for k in range(len(L)):
            a = list(df3['site'])
            ind = a.index(L[k][0])
            sect1 = str((L[k][0]) + "A")
            sect2 = str((L[k][0]) + "B")
            sect3 = str((L[k][0]) + "C")
            if sect1 in list(df2['secteur']):
                for freq in L[k][1]:
                    if freq == "3500 MHz":
                        df3[freq][ind] = "5G"
                    else:
                        df3[freq][ind] = "4G"
            if sect2 in list(df2['secteur']):
                for freq in L[k][1]:
                    if freq == "3500 MHz":
                        df3[freq][ind+1] = "5G"
                    else:
                        df3[freq][ind+1] = "4G"
            if sect3 in list(df2['secteur']):
                for freq in L[k][1]:
                    if freq == "3500 MHz":
                        df3[freq][ind+2] = "5G"
                    else:
                        df3[freq][ind+2] = "4G"
        df3.to_csv('exports/export_'+str(annee)+'.csv')
