import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt


####################### Charger et préparer les données #########################

# Charger dataset
df = pd.read_csv("data/system_resources.csv")

# Sélection des features
X = df[["cpu", "ram", "disk", "network"]]

# Normalisation
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

####################### Entraîner Isolation Forest #########################

# Créer et entraîner le modèle
model = IsolationForest(contamination=0.05, random_state=42)
y_pred = model.fit_predict(X_scaled)

# Ajouter la colonne anomalies (-1 = anomalie, 1 = normal)
df["anomaly"] = y_pred

# Résultats numériques
n_normaux = (y_pred == 1).sum()
n_anomalies = (y_pred == -1).sum()

print("Nombre d'observations normales :", n_normaux)
print("Nombre d'anomalies détectées   :", n_anomalies)

# Scores d'anomalie
scores = model.decision_function(X_scaled)
print("\nRésumé des scores d'anomalie :")
print(pd.Series(scores).describe())
####################### Visualiser les anomalies #########################

plt.figure(figsize=(8,6))
plt.scatter(df["cpu"], df["ram"], c=df["anomaly"], cmap="coolwarm")
plt.xlabel("CPU")
plt.ylabel("RAM")
plt.title("Anomalies détectées par Isolation Forest")
plt.show()

plt.figure(figsize=(8,6))
plt.scatter(df["disk"], df["network"], c=df["anomaly"], cmap="coolwarm")
plt.xlabel("Disk")
plt.ylabel("Network")
plt.title("Anomalies détectées (Disk vs Network)")
plt.show()

plt.figure(figsize=(6,4))
df["anomaly"].value_counts().plot(kind="bar", color=["red", "blue"])
plt.xticks([0,1], ["Normal (1)", "Anomalie (-1)"], rotation=0)
plt.title("Distribution des anomalies")
plt.ylabel("Nombre d'observations")
plt.show()


