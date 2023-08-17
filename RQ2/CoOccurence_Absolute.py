import pandas as pd
import numpy as np

# Lire le fichier CSV
data = pd.read_csv('Puppet_smells_all.csv')

# Sélectionner uniquement les colonnes de "code smells"
smell_columns = ['MultifacetedAbs', 'InsufficientMod', 'UnstructuredMod', 'TightlyCoupledMod', 'MissingDep',
                 'HairballStr', 'DeficientEnc', 'WeakendMod', 'ComplexExpression', 'DeprecatedStatement',
                 'IncompleteConditional', 'IncompleteTasks']

smells_data = data[smell_columns]
smells_data = smells_data.apply(lambda x: x >= 1).astype(int)

# Calculer la matrice de co-occurrence des code smells
cooccurrence_matrix = smells_data.T.dot(smells_data)

# Remplacer la diagonale par des zéros
np.fill_diagonal(cooccurrence_matrix.values, 0)

# Convertir la matrice en DataFrame
cooccurrence_df = pd.DataFrame(cooccurrence_matrix, index=smell_columns, columns=smell_columns)

# Écrire les résultats dans un nouveau fichier CSV
cooccurrence_df.to_csv('cooccurrence_matrix.csv')

print(cooccurrence_matrix)


