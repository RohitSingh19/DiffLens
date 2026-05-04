def decide_review(comments):
    high = sum(1 for c in comments if c["severity"] == "HIGH")
    medium = sum(1 for c in comments if c["severity"] == "MEDIUM")

    if high > 0:
        return "REQUEST_CHANGES"

    if medium >= 3:
        return "REQUEST_CHANGES"

    if len(comments) == 0:
        return "APPROVE"

    return "COMMENT"