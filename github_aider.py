import requests
import subprocess
import os

# Constants
GITHUB_API_URL = "https://api.github.com"
REPO_OWNER = "your-repo-owner"
REPO_NAME = "your-repo-name"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

def get_issues():
    url = f"{GITHUB_API_URL}/repos/{REPO_OWNER}/{REPO_NAME}/issues"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def filter_issues(issues):
    return [issue for issue in issues if "aider" in [label['name'] for label in issue['labels']] and issue['state'] == 'open']

def spawn_aider_session(issue):
    # Assuming aider is a command line tool that can be invoked with subprocess
    command = ["aider", "--write-pytest", issue['html_url']]
    subprocess.run(command)

def create_pull_request(issue):
    url = f"{GITHUB_API_URL}/repos/{REPO_OWNER}/{REPO_NAME}/pulls"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "title": f"Fix for issue #{issue['number']}",
        "head": "feature-branch",
        "base": "main",
        "body": f"Automated fix for issue #{issue['number']}"
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()

def main():
    issues = get_issues()
    aider_issues = filter_issues(issues)
    for issue in aider_issues:
        spawn_aider_session(issue)
        create_pull_request(issue)

if __name__ == "__main__":
    main()
