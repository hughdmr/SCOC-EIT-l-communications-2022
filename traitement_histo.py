# exécuter py -m pip install scikit-learn dans un terminal
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression
import datetime
import pickle as pkl

# Lecture du fichier
data = pd.read_csv("histo_trafic.csv", delimiter=";")

# Création du dictionnaire contenant le trafic total pour chaque date
dates = {}
trafic = np.array(data["trafic_mbps"])

for i in range(len(trafic)):
    if data["tstamp"][i][0:10] not in dates:
        dates[data["tstamp"][i][0:10]] = trafic[i]
    else:
        dates[data["tstamp"][i][0:10]] += trafic[i]

# Extraction des données sous forme de listes
x = []
y = []

for date, sum in dates.items():
    x.append(date)
    y.append(sum)

x_debut = x[0]

# Passage d'une date au format yyyy-mm-dd à une valeur numérique en jours depuis la première mesure

x_diff = []
for element in x:
    x_diff.append((datetime.date.fromisoformat(element) -
                  datetime.date.fromisoformat(x_debut)).days)

# Conversion au format numpy et redimensionnement

x_diff = np.array(x_diff)
y = np.array(y)

x_reshaped = x_diff.reshape(-1, 1)
y_reshaped = y.reshape(-1, 1)

# Régression linéaire

reg = LinearRegression()
reg.fit(x_reshaped, y_reshaped)

a = reg.coef_[0]
b = reg.intercept_

# Tracé des points et de la régression

y_reg = [a*x+b for x in x_diff]

plt.figure(figsize=(10, 6))
plt.scatter(x_diff, y)
plt.plot(x_diff, y_reg, 'r')
plt.title("Evolution du trafic en fonction du temps")
plt.xlabel("Dates")
plt.ylabel("Trafic total en Mbps")
plt.show()

# Prédiction du trafic global à une certaine date


def prediction(date_pred):
    date_pred = datetime.date.fromisoformat(date_pred)
    date_pred_days = (date_pred-datetime.date.fromisoformat(x_debut)).days
    trafic_pred = a*date_pred_days + b
    print(date_pred_days)
    return trafic_pred

# date_pred = '2032-01-01'
# print(prediction(date_pred))


############################ Adaptation à une prédiction personnalisée par secteur ############################

# On va intègrer le dictionnaire "dates" précédent dans un dictionnaire "secteurs"

secteurs = {}
coeffs_secteurs = {}

# Remplissage du dictionnaire avec les noms de secteurs

data_secteurs = data["secteur"]
for i in range(len(data_secteurs)):
    if data_secteurs[i] not in secteurs:
        secteurs[data_secteurs[i]] = {}
        coeffs_secteurs[data_secteurs[i]] = []


for i in range(len(data_secteurs)):
    secteurs[data_secteurs[i]][data["tstamp"]
                               [i][0:10]] = data["trafic_mbps"][i]

# Traitement individuel

for secteur in secteurs.keys():

    # Extraction des données sous forme de listes
    x = []
    y = []

    for date, value in secteurs[secteur].items():
        x.append(date)
        y.append(value)

    # Passage d'une date au format yyyy-mm-dd à une valeur numérique en jours depuis la première mesure

    x_diff = []
    for element in x:
        x_diff.append((datetime.date.fromisoformat(element) -
                      datetime.date.fromisoformat(x_debut)).days)

    # Conversion au format numpy et redimensionnement

    x_diff = np.array(x_diff)
    y = np.array(y)

    x_reshaped = x_diff.reshape(-1, 1)
    y_reshaped = y.reshape(-1, 1)

    # Régression linéaire

    reg = LinearRegression()
    reg.fit(x_reshaped, y_reshaped)

    a = reg.coef_[0]
    b = reg.intercept_

    coeffs_secteurs[secteur] = [(a[0], b[0]), x_diff, y]


pkl.dump(coeffs_secteurs, open("coeffs.p", "wb"))

# print(coeffs_secteurs)

# Tracé pour un secteur quelconque


def trace_secteur(secteur):
    a = coeffs_secteurs[secteur][0][0]
    b = coeffs_secteurs[secteur][0][1]
    x = coeffs_secteurs[secteur][1]
    y = coeffs_secteurs[secteur][2]
    y_reg = [a*x_i+b for x_i in x]
    plt.figure(figsize=(10, 6))
    plt.scatter(x, y)
    plt.plot(x, y_reg, 'r')
    plt.title(
        "Evolution du trafic en fonction du temps dans le secteur {}".format(secteur))
    plt.xlabel("Dates")
    plt.ylabel("Trafic total en Mbps")
    plt.show()

trace_secteur("T78273B")

# Prédiction du traffic par secteur à une date yyyy-mm-dd


def prediction_secteur(date):
    pred_trafic = {}
    for key in coeffs_secteurs.keys():
        a, b = coeffs_secteurs[key][0]
        days = (datetime.date.fromisoformat(date) -
                datetime.date.fromisoformat(x_debut)).days
        pred_trafic[key] = a*days + b
    return pred_trafic

# print(prediction_secteur("2030-01-02"))
