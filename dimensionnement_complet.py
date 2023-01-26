import pickle as pkl
import datetime
import matplotlib.pyplot as plt

coeffs_secteurs = pkl.load(open("coeffs.p", "rb"))
capacites_secteurs = pkl.load(open("capacites.p", "rb"))
# réportorie les fréquences dispo sur les différents secteurs
etats_secteurs = pkl.load(open("etats.p", "rb"))

x_debut = "2017-06-19"

# Prévisions de 2024 à 2027

previsions = {}  # dictionnaire <année>:<prediction de l’année>

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

pkl.dump(previsions, open("previsions.p", "wb"))

print(previsions)

rho = 0.8  # choix arbitraire de charge max de la cellule

pkl.dump(rho, open("rho.p", "wb"))

dic_rho = {}  # dictionnaire <secteur>:<charge du secteur>
annees = [2023, 2024, 2025, 2026, 2027]

for secteur in previsions.keys():
    dic_rho[secteur] = {}
    for annee in annees:
        dic_rho[secteur][annee] = previsions[secteur][annee] / \
            (capacites_secteurs[secteur]/10**6)

# liste des (<secteur de charge supérieure à rho>, <charge du secteur>)
sup = []
for secteur in dic_rho.keys():
    if dic_rho[secteur][2023] >= rho:
        sup.append((secteur, dic_rho[secteur][2023]))

# print(dic_rho)
# print(sup)

pkl.dump(dic_rho, open("dic_rho.p", "wb"))

# identification des ajouts

ajouts = {}  # dictionnair contenant les secteurs surchargés
# dictionnaire <secteur de charge sup à rho>:(dictionnaire {"annee","rho 2027","besoin de debit"})

# Identification des secteurs devant évoluer, en quelle année et à quel point

for secteur in dic_rho.keys():
    for annee in annees:
        if secteur not in ajouts.keys():
            if dic_rho[secteur][annee] > rho:
                ajouts[secteur] = {
                    "annee": annee,
                    "rho 2027": dic_rho[secteur][2027],
                    "besoin de debit": previsions[secteur][2027]/rho - capacites_secteurs[secteur]/10**6
                }

pkl.dump(ajouts, open("ajouts.p", "wb"))
# print(ajouts)

# Recherche des évolutions possibles

evolutions = ["700 MHz", "800 MHz", "1800 MHz", "2100 MHz", "2600 MHz"]

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
    "3500 MHz": 70*10**6
}

# Enumérer pour chaque secteur les antennes non encore présentes

bandes_dispos = {}

for secteur in ajouts.keys():
    bandes_dispos[secteur] = []
    for ajout in evolutions:
        # la fréquence est disponible sur ce secteur (en 4G)
        if etats_secteurs[secteur][ajout]:
            bandes_dispos[secteur].append(ajout+" update")
        else:  # la fréquence n’est pas dispo sur ce secteur
            bandes_dispos[secteur].append(ajout+" 4G")
            bandes_dispos[secteur].append(ajout+" 5G")
    # cette fréquence est uniquement en 5G
    if not etats_secteurs[secteur]["3500 MHz"]:
        bandes_dispos[secteur].append("3500 MHz")

# print(bandes_dispos)

# Enumérer les combinaisons, sans discrimination sur le débit apporté


def all_combis(candidates):
    combis = []
    n = len(candidates)
    for i in range(2**n):  # on parcourt toutes les combinaisons d’ajouts de fréquence
        combi = []
        for j in range(n):
            if i & 2**j != 0:
                combi.append(candidates[j])
        combis.append(combi)

    # Vérifier qu'on ne propose pas l'installation d'une bande 4G ET 5G pour une même fréquence
    combis_correctes = []
    for combi in combis:
        ajouter = True
        for freq in combi:
            if freq != "3500 MHz":
                pos_z = freq.index("z")
                if (freq[0:pos_z+1] + " 4G" in combi) and (freq[0:pos_z+1] + " 5G" in combi):
                    ajouter = False
        if ajouter:
            combis_correctes.append(combi)
    return combis_correctes

# print(all_combis(list(largeurs.keys())))

# Pour une combinaison, vérifier qu'elle fonctionne pour augmenter le débit


def combi_valable(combi, debit):
    length = 0
    for freq in combi:
        length += largeurs[freq]/10**6
    return (length*1.43 >= debit)

# Pour une combinaison donnée, calculer le coût d'installation


freq_prix = {
    "700 MHz 4G": 7000,
    "700 MHz update": 2000,
    "700 MHz 5G": 8000,
    "800 MHz 4G": 10000,
    "800 MHz update": 2000,
    "800 MHz 5G": 12000,
    "1800 MHz 4G": 14000,
    "1800 MHz update": 2000,
    "1800 MHz 5G": 14000,
    "2100 MHz 4G": 12000,
    "2100 MHz update": 2000,
    "2100 MHz 5G": 13500,
    "2600 MHz 4G": 12000,
    "2600 MHz update": 2000,
    "2600 MHz 5G": 13500,
    "3500 MHz": 35000
}


def combi_prix(combi):
    prix = 0
    for evolution in combi:
        prix += freq_prix[evolution]
    return prix

# Application aux secteurs


combis_choisies = {}

for secteur in bandes_dispos.keys():
    combis_choisies[secteur] = {}
    candidates = bandes_dispos[secteur]
    combis_possibles = all_combis(candidates)
    debit = ajouts[secteur]["besoin de debit"]

    combis_valables = []
    for combi in combis_possibles:
        if combi != []:
            if combi_valable(combi, debit):
                combis_valables.append(combi)
    if combis_valables == []:
        combis_choisies[secteur]["choix"] = "Aucune combinaison ne convient"
    else:
        choix = min(combis_valables, key=lambda c: combi_prix(c))
        combis_choisies[secteur]["choix"] = choix
        length = 0
        for freq in combi:
            length += largeurs[freq]/10**6
        combis_choisies[secteur]["bande ajoutee"] = length

# print(combis_choisies)

# Egaliser les configs sur chaque secteur d'un site

combis_sites = {}  # donne les fréquences à ajouter sur chaque site

for secteur in combis_choisies.keys():
    site = secteur[0:6]
    if not site in combis_sites:
        combis_sites[site] = {}
    if combis_choisies[secteur]["choix"] == "Aucune combinaison ne convient":
        if not "limitant" in combis_sites[site]:
            combis_sites[site]["limitant"] = [secteur]
        else:
            combis_sites[site]["limitant"].append(secteur)

    elif not "config" in combis_sites[site]:
        combis_sites[site
                     ]["config"] = combis_choisies[secteur]["choix"]
    else:
        length = 0
        for freq in combis_sites[site]["config"]:
            length += largeurs[freq]
        if combis_choisies[secteur]["bande ajoutee"] >= length:
            combis_sites[site
                         ]["config"] = combis_choisies[secteur]["choix"]

# print(combis_sites)

# les sites avec juste le champ "limitant" rempli sont les sites qui seront saturés quelle que soit la config

for site in combis_sites.keys():
    if not "config" in combis_sites[site]:
        (choix, largeur) = (None, 0)
        for lim in combis_sites[site]["limitant"]:
            combinaison = bandes_dispos[lim]
            length = 0
            for freq in combinaison:
                length += largeurs[freq]/10**6
            if length > largeur:
                largeur = length
                choix = combinaison
    combis_sites[site]["config"] = choix

    combis_sites[site]["prix"] = combi_prix(combis_sites[site]["config"])

combis_a_installer = {}
for secteur in coeffs_secteurs.keys():
    if secteur[0:6] in combis_sites:
        combis_a_installer[secteur] = combis_sites[secteur[0:6]]["config"]

pkl.dump(combis_a_installer, open("combis_a_installer.p", "wb"))

for annee in [2023, 2024, 2025, 2026, 2027]:
    for secteur in bandes_dispos:
        présentes = bandes_dispos[secteur]

# print(combis_choisies)
# print(combis_sites)
# print(combis_a_installer)

# Estimation des investissements à réaliser chaque année

prix_par_annee = {}
besoin_de_site = []  # liste les secteurs saturés même en étant améliorés

annee_update_site = {}

for site in combis_sites.keys():
    if "config" in combis_sites[site]:
        secteurs = []
        if site+"A" in ajouts:
            secteurs.append(site+"A")
        if site+"B" in ajouts:
            secteurs.append(site+"B")
        if site+"C" in ajouts:
            secteurs.append(site+"C")
        annee = min([ajouts[secteur]["annee"] for secteur in secteurs])
        annee_update_site[site] = annee
        if str(annee) not in prix_par_annee:
            prix_par_annee[str(annee)] = combis_sites[site]["prix"]
        else:
            prix_par_annee[str(annee)] += combis_sites[site]["prix"]
    if "limitant" in combis_sites[site]:
        besoin_de_site += combis_sites[site]["limitant"]

pkl.dump(annee_update_site, open("annees_update.p", "wb"))
prix_total = sum([prix_par_annee[annee] for annee in prix_par_annee])

# print(prix_total)
# print(combis_sites)
# print(besoin_de_site)

# # Tracé année par année

# plt.figure()
# names = list(prix_par_annee.keys())
# names.sort()
# values = [prix_par_annee[annee] for annee in names]
# plt.bar(names, values)
# plt.show()

# On va visualiser l'évolution de la répartition des investissements en faisaint varier rho

# Export des données
# pkl.dump(prix_par_annee, open("rho_0_95.p", "wb"))

# Rechargement des données de tous les rho

# rho_0_7 = pkl.load(open("rho_0_7.p", "rb"))
# rho_0_8 = pkl.load(open("rho_0_8.p", "rb"))
# rho_0_9 = pkl.load(open("rho_0_9.p", "rb"))
# rho_0_95 = pkl.load(open("rho_0_95.p", "rb"))
# names = ["2023", "2024", "2025", "2026", "2027"]

# figure = plt.figure(figsize=(10, 6))

# plt.gcf().subplots_adjust(wspace=0.4, hspace=0.4)

# axes = figure.add_subplot(2, 2, 1)
# values_1 = [rho_0_7[annee] for annee in names]
# axes.bar(names, values_1)
# axes.set_title("Rho = 0,7")

# axes = figure.add_subplot(2, 2, 2)
# values_2 = [rho_0_8[annee] for annee in names]
# axes.bar(names, values_2)
# axes.set_title("Rho = 0,8")

# axes = figure.add_subplot(2, 2, 3)
# values_3 = [rho_0_9[annee] for annee in names]
# axes.bar(names, values_3)
# axes.set_title("Rho = 0,9")

# axes = figure.add_subplot(2, 2, 4)
# values_4 = [rho_0_95[annee] for annee in names]
# axes.bar(names, values_4)
# axes.set_title("Rho = 0,95")

# plt.show()

#### Tracé d'un histogramme des modifications ####

plt.figure()
names = list(largeurs.keys())
# print(names)
values = [0]*len(names)
for site in combis_sites:
    for evol in combis_sites[site]["config"]:
        values[names.index(evol)] += 1
plt.bar(names, values)
plt.show()
