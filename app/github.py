import base64
import os
import logging
import requests
from dotenv import load_dotenv

load_dotenv()


GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
logger = logging.getLogger(__name__)

def fetch_file_content(owner: str, repo: str, file_path: str, branch: str = "improvement"):
    logger.info(
        "github.fetch_file_content.start owner=%s repo=%s file_path=%s branch=%s",
        owner,
        repo,
        file_path,
        branch
    )

    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}?ref={branch}"

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        logger.warning(
            "github.fetch_file_content.failed owner=%s repo=%s file_path=%s status_code=%s",
            owner,
            repo,
            file_path,
            response.status_code
        )
        return ""

    data = response.json()

    if "content" not in data:
        return ""

    encoded_content = data["content"]
    decoded_content = base64.b64decode(encoded_content).decode("utf-8")

    logger.info(
        "github.fetch_file_content.done owner=%s repo=%s file_path=%s content_length=%s",
        owner,
        repo,
        file_path,
        len(decoded_content)
    )

    return decoded_content

def fetch_pr_diff(owner: str, repo: str, pull_number: int) -> str:
    logger.info(
        "github.fetch_pr_diff.start owner=%s repo=%s pull_number=%s",
        owner,
        repo,
        pull_number
    )
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}"

    headers = { 
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3.diff"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        logger.error(
            "github.fetch_pr_diff.failed owner=%s repo=%s pull_number=%s status_code=%s",
            owner,
            repo,
            pull_number,
            response.status_code
        )
        raise Exception(
            f"GitHub API failed: {response.status_code} - {response.text}"
        )

    logger.info(
        "github.fetch_pr_diff.done owner=%s repo=%s pull_number=%s diff_length=%s",
        owner,
        repo,
        pull_number,
        len(response.text)
    )

    return response.text


def fetch_pr_details(owner, repo, pull_number):
    logger.info(
        "github.fetch_pr_details.start owner=%s repo=%s pull_number=%s",
        owner,
        repo,
        pull_number
    )
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}"

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        logger.error(
            "github.fetch_pr_details.failed owner=%s repo=%s pull_number=%s status_code=%s",
            owner,
            repo,
            pull_number,
            response.status_code
        )
        raise Exception("Failed to fetch PR details")

    logger.info(
        "github.fetch_pr_details.done owner=%s repo=%s pull_number=%s",
        owner,
        repo,
        pull_number
    )

    return response.json()