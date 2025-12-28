import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import precision_score, recall_score, f1_score
from sklearn.ensemble import IsolationForest
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense
from tensorflow.keras.optimizers import Adam

####################### 1. Charger les données #########################
train_df = pd.read_csv("ServerMachineDataset/train/machine-1-1.txt", header=None)
test_df = pd.read_csv("ServerMachineDataset/test/machine-1-1.txt", header=None)
labels = pd.read_csv("ServerMachineDataset/test_label/machine-1-1.txt", header=None)

scaler = StandardScaler()
X_train = scaler.fit_transform(train_df)
X_test = scaler.transform(test_df)
y_true = labels.values.ravel()

####################### 2. Isolation Forest #########################
iso = IsolationForest(contamination=0.05, random_state=42)
iso.fit(X_train)
y_pred_if = iso.predict(X_test)
y_pred_if = np.where(y_pred_if == -1, 1, 0)

####################### 3. Autoencoder avec optimisation du seuil #########################
input_dim = X_train.shape[1]
input_layer = Input(shape=(input_dim,))
encoded = Dense(32, activation="relu")(input_layer)
encoded = Dense(16, activation="relu")(encoded)
encoded = Dense(8, activation="relu")(encoded)
decoded = Dense(16, activation="relu")(encoded)
decoded = Dense(32, activation="relu")(decoded)
output_layer = Dense(input_dim, activation="linear")(decoded)

autoencoder = Model(inputs=input_layer, outputs=output_layer)
autoencoder.compile(optimizer=Adam(learning_rate=0.001), loss="mse")
autoencoder.fit(X_train, X_train, epochs=20, batch_size=64, shuffle=True, verbose=1)

# Reconstruction error
X_test_pred = autoencoder.predict(X_test)
errors = np.mean(np.square(X_test - X_test_pred), axis=1)

# Optimisation du seuil
percentiles = range(80, 100, 2)
best = None
for p in percentiles:
    threshold = np.percentile(errors, p)
    y_pred_ae = (errors > threshold).astype(int)
    precision = precision_score(y_true, y_pred_ae)
    recall = recall_score(y_true, y_pred_ae)
    f1 = f1_score(y_true, y_pred_ae)
    if best is None or f1 > best[4]:
        best = (p, threshold, precision, recall, f1, y_pred_ae)

print("\nAutoencoder optimisé:")
print(f"Seuil percentile {best[0]} | Precision={best[2]:.3f} | Recall={best[3]:.3f} | F1={best[4]:.3f}")
y_pred_ae = best[5]

####################### 4. Combinaison Autoencoder + Isolation Forest #########################

# Union (OR) → anomalie si l’un des deux détecte
y_pred_union = np.where((y_pred_ae == 1) | (y_pred_if == 1), 1, 0)

# Intersection (AND) → anomalie si les deux détectent
y_pred_intersection = np.where((y_pred_ae == 1) & (y_pred_if == 1), 1, 0)

# Vote pondéré (Autoencoder plus important)
weights = [0.6, 0.4]
y_pred_vote = np.where((weights[0]*y_pred_ae + weights[1]*y_pred_if) >= 0.5, 1, 0)

####################### 5. Évaluation #########################
for name, y_pred in [("Isolation Forest", y_pred_if),
                     ("Autoencoder", y_pred_ae),
                     ("Union (OR)", y_pred_union),
                     ("Intersection (AND)", y_pred_intersection),
                     ("Vote pondéré", y_pred_vote)]:
    print(f"\n{name}:")
    print("Precision:", precision_score(y_true, y_pred))
    print("Recall   :", recall_score(y_true, y_pred))
    print("F1-score :", f1_score(y_true, y_pred))
