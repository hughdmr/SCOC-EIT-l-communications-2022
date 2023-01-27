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

ajouts = {
    2023: {},
    2024: {},
    2025: {},
    2026: {},
    2027: {},
    2028: {}
}

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
secteurs_satures_prevus[2029] = []
# dico similaire des secteurs maxés mais saturés pourtant
secteurs_satures_def = {annee: [] for annee in annees}
secteurs_satures_def[2029] = []

ratio_4g = {  # ratio debit 4G / debit total en début de chaque année
    2023: 0.786,
    2024: 0.6,
    2025: 0.439,
    2026: 0.281,
    2027: 0.172,
    2028: 0.12,
    2029: 0.07
}


x_debut = "2017-06-19"

# Prévisions de 2023 à 2029

previsions = {
    2023: {},
    2024: {},
    2025: {},
    2026: {},
    2027: {},
    2028: {},
    2029: {}
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
    previsions[2029][secteur] = prediction("2029-01-01")


rho_max = 0.8  # choix arbitraire de charge max de la cellule


dic_rho2 = {}  # dictionnaire <secteur>:<charge du secteur>
pkl.dump(dic_rho2, open("dic_rho2.p", "wb"))


def rho_secteurs(previsions):
    for secteur in previsions.keys():
        dic_rho2[secteur] = {}
        for annee in annees:
            dic_rho2[secteur][annee] = previsions[secteur][annee] / \
                (capacites_secteurs[secteur]/10**6)

    # liste des (<secteur de charge supérieure à rho>, <charge du secteur>)


# Recherche des évolutions possibles
frequences = ["700 MHz", "800 MHz", "1800 MHz", "2100 MHz", "2600 MHz"]

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
        if freq_option not in config[2022][secteur] and ("update" not in freq_option):
            config[2022][secteur][freq_option] = False

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

assert (config_to_capacite(config_test) == 53)
assert (config_to_capacite_4g(config_test) == 35)


# renvoie True si une config est valide pour un débit et débit 4G donnés
def config_valide(config, debit, ratio_4g):
    if config_to_capacite(config) == 0 or config_to_capacite_4g(config) == 0:
        return False
    rho = debit/config_to_capacite(config)
    rho_4g = debit*ratio_4g/config_to_capacite_4g(config)
    return rho <= rho_max and rho_4g <= rho_max


def invalide_4g(config, debit, ratio_4g):
    if config_to_capacite_4g(config) == 0:
        return True
    rho_4g = debit*ratio_4g/config_to_capacite_4g(config)
    return rho_4g > rho_max


# Enumérer pour chaque secteur les antennes non encore présentes

def dispo_bandes(config_secteur):
    bandes_dispos = []
    for freq in frequences:
        # la fréquence est disponible sur ce secteur (en 4G)
        if config_secteur[f"{freq} 4G"]:
            bandes_dispos.append(f"{freq} update")
        # la fréquence n’est pas dispo sur ce secteur
        elif not config_secteur[f"{freq} 5G"]:
            bandes_dispos.append(freq+" 4G")
            bandes_dispos.append(freq+" 5G")
    # cette fréquence est uniquement en 5G
    if not config_secteur["3500 MHz"]:
        bandes_dispos.append("3500 MHz")

    return bandes_dispos

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


# fonction qui renvoie la config modifiée par des ajouts de nouvelles fréquences ou bien des màj 4G-->5G
def ajout_config(config_secteur, combi):
    for freq_option in combi:
        if "update" not in freq_option:
            config_secteur[freq_option] = True
        else:
            pos_z = freq_option.index("z")
            freq = freq_option[0:pos_z + 1]
            config_secteur[f"{freq} 5G"] = True
            config_secteur[f"{freq} 4G"] = False
    return config_secteur


prix_par_annee = {
    2023: 0,
    2024: 0,
    2025: 0,
    2026: 0,
    2027: 0,
    2028: 0
}

for annee in annees:  # à chaque année on regarde les previsions
    ### détection des secteurs saturés ###

    for secteur in config[annee-1]:
        configuration = config[annee-1][secteur]
        if not config_valide(config[annee-1][secteur], previsions[annee][secteur], ratio_4g[annee]):
            secteurs_satures_prevus[annee+1].append(secteur)
    config[annee] = config[annee-1]

    ### calcul de toutes les combinaisons possibles ###

    for site in sites:
        secteurs_site = [f"{site}A", f"{site}B"]
        if f"{site}C" in etats_secteurs:
            secteurs_site.append(f"{site}C")

        if f"{site}A" in secteurs_satures_prevus[annee+1] or f"{site}B" in secteurs_satures_prevus[annee+1] or f"{site}C" in secteurs_satures_prevus[annee+1]:
            debit_futur = max([previsions[annee+1][secteur]
                              for secteur in secteurs_site])

            bandes_dispo = dispo_bandes(config[annee-1][secteurs_site[0]])
            combis_possibles = all_combis(bandes_dispo)
            combis_valides = []

            ### détermination des combinaisons valables ###

            for combi in combis_possibles:
                next_config = ajout_config(
                    config[annee-1][secteurs_site[0]], combi)
                if config_valide(next_config, debit_futur, ratio_4g[annee+1]):
                    combis_valides.append(combi)

            if combis_valides == []:
                secteurs_satures_def[annee+1].append(
                    max(secteurs_site, key=lambda c: previsions[annee+1][c]))
                if invalide_4g(config[annee-1][secteur]):
                    for freq_option
            else:
                combi_choisie = min(
                    combis_valides, key=lambda c: combi_prix(c))
                prix_par_annee[annee] = prix_par_annee[annee] + \
                    combi_prix(combi_choisie)

            for secteur in secteurs_site:
                config[annee][secteur] = ajout_config(
                    config[annee-1][secteur], combi_choisie)


besoin_de_site = []  # liste les secteurs saturés même en étant améliorés


prix_total = sum([prix_par_annee[annee] for annee in prix_par_annee])


print(secteurs_satures_def)
print(len(etats_secteurs))
print(len(secteurs_satures_def[2029]))
print(prix_par_annee)
print(prix_total)
