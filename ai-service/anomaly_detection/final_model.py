import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense
from tensorflow.keras.optimizers import Adam

####################### Charger et préparer les données #########################

df = pd.read_csv("data/system_resources.csv")
X = df[["cpu", "ram", "disk", "network"]]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

####################### Étape 1 : Isolation Forest #########################

iso = IsolationForest(contamination=0.05, random_state=42)
y_pred_iso = iso.fit_predict(X_scaled)
df["anomaly_iso"] = y_pred_iso   # -1 = anomalie, 1 = normal

####################### Étape 2 : Autoencoder #########################

input_dim = X_scaled.shape[1]
input_layer = Input(shape=(input_dim,))
encoded = Dense(8, activation="relu")(input_layer)
encoded = Dense(4, activation="relu")(encoded)
decoded = Dense(8, activation="relu")(encoded)
output_layer = Dense(input_dim, activation="linear")(decoded)

autoencoder = Model(inputs=input_layer, outputs=output_layer)
autoencoder.compile(optimizer=Adam(learning_rate=0.001), loss="mse")

# Entraînement uniquement sur les normales
X_normals = X_scaled[y_pred_iso == 1]
autoencoder.fit(X_normals, X_normals,
                epochs=50,
                batch_size=16,
                shuffle=True,
                validation_split=0.1,
                verbose=0)

####################### Validation des anomalies #########################

X_suspects = X_scaled[y_pred_iso == -1]
X_suspects_pred = autoencoder.predict(X_suspects)
errors_suspects = np.mean(np.square(X_suspects - X_suspects_pred), axis=1)

X_normals_pred = autoencoder.predict(X_normals)
errors_normals = np.mean(np.square(X_normals - X_normals_pred), axis=1)
threshold = np.percentile(errors_normals, 95)

df.loc[y_pred_iso == -1, "anomaly_final"] = (errors_suspects > threshold).astype(int)
df["anomaly_final"] = df["anomaly_final"].fillna(0)

####################### Étape 3 : Comparaison avec seuils métier #########################

# Définir les seuils métier
seuils = {
    "cpu": 90,
    "ram": 80,
    "disk": 85,
    "network": 70
}

# Extraire les anomalies confirmées
anomalies = df[df["anomaly_final"] == 1]

print("\nAnomalies confirmées par le modèle :")
print(anomalies[["cpu", "ram", "disk", "network"]])

# Comparer avec les seuils métier
print("\nValidation par seuils métier :")
for idx, row in anomalies.iterrows():
    conditions = []
    if row["cpu"] > seuils["cpu"]:
        conditions.append(f"CPU={row['cpu']} > {seuils['cpu']}")
    if row["ram"] > seuils["ram"]:
        conditions.append(f"RAM={row['ram']} > {seuils['ram']}")
    if row["disk"] > seuils["disk"]:
        conditions.append(f"Disk={row['disk']} > {seuils['disk']}")
    if row["network"] > seuils["network"]:
        conditions.append(f"Network={row['network']} > {seuils['network']}")
    
    if conditions:
        print(f"Observation {idx} validée par règles métier → {', '.join(conditions)}")
    else:
        print(f"Observation {idx} détectée par le modèle mais non critique selon les seuils métier.")

####################### Visualisation #########################

plt.figure(figsize=(8,6))
plt.scatter(df["cpu"], df["ram"], c=df["anomaly_final"], cmap="coolwarm")
plt.axhline(seuils["ram"], color="green", linestyle="--", label="Seuil RAM")
plt.axvline(seuils["cpu"], color="red", linestyle="--", label="Seuil CPU")
plt.xlabel("CPU")
plt.ylabel("RAM")
plt.title("Anomalies confirmées et seuils métier")
plt.legend()
plt.show()
