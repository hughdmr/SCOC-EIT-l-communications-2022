import pandas as pd
import pickle as pkl
import shutil
import csv
pd.options.mode.chained_assignment = None  # default='warn'

annees = [2023, 2024, 2025, 2026, 2027]

annees_update = pkl.load(open("annees_update.p", "rb"))
combis_a_installer = pkl.load(open("combis_a_installer.p", "rb"))
dic_rho = pkl.load(open("dic_rho.p", "rb"))
previsions = pkl.load(open("previsions.p", "rb"))
rho = pkl.load(open("rho.p", "rb"))

# print(combis_a_installer)
print(annees_update)
# print(dic_rho)


# Partie de François

annee_et_ajout = {}

for annee in annees:
    annee_et_ajout[annee] = []
    sites = list(annees_update.keys())
    for site in sites:
        if annees_update[site] == annee:
            annee_et_ajout[annee].append([site, combis_a_installer[site+"A"]])

with open("csv_changements/changes.csv", 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    df4 = pd.read_csv("exports/initialement.csv")
    sites = list(df4['site'])
    # colonnes
    writer.writerow(('annee', 'site', 'X lambert', 'Y lambert', "700 MHz",
                    "800 MHz", "1800 MHz", "2100 MHz", "2600 MHz", "3500 MHz"))
    for annee in list(annee_et_ajout.keys()):
        for k in range(len(annee_et_ajout[annee])):
            site = annee_et_ajout[annee][k][0]
            a = sites.index(site)
            X = df4['X lambert'][a]
            Y = df4['Y lambert'][a]
            ajouts_bande = [0, 0, 0, 0, 0, 0]
            bandes = annee_et_ajout[annee][k][1]
            if ("700 MHz 4G" in bandes):
                ajouts_bande[0] = "4G"
            if ("700 MHz update" in bandes):
                ajouts_bande[0] = "p"
            if ("700 MHz 5G" in bandes):
                ajouts_bande[0] = "5G"
            if ("800 MHz 4G" in bandes):
                ajouts_bande[1] = "4G"
            if ("800 MHz update" in bandes):
                ajouts_bande[1] = "p"
            if ("800 MHz 5G" in bandes):
                ajouts_bande[1] = "5G"
            if ("1800 MHz 4G" in bandes):
                ajouts_bande[2] = "4G"
            if ("1800 MHz update" in bandes):
                ajouts_bande[2] = "p"
            if ("1800 MHz 5G" in bandes):
                ajouts_bande[2] = "5G"
            if ("2100 MHz 4G" in bandes):
                ajouts_bande[3] = "4G"
            if ("2100 MHz update" in bandes):
                ajouts_bande[3] = "p"
            if ("2100 MHz 5G" in bandes):
                ajouts_bande[3] = "5G"
            if ("2600 MHz 4G" in bandes):
                ajouts_bande[4] = "4G"
            if ("2600 MHz update" in bandes):
                ajouts_bande[4] = "p"
            if ("2600 MHz 5G" in bandes):
                ajouts_bande[4] = "5G"
            if ("3500 MHz" in bandes):
                ajouts_bande[5] = "5G"
            writer.writerow((annee, site, X, Y, ajouts_bande[0], ajouts_bande[1],
                            ajouts_bande[2], ajouts_bande[3], ajouts_bande[4], ajouts_bande[5]))


largeurs = {
    "700 MHz 4G": 5*10**6,
    "700 MHz update": 0.2*5*10**6,
    "700 MHz 5G": 1.2*5*10**6,
    "800 MHz 4G": 10*10**6,
    "800 MHz update": 0.2*10*10**6,
    "800 MHz 5G": 1.2*5*10**6,
    "1800 MHz 4G": 20*10**6,
    "1800 MHz update": 0.2*20*10**6,
    "1800 MHz 5G": 1.2*5*10**6,
    "2100 MHz 4G": 15*10**6,
    "2100 MHz update": 0.2*15*10**6,
    "2100 MHz 5G": 1.2*15*10**6,
    "2600 MHz 4G": 15*10**6,
    "2600 MHz update": 0.2*15*10**6,
    "2600 MHz 5G": 1.2*15*10**6,
    "3500 MHz": 70*10**6}

ajout_4G = ['700 MHz 4G', "800 MHz 4G",
            "1800 MHz 4G", "2100 MHz 4G", "2600 MHz 4G"]
ajout_5G = list(largeurs.keys())
for i in range(len(ajout_4G)):
    ajout_5G.remove(ajout_4G[i])
# print(ajout_5G)
# print(annee_et_ajout[2027])

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
                    pos_z = freq.index("z")
                    if freq in ajout_5G:
                        df2[freq[0:pos_z+1]][ind] = "5G"
                    else:
                        df2[freq[0:pos_z+1]][ind] = "4G"
                df2['debit_prevu'][ind] = previsions[sect1][annee]
                if dic_rho[sect1][annee] > rho:
                    sature = 1
                else:
                    sature = 0
                df2['sature'][ind] = sature
            if sect2 in list(df2['secteur']):
                for freq in L[k][1]:
                    pos_z = freq.index("z")
                    if freq in ajout_5G:
                        df2[freq[0:pos_z+1]][ind+1] = "5G"
                    else:
                        df2[freq[0:pos_z+1]][ind+1] = "4G"
                df2['debit_prevu'][ind+1] = previsions[sect2][annee]
                if dic_rho[sect2][annee] > rho:
                    sature = 1
                else:
                    sature = 0
                df2['sature'][ind+1] = sature
            if sect3 in list(df2['secteur']):
                for freq in L[k][1]:
                    pos_z = freq.index("z")
                    if freq in ajout_5G:
                        df2[freq[0:pos_z+1]][ind+2] = "5G"
                    else:
                        df2[freq[0:pos_z+1]][ind+2] = "4G"
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
        df3 = pd.read_csv("exports/export_"+str(annee)+".csv", index_col=0)
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
                    pos_z = freq.index("z")
                    if freq in ajout_5G:
                        df3[freq[0:pos_z+1]][ind] = "5G"
                    else:
                        df3[freq[0:pos_z+1]][ind] = "4G"
            if sect2 in list(df2['secteur']):
                for freq in L[k][1]:
                    pos_z = freq.index("z")
                    if freq in ajout_5G:
                        df3[freq[0:pos_z+1]][ind+1] = "5G"
                    else:
                        df3[freq[0:pos_z+1]][ind+1] = "4G"
            if sect3 in list(df2['secteur']):
                for freq in L[k][1]:
                    pos_z = freq.index("z")
                    if freq == "3500 MHz":
                        df3[freq[0:pos_z+1]][ind+2] = "5G"
                    else:
                        df3[freq[0:pos_z+1]][ind+2] = "4G"
        df3.to_csv('exports/export_'+str(annee)+'.csv')


# Recalcul des rho par annee en prenant en compte les ajouts

largeurs = {
    "700 MHz": 5*10**6,
    "800 MHz": 10*10**6,
    "1800 MHz": 20*10**6,
    "2100 MHz": 15*10**6,
    "2600 MHz": 15*10**6,
    "3500 MHz": 70*10**6
}

rho_par_annee = {}

for annee in annees:
    data = pd.read_csv("exports/export_{}.csv".format(annee), delimiter=",")
    data_secteurs = data["secteur"]
    etats = {}
    for i in range(len(data_secteurs)):
        etats[data_secteurs[i]] = {}
        for freq in ["700 MHz", "800 MHz", "1800 MHz", "2100 MHz", "2600 MHz", "3500 MHz"]:
            if data[freq][i] == "0":
                etats[data_secteurs[i]][freq] = 0
            elif data[freq][i] == "4G":
                etats[data_secteurs[i]][freq] = 1
            else:
                etats[data_secteurs[i]][freq] = 1.2

    # print(etats["T70725A"])

    capacites_actuelles = {}
    for secteur in etats:
        length = 0
        for freq in ["700 MHz", "800 MHz", "1800 MHz", "2100 MHz", "2600 MHz", "3500 MHz"]:
            length += (largeurs[freq]*etats[secteur][freq])
        capacites_actuelles[secteur] = 1.43*length

    # print(capacites_actuelles["T70725A"])

    rho_actuels = {}
    for secteur in previsions.keys():
        rho_actuels[secteur] = previsions[secteur][annee] / \
            (capacites_actuelles[secteur]/10**6)
        (capacites_actuelles[secteur]/10**6)

    rho_par_annee[annee] = rho_actuels

for annee in annees:
    df5 = pd.read_csv("exports/export_" + str(annee)+".csv", index_col=0)
    a = list(df5["secteur"])
    rhos = rho_par_annee[annee]
    secteurs = list(rhos.keys())
    values = [0]*(len(rhos.keys()))
    for j in range(len(values)):
        indexs = a.index(secteurs[j])
        values[indexs] = rhos[secteurs[j]]
    df5.insert(7, "rho_avec_chg", values)
    df5.to_csv("exports/export_" + str(annee)+".csv",)

sect_tj_sat = []
df6 = pd.read_csv("exports/export_2027.csv")
for i in range(len(df6['rho_avec_chg'])):
    if df6['rho_avec_chg'][i] > rho:
        sect_tj_sat.append(df6['secteur'][i])

print(sect_tj_sat)
