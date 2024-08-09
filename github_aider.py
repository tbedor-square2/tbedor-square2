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
    
    coder = Coder.create(main_model=Model("gpt-4o"))
    
    coder.run(prompt)

def checkout_branch(branch_name, base_branch="main"):
    subprocess.run(["git", "checkout", "-b", branch_name, f"origin/{base_branch}"], check=True)

def commit_changes(file_path, commit_message):
    subprocess.run(["git", "add", file_path], check=True)
    subprocess.run(["git", "commit", "-m", commit_message], check=True)

def push_branch(branch_name):
    subprocess.run(["git", "push", "-u", "origin", branch_name], check=True)


    

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
    print(f"Creating pull request with data: {data}")
    response = requests.post(url, headers=headers, json=data)
    print(f"Response Status Code: {response.status_code}")
    print(f"Response Content: {response.content}")
    response.raise_for_status()
    return response.json()

def get_issue_summary_prompt(issue):
    """
    Convert the issue API response into a textual summary of what the issue is.
    """
    title = issue.get('title', 'No title')
    body = issue.get('body', 'No description')
    issue_number = issue.get('number', 'No number')
    labels = [label['name'] for label in issue.get('labels', [])]
    state = issue.get('state', 'No state')

    summary = (
        f"Issue #{issue_number}\n"
        f"Title: {title}\n"
        f"Description: {body}\n"
        f"Labels: {', '.join(labels)}\n"
        f"State: {state}\n"
    )
    return summary

def main():
    issues = get_issues()
    aider_issues = filter_issues(issues)
    for issue in aider_issues:
        branch_name = f"feature-branch-for-issue-{issue['number']}"
        checkout_branch(branch_name)
        issue_summary = get_issue_summary_prompt(issue)
        spawn_aider_session(issue_summary)
        commit_changes("new_file.txt", f"Add new file for issue #{issue['number']}")
        push_branch(branch_name)
        issue_summary = get_issue_summary_prompt(issue)
        spawn_aider_session(issue_summary)
        create_pull_request(issue)

if __name__ == "__main__":
    main()
