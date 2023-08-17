import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Charger les fichiers CSV
df1 = pd.read_csv('PuppeteerSmells_All_RQ1.csv')
df2 = pd.read_csv('PuppetLintSmells_All__RQ1.csv')

# Renommer les colonnes
df2.rename(columns={'RepoName': 'projectName', 'File': 'file_name', 'Module': 'module'}, inplace=True)
# Ajouter les colonnes du fichier 2 au fichier 1
merged_df = pd.concat([df1, df2[df2.columns.difference(df1.columns)]], axis=1)
merged_df = merged_df.loc[:, ~merged_df.columns.str.contains('^Unnamed')]

# **********************************************************************************************
#************************** Retirer les smells qui sont vides **********************************
# **********************************************************************************************

smell_cols = merged_df.columns[6:]  # Colonnes spécifiques aux odeurs de code
cols_to_remove = []
for smell in smell_cols:
    if merged_df[smell].sum() == 0:
        cols_to_remove.append(smell)
merged_df_filtred = merged_df.drop(cols_to_remove, axis=1)
merged_df_filtred.fillna(0,inplace=True)
# Enregistrer les données fusionnées dans un nouveau fichier CSV
merged_df_filtred.to_csv("Puppet_smells_all.csv", index=False)


# Extraire les smells spécifiques aux fichiers Puppet
df_with_file = merged_df.dropna(subset=['file_name'])
#df_with_file.to_csv('Puppet_smells_filesSmells.csv', index=False)
# Extraire les  smells spécifiques aux modules Puppet
df_without_file = merged_df[merged_df['file_name'].isna()]
#df_without_file.to_csv('Puppet_smells_modulesSmells.csv', index=False)

'''# Liste des colonnes de smells
smells_columns = ['MultifacetedAbs', 'UnnecessaryAbs', 'ImperativeAbs', 'MissingAbs', 'InsufficientMod',
                  'UnstructuredMod', 'TightlyCoupledMod', 'DuplicateAbs', 'MissingDep', 'BrokenHie',
                  'HairballStr', 'DeficientEnc', 'WeakendMod', 'ComplexExpression', 'DeprecatedStatement',
                  'DuplicateEntity', 'ImproperAlignment', 'ImproperQuoteUsage', 'IncompleteConditional',
                  'IncompleteTasks', 'InconsistentNaming', 'InvalidProperty', 'LongStatement',
                  'MisplacedAttribute', 'MissingDefault', 'UnguardedVariable']

df_grouped = merged_df.drop_duplicates(subset=['URL', 'projectName', 'file_name', 'module', 'LOC'], keep='first')
df_grouped.to_csv('mergedSmells_grouped.csv', index=False)'''


# **********************************************************************************************
#******************************** Normaliser les smells par KLOC********************************
# **********************************************************************************************
df_normalized = df_with_file.copy()
# Calculer le nombre de KLOC (millier de lignes de code)
df_normalized["KLOC"] = df_normalized["LOC"] / 1000
columns_to_normalize = df_normalized.columns[5:-1]  # Sélectionner les colonnes de code smells à normaliser
df_normalized[columns_to_normalize+"_norm"] = df_normalized[columns_to_normalize].div(df_normalized["KLOC"], axis=0)
df_normalized = df_normalized.drop(columns=columns_to_normalize)
df_normalized.fillna(0,inplace=True)
#df_normalized.to_csv("fileSmells_KLOC.csv", index=False)


# **********************************************************************************************
#************************** Retirer les smells qui sont vides **********************************
# **********************************************************************************************
new_columns = [col.replace("_norm", "") for col in df_normalized.columns]
df_normalized.columns = new_columns
smell_cols = df_normalized.columns[7:]  # Colonnes contenant les code smells
cols_to_remove = []
for smell in smell_cols:
    if df_normalized[smell].sum() == 0:
        cols_to_remove.append(smell)
df_normalized_filtred = df_normalized.drop(cols_to_remove, axis=1)
df_normalized_filtred.to_csv("fileSmellsFiltred_KLOC.csv", index=False)


# **********************************************************************************************
#************************** Statistique diffusion de smells **********************************
# **********************************************************************************************
# Liste des numéros de colonnes correspondant aux odeurs de code
smell_cols = range(6, df_normalized_filtred.shape[1])
total_files = len(df_normalized_filtred["file_name"])
total_projects = len(df_normalized_filtred["URL"].unique())
# Calcul du nombre de fichiers affectés par chaque odeur de code
files_affected = {}
projects_affected = {}
for col in smell_cols:
    smell = df_normalized_filtred.columns[col]
    files_affected[smell] = df_normalized_filtred[df_normalized_filtred.iloc[:, col] > 0]["file_name"].count()/total_files*100
    projects_affected[smell] = df_normalized_filtred[df_normalized_filtred.iloc[:, col] > 0]["URL"].nunique()/int(total_projects)*100

print("\n******************** CALCUL DES POURCENTAGE DE FICHIERS ************************")
print(files_affected)
print("\n******************** CALCUL DES POURCENTAGE DE PROJETS ************************")
print(projects_affected)
print("\n******************** CALCUL DES POURCENTAGE DE SMELLS ************************")
# Sélection des colonnes contenant les noms de projets et les types de code smells
smell_cols = df_normalized_filtred.columns[6:]  # Exclure les colonnes non-smell
# Calcul du nombre total de chaque code smell
total_smells = df_normalized_filtred[smell_cols].sum()
# Calcul du pourcentage par rapport au total de tous les code smells
percentage_smells = total_smells / total_smells.sum() * 100
# Création d'un DataFrame pour stocker les résultats
result_df = pd.DataFrame({"Code Smell": smell_cols, "Nombre Total": total_smells, "% Total": percentage_smells})
# Affichage du DataFrame résultant
print(result_df)


# **********************************************************************************************
#************************************** Files Smells Summary ****************************************
# **********************************************************************************************
OUTPUT_COLUMNS = [
    "Projet", "MultifacetedAbs", "InsufficientMod",
    "TightlyCoupledMod", "WeakendMod", "ComplexExpression",
    "DeprecatedStatement", "IncompleteConditional", "IncompleteTasks"
]
# Calculer les totaux pour chaque projet
totals = {}
for _, row in df_normalized_filtred.iterrows():
    project = row["projectName"]
    if project not in totals:
        totals[project] = [0] * len(OUTPUT_COLUMNS)
        totals[project][0] = project
    for i in range(len(OUTPUT_COLUMNS) - 1):
        totals[project][i + 1] += int(row[i + 6])
# Créer le DataFrame de sortie
df_summary = pd.DataFrame.from_dict(totals, orient="index", columns=OUTPUT_COLUMNS)
df_summary.to_csv("summary_filtrered.csv", index=False)



# **************************************************************************************************
#****** Graphique de densité des smells par KLOC ******
# **************************************************************************************************
project_col = "Projet"
smell_cols = df_summary.columns[1:]
df = pd.melt(df_summary, id_vars=[project_col], value_vars=smell_cols, var_name="Odeur de code", value_name="Nombre d'odeurs")
# Création du graphique beanplot
sns.set(style="whitegrid")
sns.catplot(x="Odeur de code", y="Nombre d'odeurs", data=df, kind="violin", height=6, aspect=2)
# Affichage du graphique
sns.despine(left=True)
plt.xticks(rotation=90)
plt.savefig("RQ1_density_KLOC.png")
plt.show()

'''
# Liste des colonnes de code smells
smell_cols = df_summary.columns[1:]
# Transformation des données pour les utiliser avec la fonction de tracé de Seaborn
df_melted = pd.melt(df_summary, value_vars=smell_cols, var_name="Type de smell", value_name="Nombre de smells")
# Création du graphique beanplot
plt.figure(figsize=(12, 6))
sns.violinplot(x="Type de smell", y="Nombre de smells", data=df_melted)
plt.xlabel("Type de smell")
plt.ylabel("Nombre de smells")
plt.title("Distribution du nombre de code smells")
# Rotation des étiquettes des types de smell pour une meilleure lisibilité
plt.xticks(rotation=90)
# Affichage du graphique
plt.show()'''


# **************************************************************************************************
#****** Graphique nombre absolu de smells ******
# **************************************************************************************************
# Calcul du nombre total de code smells pour chaque type
smell_cols = merged_df_filtred.columns[5:]  # Colonnes contenant les code smells
cols_to_remove = []
for smell in smell_cols:
    if merged_df_filtred[smell].sum() == 0:
        cols_to_remove.append(smell)
merged_df_filtred_2 = merged_df_filtred.drop(cols_to_remove, axis=1)
merged_df_filtred_2.to_csv("merged_df_filtred_2.csv", index=False)
smell_cols = merged_df_filtred_2.columns[5:]
smell_counts = merged_df_filtred_2[smell_cols].sum()
# Création du graphique countplot
plt.figure(figsize=(12, 6))
sns.barplot(x=smell_cols, y=smell_counts)
plt.xlabel("Type d'odeur de code")
plt.ylabel("Nombre d'odeur de code")
plt.title("Nombre absolu d'odeur de code dans les projets étudiés")
# Rotation des étiquettes des types de smell pour une meilleure lisibilité
plt.xticks(rotation=90)
# Affichage du graphique
plt.show()


# **************************************************************************************************
#****** Calcul du nombre de fichiers affectés par chaque smells pour chaque projet ******
# **************************************************************************************************
smell_cols = df_normalized_filtred.columns[6:]
resultats = {}
for _, row in df_normalized_filtred.iterrows():
    projet = row["projectName"]
    if projet not in resultats:
        resultats[projet] = {}

    for col in smell_cols:
        code_smell = col.strip()
        if code_smell not in resultats[projet]:
            resultats[projet][code_smell] = 0

        if row[col] > 0:
            resultats[projet][code_smell] += 1

df_resultats_files = pd.DataFrame.from_dict(resultats, orient="index")
df_resultats_files = df_resultats_files.reset_index().rename(columns={"index": "projet"})
#df_resultats_files.to_csv("affected_files.csv", index=False)




# **************************************************************************************************
#****** Graphique du nombre de fichiers affectés par chaque smells pour chaque projet ******
# **************************************************************************************************
smell_cols = df_resultats_files.columns[1:]
df_melted = pd.melt(df_resultats_files, id_vars=["projet"], value_vars=smell_cols, var_name="Type de smell", value_name="Nombre de fichiers affectés")
sns.set(style="whitegrid")
plt.figure(figsize=(12, 6))
sns.violinplot(x="Type de smell", y="Nombre de fichiers affectés", data=df_melted, inner="quartile")
plt.xticks(rotation=90)
plt.xlabel("Type de smell")
plt.ylabel("Nombre de fichiers affectés")
plt.title("Avg number of files affected by each code smell type")
# Affichage du graphique
plt.savefig("RQ1_AVG_Affected_Files.png")
plt.show()








