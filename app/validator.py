def validate_comments(comments):
    filtered = []

    for comment in comments:
        issue_text = comment.get("issue", "").lower()

        # reject low confidence
        if is_weak_pattern_issue(issue_text) and comment.get("confidence", 0) < 0.85:
            continue

        filtered.append(comment)

    return filtered


def is_weak_pattern_issue(issue_text):
    patterns = [
        "inconsistent with",
        "similar files",
        "pattern in other files",
        "could be improved",
        "better error message"
    ]

    return any(p in issue_text.lower() for p in patterns)