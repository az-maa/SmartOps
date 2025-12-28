import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import precision_score, recall_score, f1_score
from sklearn.ensemble import IsolationForest
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense
from tensorflow.keras.optimizers import Adam

####################### 1. Fonction Autoencoder #########################
def train_autoencoder(X_train, X_test, y_true):
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
    autoencoder.fit(X_train, X_train, epochs=20, batch_size=64, shuffle=True, verbose=0)

    # Reconstruction error
    X_test_pred = autoencoder.predict(X_test)
    errors = np.mean(np.square(X_test - X_test_pred), axis=1)

    # Optimisation du seuil
    percentiles = range(80, 100, 2)
    best = None
    for p in percentiles:
        threshold = np.percentile(errors, p)
        y_pred = (errors > threshold).astype(int)
        precision = precision_score(y_true, y_pred)
        recall = recall_score(y_true, y_pred)
        f1 = f1_score(y_true, y_pred)
        if best is None or f1 > best[4]:
            best = (p, threshold, precision, recall, f1, y_pred)
    return best[2], best[3], best[4], best[5]  # Precision, Recall, F1, y_pred

####################### 2. Isolation Forest #########################
def train_isolation_forest(X_train, X_test, y_true):
    iso = IsolationForest(contamination=0.05, random_state=42)
    iso.fit(X_train)
    y_pred = iso.predict(X_test)
    y_pred = np.where(y_pred == -1, 1, 0)
    return (precision_score(y_true, y_pred),
            recall_score(y_true, y_pred),
            f1_score(y_true, y_pred),
            y_pred)

####################### 3. Boucle sur toutes les machines #########################
results = []

base_path = "ServerMachineDataset"
train_path = os.path.join(base_path, "train")
test_path = os.path.join(base_path, "test")
label_path = os.path.join(base_path, "test_label")

for file in os.listdir(train_path):
    if file.endswith(".txt"):
        machine_name = file.replace(".txt", "")
        print(f"\n=== Machine {machine_name} ===")

        # Charger données
        train_df = pd.read_csv(os.path.join(train_path, file), header=None)
        test_df = pd.read_csv(os.path.join(test_path, file), header=None)
        labels = pd.read_csv(os.path.join(label_path, file), header=None)

        scaler = StandardScaler()
        X_train = scaler.fit_transform(train_df)
        X_test = scaler.transform(test_df)
        y_true = labels.values.ravel()

        # Isolation Forest
        p_if, r_if, f_if, y_pred_if = train_isolation_forest(X_train, X_test, y_true)

        # Autoencoder
        p_ae, r_ae, f_ae, y_pred_ae = train_autoencoder(X_train, X_test, y_true)

        # Combinaisons
        y_pred_union = np.where((y_pred_ae == 1) | (y_pred_if == 1), 1, 0)
        y_pred_intersection = np.where((y_pred_ae == 1) & (y_pred_if == 1), 1, 0)

        # Vote pondéré avec plusieurs poids
        weights_list = [(0.3,0.7), (0.5,0.5), (0.7,0.3)]
        vote_scores = []
        for w in weights_list:
            y_pred_vote = np.where((w[0]*y_pred_ae + w[1]*y_pred_if) >= 0.5, 1, 0)
            vote_scores.append((w,
                                precision_score(y_true, y_pred_vote),
                                recall_score(y_true, y_pred_vote),
                                f1_score(y_true, y_pred_vote)))

        # Sauvegarder résultats
        results.append([machine_name,
                        p_if, r_if, f_if,
                        p_ae, r_ae, f_ae,
                        precision_score(y_true, y_pred_union),
                        recall_score(y_true, y_pred_union),
                        f1_score(y_true, y_pred_union),
                        precision_score(y_true, y_pred_intersection),
                        recall_score(y_true, y_pred_intersection),
                        f1_score(y_true, y_pred_intersection),
                        vote_scores[0][1], vote_scores[0][2], vote_scores[0][3],  # 0.3/0.7
                        vote_scores[1][1], vote_scores[1][2], vote_scores[1][3],  # 0.5/0.5
                        vote_scores[2][1], vote_scores[2][2], vote_scores[2][3]]) # 0.7/0.3

####################### 4. Tableau comparatif global #########################
columns = ["Machine",
           "IF_Precision","IF_Recall","IF_F1",
           "AE_Precision","AE_Recall","AE_F1",
           "Union_Precision","Union_Recall","Union_F1",
           "Inter_Precision","Inter_Recall","Inter_F1",
           "Vote03_Precision","Vote03_Recall","Vote03_F1",
           "Vote05_Precision","Vote05_Recall","Vote05_F1",
           "Vote07_Precision","Vote07_Recall","Vote07_F1"]

results_df = pd.DataFrame(results, columns=columns)
print("\n=== Résultats globaux ===")
print(results_df)

# Sauvegarder en CSV
results_df.to_csv("comparaison_combinaisons_votes_SMD.csv", index=False)

####################### 5. Visualisation #########################
plt.figure(figsize=(12,8))
sns.heatmap(results_df.set_index("Machine")[["IF_F1","AE_F1","Union_F1","Inter_F1","Vote03_F1","Vote05_F1","Vote07_F1"]],
            annot=True, fmt=".2f", cmap="YlGnBu")
plt.title("Heatmap des F1-scores par machine et stratégie")
plt.show()

plt.figure(figsize=(14,6))
results_melt = results_df.melt(id_vars="Machine",
                               value_vars=["IF_F1","AE_F1","Union_F1","Inter_F1","Vote03_F1","Vote05_F1","Vote07_F1"],
                               var_name="Modèle", value_name="F1-score")
sns.barplot(data=results_melt, x="Machine", y="F1-score", hue="Modèle")
plt.xticks(rotation=90)
plt.title("Comparaison des F1-scores par machine")
plt.show()

####################### 6. Moyennes globales #########################
print("\n=== Moyennes globales des F1-scores ===")
for col in ["IF_F1","AE_F1","Union_F1","Inter_F1","Vote03_F1","Vote05_F1","Vote07_F1"]:
    print(f"{col}: {results_df[col].mean():.3f}")
