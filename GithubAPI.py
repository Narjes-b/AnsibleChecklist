from github import Github
import os
# Create a Github instance by providing your personal access token
# Replace 'YOUR_ACCESS_YOUR_ACCESS_TOKENTOKEN' with your actual access token
g = Github('YOUR_ACCESS_TOKEN')

# Get a specific repository by its full name (owner/repo)
repo = g.get_repo('openstack/ansible-config_template')

project= "ansible-config_template"
# Get all pull requests from the repository
pull_requests = repo.get_pulls(state='all')
#print('Number of pull requests:', pull_requests)
# Initialize counters for open and closed pull requests
open_count = 0
closed_count = 0

# Iterate over the pull requests and count the number of open and closed ones
for pr in pull_requests:
    if pr.state == 'open':
        open_count += 1
    elif pr.state == 'closed':
        closed_count += 1

# Print the results
print('Number of open pull requests:', open_count)
print('Number of closed pull requests:', closed_count)




# Retrieve the number of pull requests
pull_requests_count = repo.get_pulls().totalCount
print('Number of pull requests:', pull_requests_count)

# Retrieve the number of contributors
contributors_count = repo.get_contributors(anon="false").totalCount
print('Number of contributors:', contributors_count)

# Retrieve the number of developers (by counting unique authors of commits)

# Retrieve the list of commit authors
commit_authors = [commit.author for commit in repo.get_commits()]
print('List of commit authors:', commit_authors)

# Count the number of unique commit authors
#developers_count = len(set(commit_authors))
#print('Number of developers:', developers_count)

# Filter out bot accounts from the list of commit authors
commit_authors = [author for author in commit_authors if author and author.type != 'Bot']

# Count the number of unique commit authors (excluding bots)
developers_count = len(set(commit_authors))
print('Number of developers (excluding bots):', developers_count)


developers_count = len(list(repo.get_commits(author='all')))
print('Number of developers:', developers_count)

# Get the total number of commits in the repository
commit_count = repo.get_commits().totalCount

# Print the number of commits
print("number of commits",commit_count)
