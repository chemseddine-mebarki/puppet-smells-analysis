import requests
import csv
from datetime import datetime
from dateutil.relativedelta import relativedelta
import math
from pydriller import Repository
from numpy import random
from random import randint
from time import sleep

# Set the headers for the API request
headers = {
    'Accept': 'application/vnd.github+json',
    'User-Agent': 'request',
    'Authorization': 'token ' + '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'
}

starting_date = '2012-01-01'
language = 'Puppet'
page = 1
total_repositories = 0

def increment_month(date_string):
    date_object = datetime.strptime(date_string, '%Y-%m-%d')
    incremented_date = date_object + relativedelta(months=1)
    formatted_date = incremented_date.strftime('%Y-%m-%d')
    return formatted_date

def getNumberOfRepositories(selected_date):
    response = requests.get(f"https://api.github.com/search/repositories?q=language:puppet%20created:"+selected_date+".."+increment_month(selected_date)+"&page=1&per_page=100",
                            headers=headers)
    # Parse the JSON response
    data = response.json()
    print('count_repositories: ' + str(data['total_count']))
    return data['total_count']


def count_commits(repo_url):
    # Initialiser le compteur de commits à zéro
    commit_count = 0
    total_file_count = 0
    pp_file_count = 0
    files = set()
    try:
        # Miner le repository pour les commits
        for commit in Repository(repo_url).traverse_commits():
            commit_count += 1
            for modification in commit.modified_files:
                if modification.filename not in files:
                    files.add(modification.filename)
                    total_file_count += 1
                    if ".pp" in modification.filename:
                        pp_file_count += 1
    except Exception as e:
        # code to handle the exception
        print("Error:", e)
    return total_file_count, pp_file_count, commit_count

# Open the file for writing
with open('puppet_projects.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    # Write the header row
    writer.writerow(['Name', 'URL', 'forks', 'watchers', 'stars_count', 'created_at', 'updated_at', 'fork', 'size', 'commit_count', 'files_count', 'pp_files_count'])

    while datetime.strptime(starting_date, "%Y-%m-%d") < datetime.now():
        print('starting_date ' + starting_date)

        # Set the number of pages to retrieve
        nb_repos = getNumberOfRepositories(starting_date)
        pages = to_page_index = math.ceil(nb_repos / 100)
        print('Nombre de pages ' +str(pages))

        total_repositories = total_repositories + nb_repos
        print('total_repositories: ' + str(total_repositories))

        while page <= pages:
            print('Fetched GitHub page: ' + str(page))

            response = requests.get(
                f"https://api.github.com/search/repositories?q=language:puppet%20created:" + starting_date + ".." + increment_month(
                    starting_date) + "&page=" + str(page) + "&per_page=100",
                headers=headers)

            # Check if the request was successful
            if response.status_code == 200:
                # Parse the JSON response
                data = response.json()
                # Iterate over the items in the response
                for item in data['items']:
                    total_file_count, pp_file_count, commit_count = count_commits(item['html_url'])
                    # Write the rows with repository name and URL
                    writer.writerow([item['name'], item['html_url'], item['forks'], item['watchers'], item['stargazers_count'], item['created_at'], item['updated_at'], item['fork'], item['size'], commit_count, total_file_count, pp_file_count])
                    #sleep(randint(5, 20))
            else:
                print("Error:", response.status_code)
                #sleep(randint(10, 60))

            page += 1

        starting_date = increment_month(starting_date)
        page = 1

print("File saved successfully!")





