import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, LayerNormalization
from tensorflow.keras.layers import MultiHeadAttention, Flatten
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

# === 4. Undersampling ratio 3:1 ===
pos_idx = np.where(y == 1)[0]
neg_idx = np.where(y == 0)[0]
undersampled_neg_idx = np.random.choice(neg_idx, size=len(pos_idx)*3, replace=False)
balanced_idx = np.concatenate([pos_idx, undersampled_neg_idx])

X_balanced = X[balanced_idx]
y_balanced = y[balanced_idx]

print("Nouvelle distribution :", np.bincount(y_balanced))

# === 5. Split train/test ===
X_train, X_test, y_train, y_test = train_test_split(X_balanced, y_balanced, test_size=0.2, random_state=42, stratify=y_balanced)

# === 6. Construire le modèle Transformer ===
inputs = tf.keras.Input(shape=(sequence_length, len(features)))
x = MultiHeadAttention(num_heads=4, key_dim=16)(inputs, inputs)
x = LayerNormalization(epsilon=1e-6)(x)
x = Flatten()(x)
x = Dense(64, activation='relu')(x)
x = Dropout(0.3)(x)
x = Dense(32, activation='relu')(x)
x = Dropout(0.3)(x)
outputs = Dense(1, activation='sigmoid')(x)

model = tf.keras.Model(inputs, outputs)
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# === 7. Entraînement ===
history = model.fit(X_train, y_train, epochs=10, batch_size=32, validation_split=0.2)

# === 8. Évaluation ===
y_pred_prob = model.predict(X_test)
y_pred = (y_pred_prob > 0.5).astype("int32")

print(classification_report(y_test, y_pred))
print("AUC-ROC :", roc_auc_score(y_test, y_pred_prob))
