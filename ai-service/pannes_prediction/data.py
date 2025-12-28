import pandas as pd

# Liste des fichiers
files = {
    "Telemetry": "../Data_Pred/PdM_telemetry.csv",
    "Errors": "../Data_Pred/PdM_errors.csv",
    "Maintenance": "../Data_Pred/PdM_maint.csv",
    "Failures": "../Data_Pred/PdM_failures.csv",
    "Machines": "../Data_Pred/PdM_machines.csv"
}

# Lecture et exploration
for name, path in files.items():
    print(f"\n===== {name} =====")
    try:
        df = pd.read_csv(path)
        print("Colonnes :", df.columns.tolist())
        print("Nombre de lignes :", len(df))
        print("Aperçu :")
        print(df.head(5))   # afficher les 5 premières lignes
        print("\nInfos générales :")
        print(df.info())
        print("\nStatistiques descriptives :")
        print(df.describe(include='all'))
    except Exception as e:
        print(f"Erreur lors de la lecture de {name} : {e}")
