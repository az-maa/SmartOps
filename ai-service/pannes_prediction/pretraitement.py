import pandas as pd
import numpy as np

# === 1. Charger les fichiers CSV ===
telemetry = pd.read_csv("../Data_Pred/PdM_telemetry.csv")
errors = pd.read_csv("../Data_Pred/PdM_errors.csv")
maint = pd.read_csv("../Data_Pred/PdM_maint.csv")
failures = pd.read_csv("../Data_Pred/PdM_failures.csv")
machines = pd.read_csv("../Data_Pred/PdM_machines.csv")

# === 2. Harmoniser les colonnes de temps ===
for df in [telemetry, errors, maint, failures]:
    df['datetime'] = pd.to_datetime(df['datetime'])

# === 3. Fusionner les données ===
data = telemetry.copy()

# Ajouter les pannes (labels)
data = data.merge(failures, on=["datetime","machineID"], how="left")
data['failure'] = data['failure'].notnull().astype(int)

# Ajouter les erreurs (one-hot encoding)
data = data.merge(errors, on=["datetime","machineID"], how="left")
data = pd.get_dummies(data, columns=["errorID"], prefix="error")
for col in data.columns:
    if "error_" in col:
        data[col] = data[col].fillna(0)

# Ajouter la maintenance
data = data.merge(maint, on=["datetime","machineID"], how="left")
data['maintenance'] = data['comp'].notnull().astype(int)

# Ajouter les métadonnées
data = data.merge(machines, on="machineID", how="left")

# === 4. Feature engineering : rolling windows sur 24h ===
data = data.sort_values(["machineID","datetime"])
for feature in ['volt','rotate','pressure','vibration']:
    data[f'{feature}_mean_24h'] = data.groupby("machineID")[feature].transform(lambda x: x.rolling(24, min_periods=1).mean())
    data[f'{feature}_std_24h'] = data.groupby("machineID")[feature].transform(lambda x: x.rolling(24, min_periods=1).std())

# Remplacer NaN par 0
data.fillna(0, inplace=True)

# === 5. Sauvegarder le dataset final ===
data.to_csv("../Data_Pred/preprocessed_dataset.csv", index=False)

print("✅ Prétraitement terminé. Dataset fusionné et enrichi enregistré sous : Data_Pred/preprocessed_dataset.csv")
print("Dimensions finales :", data.shape)
print("Colonnes :", data.columns.tolist())
