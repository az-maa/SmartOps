import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense
from tensorflow.keras.optimizers import Adam

####################### Charger et préparer les données #########################

# Charger dataset
df = pd.read_csv("data/system_resources.csv")

# Sélection des features
X = df[["cpu", "ram", "disk", "network"]]

# Normalisation
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

####################### Construire l'Autoencoder #########################

# Dimension d'entrée
input_dim = X_scaled.shape[1]

# Architecture simple
input_layer = Input(shape=(input_dim,))
encoded = Dense(8, activation="relu")(input_layer)
encoded = Dense(4, activation="relu")(encoded)
decoded = Dense(8, activation="relu")(encoded)
output_layer = Dense(input_dim, activation="linear")(decoded)

autoencoder = Model(inputs=input_layer, outputs=output_layer)
autoencoder.compile(optimizer=Adam(learning_rate=0.001), loss="mse")

####################### Entraîner l'Autoencoder #########################

autoencoder.fit(X_scaled, X_scaled,
                epochs=50,
                batch_size=16,
                shuffle=True,
                validation_split=0.1,
                verbose=0)

####################### Calculer les erreurs de reconstruction #########################

X_pred = autoencoder.predict(X_scaled)
mse = np.mean(np.power(X_scaled - X_pred, 2), axis=1)

# Définir un seuil (par ex. 95e percentile)
threshold = np.percentile(mse, 95)
df["anomaly_auto"] = (mse > threshold).astype(int)  # 1 = anomalie, 0 = normal

####################### Résultats numériques #########################

n_normaux = (df["anomaly_auto"] == 0).sum()
n_anomalies = (df["anomaly_auto"] == 1).sum()

print("Nombre d'observations normales :", n_normaux)
print("Nombre d'anomalies détectées   :", n_anomalies)
print("\nRésumé des erreurs de reconstruction :")
print(pd.Series(mse).describe())

####################### Visualiser les anomalies #########################

plt.figure(figsize=(8,6))
plt.scatter(df["cpu"], df["ram"], c=df["anomaly_auto"], cmap="coolwarm")
plt.xlabel("CPU")
plt.ylabel("RAM")
plt.title("Anomalies détectées par Autoencoder")
plt.show()

