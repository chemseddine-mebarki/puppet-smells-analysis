import csv

repos = []
#filtering criteria
min_commits = 20
min_size = 30
min_files_count = 30
is_fork = False

# Read the data from the CSV file
with open('puppet_projects.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        repos.append(row)

# Filter out the repos that meet the criteria
filtered_repos = [repo for repo in repos if int(repo['commit_count']) >= min_commits and int(repo['size']) >= min_size]

# Write the filtered repos to a new CSV file
with open('filtered_puppets_repos.csv', 'w', newline='') as f:
    fieldnames = ['Name', 'URL', 'forks', 'watchers', 'stars_count', 'created_at', 'updated_at', 'fork', 'size', 'commit_count']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for repo in filtered_repos:
        writer.writerow(repo)
