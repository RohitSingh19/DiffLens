import json

FILE = "processed_commits.json"

def load():
    try:
        with open(FILE, "r") as f:
            return set(json.load(f))
    except:
        return set()

def save(data):
    with open(FILE, "w") as f:
        json.dump(list(data), f)

processed_commits = load()

def mark_processed(commit_id):
    processed_commits.add(commit_id)
    save(processed_commits)

def is_already_processed(commit_id):
    return commit_id in processed_commits
