from app.indexer import build_vector_index

if __name__ == "__main__":
    owner = ""
    repo = ""
    print(f"Building vector index for {owner}/{repo}...")
    build_vector_index(owner, repo)