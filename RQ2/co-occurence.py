import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, association_rules

# Charger le fichier CSV
data = pd.read_csv('Puppet_smells_all.csv')
data = data.drop(['URL', 'projectName', 'file_name', 'LOC', 'module'], axis=1)
data = pd.get_dummies(data)
data = data.astype(bool)

# Utiliser l'algorithme Apriori pour trouver les itemsets fréquents
#frequent_itemsets = apriori(data, min_support=0.00001,  use_colnames=True)
frequent_itemsets = apriori(data, min_support=0.004,  use_colnames=True)

# Calculer les règles d'association à partir des itemsets fréquents
rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1.0)
#rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.5)

# Filtrer les règles avec un minimum de confiance
'''min_confidence = 0.
rules['confidence'] = rules['confidence'].astype(float)
filtered_rules = rules[rules['confidence'] >= min_confidence]'''

# Sélectionner les paires 1 vs 1 de smells
pairs_1vs1 = rules[(rules['antecedents'].apply(lambda x: len(x)) == 1) & (rules['consequents'].apply(lambda x: len(x)) == 1)]

# Sélectionner les colonnes nécessaires
selected_columns = ['antecedents', 'consequents', 'support', 'confidence', 'lift', 'leverage', 'conviction']
pairs_1vs1 = pairs_1vs1[selected_columns]

# Convertir les colonnes 'antecedents' et 'consequents' en chaînes de caractères
pairs_1vs1['antecedents'] = pairs_1vs1['antecedents'].astype(str)
pairs_1vs1['consequents'] = pairs_1vs1['consequents'].astype(str)

# Nettoyer les valeurs des colonnes 'antecedents' et 'consequents'
pairs_1vs1['antecedents'] = pairs_1vs1['antecedents'].str.replace(r"frozenset\(\{'", "", regex=True).str.replace(r"'\}\)", "", regex=True)
pairs_1vs1['consequents'] = pairs_1vs1['consequents'].str.replace(r"frozenset\(\{'", "", regex=True).str.replace(r"'\}\)", "", regex=True)

# Enregistrer les résultats dans un fichier CSV
pairs_1vs1.to_csv('pairSmells.csv', index=False)

pairs_1vs1['smells_pairs'] = pairs_1vs1.apply(lambda row: '-'.join([row['antecedents'], row['consequents']]), axis=1)
pairs_1vs1 = pairs_1vs1.drop(['antecedents', 'consequents'], axis=1)
pairs_1vs1.insert(0, 'smells_pairs', pairs_1vs1.pop('smells_pairs'))
# Filter out pairs with NaN values
#df_results = df_results.dropna()
pairs_1vs1.to_csv('statsRQ2Paper.csv', index=False)


# Trouver la valeur de support qui couvre 80% de l'ensemble des lignes
'''support_threshold = pairs_1vs1['support'].quantile(0.2)
print('Nombre de pairs avant min support : '+str(len(pairs_1vs1)))
print('support_threshold : '+str(support_threshold))
# Filtrer les lignes avec un support supérieur ou égal au seuil
filtered_pairs_1vs1 = pairs_1vs1[pairs_1vs1['support'] >= support_threshold]
print('Nombre de pairs avec 80% support : '+str(len(filtered_pairs_1vs1)))'''





