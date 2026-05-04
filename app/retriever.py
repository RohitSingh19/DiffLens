import os
import re
from app.github import fetch_file_content


def retrieve_related_context(owner, repo, file_content, current_file):
    import_paths = extract_import_paths(file_content)
    candidate_files = [resolve_import_path(current_file, path) for path in import_paths]

    related_context = []

    for file_path in candidate_files[:3]:
        content = fetch_file_content(owner, repo, file_path)

        if content:
            related_context.append({
                "file": file_path,
                "content": content[:3000]  # prevent token explosion
            })

    return related_context


def resolve_import_path(current_file: str, import_path: str):
    """
    Resolve relative import to repo absolute path

    Example:
    current_file = src/app/features/contact/contact.component.ts
    import_path = ../../core/services/contact.service

    Result:
    src/app/core/services/contact.service.ts
    """

    # Get directory of current file
    base_dir = os.path.dirname(current_file)

    # Join and normalize path
    full_path = os.path.normpath(os.path.join(base_dir, import_path))

    # Add extension if missing
    if not full_path.endswith(".ts"):
        full_path += ".ts"

    # convert Windows path to POSIX
    full_path = full_path.replace("\\", "/")

    return full_path

def extract_import_paths(file_content: str):
    """
    Extract relative import paths from TS/JS files

    Example:
    import { ContactService } from '../../core/services/contact.service';

    Returns:
    [
        '../../core/services/contact.service'
    ]
    """

    pattern = r"from\s+['\"](.+?)['\"]"

    matches = re.findall(pattern, file_content)

    # Keep only local relative imports
    local_imports = [
        match for match in matches
        if match.startswith(".")
    ]

    return local_imports