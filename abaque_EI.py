import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 100, 11)
eta = 1.43
y = 1.43*x

plt.figure()
plt.plot(x, y)
plt.xlabel("Largeur de bande (MHz)")
plt.ylabel("Débit maximum écoulable (Mbits/s)")
plt.title("Abaque")
plt.show()
