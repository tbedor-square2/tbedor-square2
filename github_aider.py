import requests
import subprocess
import os

# Constants
GITHUB_API_URL = "https://api.github.com"
REPO_OWNER = "tbedor-square2"
REPO_NAME = "tbedor-square2"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

def get_issues():
    url = f"{GITHUB_API_URL}/repos/{REPO_OWNER}/{REPO_NAME}/issues"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    print(f"Requesting URL: {url}")
    response = requests.get(url, headers=headers)
    print(f"Response Status Code: {response.status_code}")
    response.raise_for_status()
    return response.json()

def filter_issues(issues):
    return [issue for issue in issues if "aider" in [label['name'] for label in issue['labels']] and issue['state'] == 'open']

def spawn_aider_session(prompt):
    
    from aider.coders import Coder
    from aider.models import Model
    
    import pdb; pdb.set_trace()
    
    coder = Coder.create(main_model=Model("gpt-4o"))
    
    coder.run(prompt)

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

def get_issue_summary_prompt(issue):
    """TODO"""

def main():
    issues = get_issues()
    aider_issues = filter_issues(issues)
    for issue in aider_issues:
        issue_summary = get_issue_summary_prompt(issue)
        spawn_aider_session(issue_summary)
        create_pull_request(issue)

if __name__ == "__main__":
    main()
