from importlib.resources import files

import requests
import os
from app.embedder import CodeEmbedder
from app import embedder
from app import vector_store
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

def build_vector_index(owner: str, repo: str):
    repo_key = f"{owner}_{repo}"

    vector_store = VectorStore(repo_key)
    embedder = CodeEmbedder()  
    
    files = fetch_repo_files(owner, repo)

    for file in files[:50]:
        content = fetch_file_content(owner, repo, file)

        chunks = chunk_code(file, content, chunk_size=40)

        chunk_texts = [chunk["content"] for chunk in chunks]
        
        chunk_ids = [chunk["id"] for chunk in chunks]

        embeddings = embedder.generate_embeddings(chunk_texts)

        vector_store.collection.add(
            ids=chunk_ids,
            documents=chunk_texts,
            embeddings=embeddings,
            metadatas=chunks
        )

def is_index_empty(vector_store):
    return vector_store.collection.count() == 0