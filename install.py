import os
import shutil

# Make paths
home = os.path.expanduser('~')
slrg = os.path.join(home, '.slrg')
conf = os.path.join(slrg, 'config.py')
logs = os.path.join(slrg, 'logs')
cf_logs = os.path.join(logs, 'codeforces')
git_commit_logs = os.path.join(logs, 'git_commits')
git_project_logs = os.path.join(logs, 'git_projects')

# Make directories
os.mkdir(slrg)
os.mkdir(logs)
os.mkdir(cf_logs)
os.mkdir(git_commit_logs)
os.mkdir(git_project_logs)

# Copy over config file
shutil.copy('config.py', slrg)

# At some point you could ask some questions for config
print("Install Successfull!")
print("Config file and log directories located in:", slrg)
