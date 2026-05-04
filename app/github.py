import base64
import os
import requests
from dotenv import load_dotenv

load_dotenv()


GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

def fetch_file_content(owner: str, repo: str, file_path: str, branch: str = "improvement"):
    
    print(f"Fetching file: {file_path}")

    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}?ref={branch}"

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Could not fetch file: {file_path}")
        return ""

    data = response.json()

    if "content" not in data:
        return ""

    encoded_content = data["content"]
    decoded_content = base64.b64decode(encoded_content).decode("utf-8")

    return decoded_content

def fetch_pr_diff(owner: str, repo: str, pull_number: int) -> str:
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}"

    headers = { 
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3.diff"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(
            f"GitHub API failed: {response.status_code} - {response.text}"
        )

    return response.text


def fetch_pr_details(owner, repo, pull_number):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}"

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception("Failed to fetch PR details")

    return response.json()