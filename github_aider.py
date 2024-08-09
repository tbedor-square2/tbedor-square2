import subprocess
import subprocess
import os
import json

# Constants
GITHUB_API_URL = "https://api.github.com"
REPO_OWNER = "tbedor-square2"
REPO_NAME = "tbedor-square2"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

def get_issues():
    try:
        result = subprocess.run(
            ["gh", "issue", "list", "--repo", f"{REPO_OWNER}/{REPO_NAME}", "--state", "open", "--json", "number,title,body,labels,state"],
            capture_output=True, text=True, check=True
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print(f"Output: {e.output}")
        print(f"Stderr: {e.stderr}")
        raise

def filter_issues(issues):  
    import pdb; pdb.set_trace()
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



def create_pull_request(issue, branch_name):
    subprocess.run([
        "gh", "pr", "create",
        "--repo", f"{REPO_OWNER}/{REPO_NAME}",
        "--head", branch_name,
        "--base", "main",
        "--title", f"Fix for issue #{issue['number']}",
        "--body", f"Automated fix for issue #{issue['number']}"
    ], check=True)

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
    print(f"Total issues found: {len(issues)}")
    aider_issues = issues #filter_issues(issues)
    print(f"Total aider issues found: {len(aider_issues)}")
    for issue in aider_issues:
        branch_name = f"feature-branch-for-issue-{issue['number']}"
        checkout_branch(branch_name)
        issue_summary = get_issue_summary_prompt(issue)
        spawn_aider_session(issue_summary)
        push_branch(branch_name)
        issue_summary = get_issue_summary_prompt(issue)
        spawn_aider_session(issue_summary)
        create_pull_request(issue, branch_name)

if __name__ == "__main__":
    main()
