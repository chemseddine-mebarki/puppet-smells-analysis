from datetime import datetime, timezone, timedelta

import pandas as pd
import pytz
from pydriller import Repository

def getCreatedDt(created_at):
    created_at_str = created_at.strftime('%Y-%m-%d %H:%M:%S%z')
    return datetime.strptime(created_at_str, '%Y-%m-%d %H:%M:%S%z').replace(tzinfo=pytz.UTC)

def getUpdatedDt(updated_at):
    updated_at_str = updated_at.strftime('%Y-%m-%d %H:%M:%S%z')
    return datetime.strptime(updated_at_str, '%Y-%m-%d %H:%M:%S%z').replace(tzinfo=pytz.UTC)

def commits_dates(repo_url):
    first_commit = None
    last_commit = None
    try:
        for commit in Repository(repo_url).traverse_commits():
            if not first_commit:
                first_commit = commit
            last_commit = commit

        first_commit_date = first_commit.committer_date
        last_commit_date = last_commit.committer_date
    except Exception as e:
        # code to handle the exception
        print("Error:", e)
    return first_commit_date, last_commit_date


# Chargement du fichier CSV
df = pd.read_csv('filtered_repos.csv')

# Suppression des lignes avec commit_count < 1000 et sans "vagrant" dans l'URL
#df = df[(df['commit_count'] >= 1000) & (~df['URL'].str.contains('vagrant'))]

df = df[~df['URL'].str.contains('vagrant')]

treated_repos = 0
# Remplacement des valeurs de "created_at" et "updated_at"
for index, row in df.iterrows():
    try:
        repo_url = row["URL"]

        created_dt, updated_dt = commits_dates(repo_url)

        df.at[index, "created_at"] = created_dt
        df.at[index, "updated_at"] = updated_dt
        treated_repos+=1
        print("treated repos"+str(treated_repos))
        print("name repos" + str(repo_url))
    except Exception as e:
        # code to handle the exception
        print("Error:", e)


# replace values in created_at and updated_at columns with datetime objects
df['created_at'] = df['created_at'].apply(getCreatedDt)
df['updated_at'] = df['updated_at'].apply(getUpdatedDt)
# create new column repo_history with the difference between updated_at and created_at
df['repo_history'] = df['updated_at'] - df['created_at']

# remove rows with repo_history less than 3 years
#df = df[df['repo_history'] >= timedelta(days=1095)]

# Enregistrer le nouveau fichier CSV
df.to_csv('new_filtered_repos.csv', index=False)
