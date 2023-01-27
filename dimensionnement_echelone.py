import pickle as pkl
import datetime
import matplotlib.pyplot as plt

coeffs_secteurs = pkl.load(open("coeffs.p", "rb"))
capacites_secteurs = pkl.load(open("capacites.p", "rb"))
# réportorie les fréquences dispo sur les différents secteurs
etats_secteurs = pkl.load(open("etats.p", "rb"))

sites = set()  # set des sites
for secteur in etats_secteurs:
    sites.add(secteur[0:6])

config = {
    2022: {},
    2023: {},
    2024: {},
    2025: {},
    2026: {},
    2027: {},
    2028: {}
}  # dictionnaire des config par année et secteur <annee>:{<secteur>:<config du secteur pour cette année>}

annees = [2023, 2024, 2025, 2026, 2027, 2028]
# dico {<année>:set(<secteurs saturés>)} secteurs saturés si on ne changeait pas la config
secteurs_satures_prevus = {annee: [] for annee in annees}
# dico similaire des secteurs maxés mais saturés pourtant
secteurs_satures_def = {annee: [] for annee in annees}

ratio_4g = {  # ratio debit 4G / debit total en début de chaque année
    2023: 0.786,
    2024: 0.6,
    2025: 0.439,
    2026: 0.281,
    2027: 0.172,
    2028: 0.12
}


x_debut = "2017-06-19"

# Prévisions de 2024 à 2027

previsions = {
    2023: {},
    2024: {},
    2025: {},
    2026: {},
    2027: {},
    2028: {}
}  # dictionnaire {<année>:{<secteur>:<prediction de débit sur le secteur au début de l’année>}}

for secteur in coeffs_secteurs.keys():
    a = coeffs_secteurs[secteur][0][0]
    b = coeffs_secteurs[secteur][0][1]

    def prediction(date_pred):
        date_pred = datetime.date.fromisoformat(date_pred)
        date_pred_days = (date_pred-datetime.date.fromisoformat(x_debut)).days
        trafic_pred = a*date_pred_days + b
        return trafic_pred

    for annee in annees:
        previsions[annee][secteur] = prediction(f"{annee}-01-01")


# print(previsions)

rho_max = 0.8  # choix arbitraire de charge max de la cellule


dic_rho = {}  # dictionnaire <secteur>:<charge du secteur>
pkl.dump(dic_rho, open("dic_rho.p", "wb"))


def rho_secteurs(previsions):
    for secteur in previsions.keys():
        dic_rho[secteur] = {}
        for annee in annees:
            dic_rho[secteur][annee] = previsions[secteur][annee] / \
                (capacites_secteurs[secteur]/10**6)

    # liste des (<secteur de charge supérieure à rho>, <charge du secteur>)


# identification des ajouts


# Identification des secteurs devant évoluer, en quelle année et à quel point
'''
for secteur in dic_rho.keys():
    for annee in annees:
        if secteur not in ajouts.keys():
            if dic_rho[secteur][annee] > rho:
                ajouts[secteur] = {
                    "annee": annee,
                    "rho 2028": dic_rho[secteur][2028],
                    "besoin de debit": previsions[secteur][2028]/rho - capacites_secteurs[secteur]/10**6,
                    "besoin de 4g": previsions[secteur][annee]*ratio_4g[annee]/rho - capacites_secteurs_4g[secteur]
                }
'''

# print(ajouts)

# Recherche des évolutions possibles

frequences = ["700 MHz", "800 MHz", "1800 MHz", "2100 MHz", "2600 MHz"]
# frequences_ext = ["700 MHz", "800 MHz",
#                  "1800 MHz", "2100 MHz", "2600 MHz", "3500 MHz"]

largeurs = {
    "700 MHz 4G": 5,
    "700 MHz update": 0.2*5,
    "700 MHz 5G": 1.2*5,
    "800 MHz 4G": 10,
    "800 MHz update": 0.2*10,
    "800 MHz 5G": 1.2*5,
    "1800 MHz 4G": 20,
    "1800 MHz update": 0.2*20,
    "1800 MHz 5G": 1.2*5,
    "2100 MHz 4G": 15,
    "2100 MHz update": 0.2*15,
    "2100 MHz 5G": 1.2*15,
    "2600 MHz 4G": 15,
    "2600 MHz update": 0.2*15,
    "2600 MHz 5G": 1.2*15,
    "3500 MHz": 70
}

# initialisation de config
for secteur in etats_secteurs:
    config[2022][secteur] = {}
    for freq in frequences:
        config[2022][secteur][f"{freq} 4G"] = etats_secteurs[secteur][freq]
    for freq_option in largeurs:
        if (freq_option not in config[2022][secteur]) and ("update" not in freq_option):
            config[2022] = False

assert (config[2022]["T70730A"]) == {
    "700 MHz 4G": False,
    "700 MHz 5G": False,
    "800 MHz 4G": True,
    "800 MHz 5G": False,
    "1800 MHz 4G": True,
    "1800 MHz 5G": False,
    "2100 MHz 4G": True,
    "2100 MHz 5G": False,
    "2600 MHz 4G": False,
    "2600 MHz 5G": False,
    "3500 MHz": False
}


def config_to_capacite(config):  # renvoie la capacité harmonique associée à la config
    capacite = 0
    for freq_option in config:
        if config[freq_option]:
            capacite += largeurs[freq_option]
    return capacite


# renvoie la capacité harmonique en 4G associée à la config
def config_to_capacite_4g(config):
    capacite_4g = 0
    for freq_option in config:
        if "4G" in freq_option and config[freq_option]:
            capacite_4g += largeurs[freq_option]
    return capacite_4g


config_test = {
    "700 MHz 4G": True,
    "700 MHz 5G": False,
    "800 MHz 4G": True,
    "800 MHz 5G": False,
    "1800 MHz 4G": True,
    "1800 MHz 5G": False,
    "2100 MHz 4G": False,
    "2100 MHz 5G": True,
    "2600 MHz 4G": False,
    "2600 MHz 5G": False,
    "3500 MHz": False
}

assert (config_to_capacite(config_test) == 50)
assert (config_to_capacite_4g(config_test) == 35)


# renvoie True si une config est valide pour un débit et débit 4G donnés
def config_valide(config, debit, ratio_4g):
    rho = debit/config_to_capacite(config)
    rho_4g = debit*ratio_4g/config_to_capacite_4g(config)
    return rho <= rho_max and rho_4g <= rho_max


# Enumérer pour chaque secteur les antennes non encore présentes

def dispo_bandes(config_secteur):
    bandes_dispos = []
    for freq in frequences:
        # la fréquence est disponible sur ce secteur (en 4G)
        if config_secteur[f"{freq} 4G"]:
            bandes_dispos.append(f"{freq} update")
        # la fréquence n’est pas dispo sur ce secteur
        elif not config_secteur[f"{freq} 5G"]:
            bandes_dispos[secteur].append(freq+" 4G")
            bandes_dispos[secteur].append(freq+" 5G")
    # cette fréquence est uniquement en 5G
    if not etats_secteurs[secteur]["3500 MHz"]:
        bandes_dispos[secteur].append("3500 MHz")

    return bandes_dispos

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


'''
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
        
'''

# print(combis_choisies)

# Egaliser les configs sur chaque secteur d'un site

'''
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

'''

# print(combis_sites)

# les sites avec juste le champ "limitant" rempli sont les sites qui seront saturés quelle que soit la config

'''

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
for secteur in combis_choisies.keys():
    combis_a_installer[secteur] = combis_sites[secteur[0:6]]["config"]
    
'''

# fonction qui renvoie la config modifiée par des ajouts de nouvelles fréquences ou bien des màj 4G-->5G


def ajout_config(config_secteur, combi):
    for freq_option in combi:
        if "update" not in freq_option:
            config_secteur[freq_option] = True
        else:
            pos_z = freq.index("z")
            freq = freq_option[0:pos_z + 1]
            config_secteur[f"{freq} 5G"] = True
            config_secteur[f"{freq} 4G"] = False


prix_par_annee = {}

for annee in annees:  # à chaque année on regarde les previsions
    ### détection des secteurs saturés ###

    for secteur in config[annee-1]:
        configuration = config[annee-1][secteur]
        if not (config_valide(config, previsions[annee], ratio_4g[annee]) and config_valide(config, previsions[annee+1], ratio_4g[annee])):
            secteurs_satures_prevus[annee+1].append(secteur)
    config[annee] = config[annee-1]

    ### calcul de toutes les combinaisons possibles ###

    for site in sites:
        secteurs_site = [f"{site}A", f"{site}B", f"{site}C"]
        if f"{site}A" in secteurs_satures_prevus[annee+1] or f"{site}B" in secteurs_satures_prevus[annee+1] or f"{site}C" in secteurs_satures_prevus[annee+1]:
            debit_futur = max([previsions[annee+1][secteur]
                              for secteur in secteurs_site])
            debit_actuel = max([previsions[annee][secteur]
                               for secteur in secteurs_site])

        bandes_dispo = dispo_bandes(secteurs_site[0])
        combis_possibles = all_combis(bandes_dispo)
        combis_valides = []

        ### détermination des combinaisons valables ###

        for combi in combis_possibles:
            next_config = ajout_config(
                config[annee-1][secteurs_site[0]], combi)
            if config_valide(next_config, debit_actuel, ratio_4g[annee]) and config_valide(next_config, debit_futur, ratio_4g[annee+1]):
                combis_valides.append(combi)

        combi_choisie = 0
        if combis_valides == []:
            secteurs_satures_def.append(
                max(secteurs_site, key=lambda c: previsions[annee+1][c]))

    # print(combis_choisies)
    # print(combis_sites)
    # print(combis_a_installer)

    # Estimation des investissements à réaliser chaque année


besoin_de_site = []  # liste les secteurs saturés même en étant améliorés


'''
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
        if str(annee) not in prix_par_annee:
            prix_par_annee[str(annee)] = combis_sites[site]["prix"]
        else:
            prix_par_annee[str(annee)] += combis_sites[site]["prix"]
    if "limitant" in combis_sites[site]:
        besoin_de_site += combis_sites[site]["limitant"]
'''

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
