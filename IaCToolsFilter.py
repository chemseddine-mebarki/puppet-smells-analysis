from pydriller import Repository
import csv
import datetime

def is_repo_using_chef(modification):
    # Liste des fichiers fréquemment associés à Chef
    chef_files = [
        "cookbooks",
        "recipes",
        "roles",
        "attributes"
    ]
    # Démarrer le processus de minage de repository avec l'URL spécifiée
    try:
        if '.rb' in modification.filename:
            # Vérifier si l'un des fichiers associés à Chef est présent dans le commit
            for chef_file in chef_files:
                if chef_file in modification.new_path:
                    return True
    except Exception as e:
        # code to handle the exception
        print("Error:", e)
    # Si aucun fichier associé à Chef n'a été trouvé, retourner False
    return False



def is_repo_using_ansible(modification):
    # Liste des fichiers fréquemment associés à Chef
    ansible_files = [
        "playbooks",
        "inventory",
        "roles"
    ]
    # Démarrer le processus de minage de repository avec l'URL spécifiée
    try:
        if ('.yaml' in modification.filename) or ('.yml' in modification.filename):
            # Vérifier si l'un des fichiers associés à Ansible est présent dans le commit
            for ansible_file in ansible_files:
                if ansible_file in modification.new_path:
                    return True
    except Exception as e:
        # code to handle the exception
        print("Error:", e)
    # Si aucun fichier associé à Ansible n'a été trouvé, retourner False
    return False

def is_repo_using_helm(modification):
    use_helm = False
    helm_files = [
        "Chart.yaml",
        "Chart.yml"
    ]
    chart_name_folder = "charts"
    try:
        for helm_file in helm_files:
            if helm_file in modification.filename:
                if chart_name_folder in modification.new_path:
                    return True
    except Exception as e:
        # code to handle the exception
        print("Error:", e)
    return False

def is_repo_using_juju(modification):
    juju_files = [
        "charmcraft.yaml",
        "charm.py"
    ]
    try:
        for juju_file in juju_files:
            if juju_file in modification.filename:
                return True
    except Exception as e:
        # code to handle the exception
        print("Error:", e)
    return False

def is_repo_using_terraform(modification):
    if ('tf' in modification.filename) or ('tfvars' in modification.filename):
        return True
    return False

start = datetime.datetime.now()

chef_repos = []
ansible_repos = []
helm_repos = []
terraform_repos = []
juju_repos = []
filtered_repos = []

with open("filtered_puppets_repos.csv", "r") as input_file:
    reader = csv.DictReader(input_file)
    repos = [row for row in reader]
repos_counter = 0
for row in repos:
    try:
        processed_files = set()
        repo_processed = False
        repos_counter += 1
        for commit in Repository(row['URL']).traverse_commits():
            for modification in commit.modified_files:
                if modification.filename not in processed_files:
                    if is_repo_using_chef(modification):
                        chef_repos.append(row)
                        repo_processed = True
                        break
                    elif is_repo_using_ansible(modification):
                        ansible_repos.append(row)
                        repo_processed = True
                        break
                    elif is_repo_using_helm(modification):
                        helm_repos.append(row)
                        repo_processed = True
                        break
                    elif is_repo_using_terraform(modification):
                        terraform_repos.append(row)
                        repo_processed = True
                        break
                    elif is_repo_using_juju(modification):
                        juju_repos.append(row)
                        repo_processed = True
                        break
                    processed_files.add(modification.filename)
            if repo_processed:
                break
        if not repo_processed:
            filtered_repos.append(row)
    except Exception as e:
        # code to handle the exception
        print("Error:", e)

def write_to_csv(file_name, repo_list):
    with open(file_name, "w") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=repos[0].keys())
        writer.writeheader()
        writer.writerows(repo_list)

repo_lists = [
    ("chef_repos.csv", chef_repos),
    ("ansible_repos.csv", ansible_repos),
    ("helm_repos.csv", helm_repos),
    ("terraform_repos.csv", terraform_repos),
    ("juju_repos.csv", juju_repos),
    ("filtered_repos.csv", filtered_repos)
]

for repo_list in repo_lists:
    write_to_csv(*repo_list)

print("Number of total Chef repositories : ", len(chef_repos))
print("Number of total Ansible repositories : ", len(ansible_repos))
print("Number of total Helm repositories : ", len(helm_repos))
print("Number of total juju repositories : ", len(juju_repos))
print("Number of total terraform repositories : ", len(terraform_repos))

print("Number of total filtered repositories : ", len(filtered_repos))

end = datetime.datetime.now()
delta = end - start
hours, remainder = divmod(delta.seconds, 3600)
minutes, seconds = divmod(remainder, 60)
print("Execution time:", hours, "hours", minutes, "minutes", seconds, "seconds")
