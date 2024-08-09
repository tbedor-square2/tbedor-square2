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

def branch_exists(branch_name):
    url = f"{GITHUB_API_URL}/repos/{REPO_OWNER}/{REPO_NAME}/branches/{branch_name}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)
    return response.status_code == 200

def create_branch(branch_name, base_branch="main"):
    url = f"{GITHUB_API_URL}/repos/{REPO_OWNER}/{REPO_NAME}/git/refs"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    base_branch_url = f"{GITHUB_API_URL}/repos/{REPO_OWNER}/{REPO_NAME}/git/refs/heads/{base_branch}"
    base_branch_response = requests.get(base_branch_url, headers=headers)
    base_branch_response.raise_for_status()
    base_sha = base_branch_response.json()["object"]["sha"]

    data = {
        "ref": f"refs/heads/{branch_name}",
        "sha": base_sha
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()

def make_commit(branch_name, file_path, commit_message, content):
    url = f"{GITHUB_API_URL}/repos/{REPO_OWNER}/{REPO_NAME}/contents/{file_path}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "message": commit_message,
        "content": content,
        "branch": branch_name
    }
    response = requests.put(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()

def create_pull_request(issue):
    branch_name = "feature-branch"
    if not branch_exists(branch_name):
        create_branch(branch_name)
        make_commit(branch_name, "new_file.txt", "Add new file", "U29tZSBjb250ZW50IGZvciB0aGUgbmV3IGZpbGUu")  # Base64 encoded content
    if not branch_exists(branch_name):
        create_branch(branch_name)
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
        issue_summary = get_issue_summary_prompt(issue)
        spawn_aider_session(issue_summary)
        create_pull_request(issue)

if __name__ == "__main__":
    main()
