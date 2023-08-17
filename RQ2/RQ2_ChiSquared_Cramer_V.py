import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency

data = pd.read_csv('Puppet_smells_all.csv')

# Create dummy variables
data = data.drop(['URL', 'projectName', 'file_name', 'module', 'LOC'], axis=1)
data = pd.get_dummies(data)
data = data.astype(bool)

# Find all pairs of columns
column_pairs = [(data.columns[i], data.columns[j]) for i in range(len(data.columns)) for j in range(i+1, len(data.columns))]

# Calculate Chi-squared and Cramer's V for each pair
results = []
for pair in column_pairs:
    contingency_table = pd.crosstab(data[pair[0]], data[pair[1]])
    if contingency_table.isnull().values.any():
        results.append((pair[0], pair[1], np.nan, np.nan))
        continue
    chi2, p, dof, expected = chi2_contingency(contingency_table)
    n = contingency_table.sum().sum()
    v = np.nan if (min(contingency_table.shape) - 1) == 0 or np.isnan(chi2) else np.sqrt(chi2 / (n * (min(contingency_table.shape) - 1)))
    if p < 0.0001:
        p_text = '<0.00001'
    else:
        p_text = str(p)
    results.append((pair[0], pair[1], chi2, p, v))

# Create DataFrame of results
df_results = pd.DataFrame(results, columns=['smell1', 'smell2', 'chi2', 'Chi2 p-value', 'cramers_v'])
#df_results = df_results.dropna()
#print(df_results)


# Charger le fichier "pairSmells.csv"
pair_smells = pd.read_csv('pairSmells.csv')
pair_list = list(zip(pair_smells['antecedents'], pair_smells['consequents']))
# Filtrer les lignes de df_results où la paire 'smell1', 'smell2' ne se trouve pas dans pairSmells
filtered_df = df_results[df_results.apply(lambda row: (row['smell1'], row['smell2']) in pair_list, axis=1)]
#filtered_df = filtered_df.dropna()
print(filtered_df)
filtered_df.to_csv('RQ2_ChiSquared_CramerV.csv', index=False)

filtered_df['smells_pairs'] = filtered_df.apply(lambda row: '-'.join([row['smell1'], row['smell2']]), axis=1)
filtered_df = filtered_df.drop(['smell1', 'smell2'], axis=1)
filtered_df.insert(0, 'smells_pairs', filtered_df.pop('smells_pairs'))
filtered_df.to_csv('RQ2_ChiSquared_CramerV.csv', index=False)

'''
# Charger le fichier "pairSmells.csv"
pair_smells = pd.read_csv('pairSmells.csv')
# Créer une liste de tuples contenant les paires 'antecedents', 'consequents' présentes dans pairSmells
pair_list = list(zip(pair_smells['antecedents'], pair_smells['consequents']))
# Filtrer les lignes de df_results où la paire 'smell1', 'smell2' ne se trouve pas dans pairSmells
filtered_df = df_results[df_results.apply(lambda row: (row['smell1'], row['smell2']) in pair_list, axis=1)]
filtered_df = filtered_df.dropna()
print(filtered_df)'''



