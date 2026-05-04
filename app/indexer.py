import requests
import os
from app.chunker import chunk_code
from app.vector_store import VectorStore
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


def fetch_repo_files(owner, repo, branch="main"):
    """
    Fetch all repo files recursively (basic version)
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch repo tree: {response.text}")

    data = response.json()

    files = [
        item["path"]
        for item in data["tree"]
        if item["type"] == "blob"
        and item["path"].endswith((".ts", ".js", ".py"))
    ]

    return files


def fetch_file_content(owner, repo, path, branch="main"):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={branch}"

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return ""

    data = response.json()

    if "content" not in data:
        return ""

    import base64
    return base64.b64decode(data["content"]).decode("utf-8")


def build_vector_index(owner, repo):
    store = VectorStore()

    print("Fetching repo file list...")
    files = fetch_repo_files(owner, repo)

    print(f"Found {len(files)} files")

    for file_path in files[:50]:  # limit for now
        try:
            content = fetch_file_content(owner, repo, file_path)

            if not content.strip():
                continue

            chunks = chunk_code(file_path, content, chunk_size=40)

            store.add_chunks(chunks)

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    print("Indexing complete.")