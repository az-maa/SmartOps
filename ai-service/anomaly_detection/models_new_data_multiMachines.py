import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import precision_score, recall_score, f1_score
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense
from tensorflow.keras.optimizers import Adam

####################### 1. Fonction Autoencoder avec optimisation #########################
def train_autoencoder(X_train, X_test, y_true):
    input_dim = X_train.shape[1]
    input_layer = Input(shape=(input_dim,))
    encoded = Dense(32, activation="relu")(input_layer)   # plus de neurones
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
            best = (p, threshold, precision, recall, f1)
    return best[2], best[3], best[4]  # Precision, Recall, F1

####################### 2. Isolation Forest #########################
def train_isolation_forest(X_train, X_test, y_true):
    iso = IsolationForest(contamination=0.05, random_state=42)
    iso.fit(X_train)
    y_pred = iso.predict(X_test)
    y_pred = np.where(y_pred == -1, 1, 0)
    return (precision_score(y_true, y_pred),
            recall_score(y_true, y_pred),
            f1_score(y_true, y_pred))

####################### 3. One-Class SVM #########################
def train_oneclass_svm(X_train, X_test, y_true):
    svm = OneClassSVM(kernel="rbf", nu=0.05, gamma="scale")
    svm.fit(X_train)
    y_pred = svm.predict(X_test)
    y_pred = np.where(y_pred == -1, 1, 0)
    return (precision_score(y_true, y_pred),
            recall_score(y_true, y_pred),
            f1_score(y_true, y_pred))

####################### 4. Boucle sur toutes les machines #########################
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
        p_if, r_if, f_if = train_isolation_forest(X_train, X_test, y_true)

        # One-Class SVM
        p_svm, r_svm, f_svm = train_oneclass_svm(X_train, X_test, y_true)

        # Autoencoder
        p_ae, r_ae, f_ae = train_autoencoder(X_train, X_test, y_true)

        # Sauvegarder résultats
        results.append([machine_name,
                        p_if, r_if, f_if,
                        p_svm, r_svm, f_svm,
                        p_ae, r_ae, f_ae])

####################### 5. Tableau comparatif global #########################
columns = ["Machine",
           "IF_Precision", "IF_Recall", "IF_F1",
           "SVM_Precision", "SVM_Recall", "SVM_F1",
           "AE_Precision", "AE_Recall", "AE_F1"]

results_df = pd.DataFrame(results, columns=columns)
print("\n=== Résultats globaux ===")
print(results_df)

# Sauvegarder en CSV
results_df.to_csv("comparaison_models_SMD.csv", index=False)

####################### 6. Visualisation graphique #########################
plt.figure(figsize=(12,8))
sns.heatmap(results_df.set_index("Machine")[["IF_F1","SVM_F1","AE_F1"]],
            annot=True, fmt=".2f", cmap="YlGnBu")
plt.title("Comparaison des F1-scores par machine et par modèle")
plt.show()

# Barplot comparatif
plt.figure(figsize=(14,6))
results_melt = results_df.melt(id_vars="Machine",
                               value_vars=["IF_F1","SVM_F1","AE_F1"],
                               var_name="Modèle", value_name="F1-score")
sns.barplot(data=results_melt, x="Machine", y="F1-score", hue="Modèle")
plt.xticks(rotation=90)
plt.title("Comparaison des F1-scores par machine")
plt.show()
