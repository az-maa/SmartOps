import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score

# === 1. Charger le dataset prétraité ===
data = pd.read_csv("../Data_Pred/preprocessed_dataset.csv")
data = data.sort_values(["machineID","datetime"])

# === 2. Définir les features ===
features = ['volt','rotate','pressure','vibration',
            'volt_mean_24h','rotate_mean_24h','pressure_mean_24h','vibration_mean_24h',
            'volt_std_24h','rotate_std_24h','pressure_std_24h','vibration_std_24h',
            'maintenance','age']

sequence_length = 24
X, y = [], []

# === 3. Créer les séquences temporelles ===
for machine in data['machineID'].unique():
    machine_data = data[data['machineID']==machine]
    values = machine_data[features].astype(np.float32).values
    labels_machine = machine_data['failure'].values
    for i in range(len(values)-sequence_length):
        X.append(values[i:i+sequence_length])
        y.append(labels_machine[i+sequence_length])

X = np.array(X)
y = np.array(y)

print("Shape des séquences :", X.shape, "Shape des labels :", y.shape)

# === 4. Undersampling avec ratio 3:1 ===
pos_idx = np.where(y == 1)[0]   # indices des pannes
neg_idx = np.where(y == 0)[0]   # indices des normales

# Ratio choisi : 3 normales pour 1 panne
undersampled_neg_idx = np.random.choice(neg_idx, size=len(pos_idx)*3, replace=False)

# Fusionner indices
balanced_idx = np.concatenate([pos_idx, undersampled_neg_idx])

# Créer dataset équilibré
X_balanced = X[balanced_idx]
y_balanced = y[balanced_idx]

print("Nouvelle distribution :", np.bincount(y_balanced))

# === 5. Split train/test ===
X_train, X_test, y_train, y_test = train_test_split(X_balanced, y_balanced, test_size=0.2, random_state=42, stratify=y_balanced)

# === 6. Construire le modèle LSTM ===
model = Sequential()
model.add(LSTM(64, input_shape=(sequence_length, len(features)), return_sequences=False))
model.add(Dropout(0.3))
model.add(Dense(32, activation='relu'))
model.add(Dropout(0.3))
model.add(Dense(1, activation='sigmoid'))

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# === 7. Entraînement ===
history = model.fit(X_train, y_train, epochs=10, batch_size=32, validation_split=0.2)

# === 8. Évaluation ===
y_pred_prob = model.predict(X_test)
y_pred = (y_pred_prob > 0.5).astype("int32")

print(classification_report(y_test, y_pred))
print("AUC-ROC :", roc_auc_score(y_test, y_pred_prob))

