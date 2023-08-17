import pandas as pd

# Charger le fichier CSV
data = pd.read_csv('Puppet_smells_all.csv')
data = data.drop(['URL', 'projectName', 'file_name', 'LOC', 'module'], axis=1)
data = pd.get_dummies(data)
data = data.astype(bool)

# Compter le nombre de lignes avec chaque nombre de smells
co_occurrence_counts = data.sum(axis=1).value_counts().sort_index()

# Calculer le pourcentage de présence de co-occurrence pour chaque nombre de smells
total_rows = len(data)
co_occurrence_percentages = co_occurrence_counts / total_rows * 100

# Afficher les résultats
for num_smells, percentage in co_occurrence_percentages.items():
    print(f"{num_smells} Smells: {percentage:.2f}%")

