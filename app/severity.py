def normalize_severity(comment):
    issue = comment.get("issue", "").lower()

    high_patterns = [
        "sql injection",
        "hardcoded secret",
        "authentication bypass",
        "authorization issue",
        "data exposure",
        "sensitive data",
        "security vulnerability",
        "application crash",
        "critical null reference"
    ]

    medium_patterns = [
        "missing error handling",
        "form submission state",
        "duplicate submission",
        "null reference",
        "input validation",
        "retry handling",
        "http request failure",
        "state inconsistency",
        "submission failure"
    ]

    low_patterns = [
        "error message",
        "validation message",
        "wording",
        "user feedback",
        "logging improvement",
        "could be improved",
        "better message",
        "optional improvement",
        "minor maintainability"
    ]

    if any(p in issue for p in high_patterns):
        comment["severity"] = "HIGH"
        return comment

    if any(p in issue for p in medium_patterns):
        comment["severity"] = "MEDIUM"
        return comment

    if any(p in issue for p in low_patterns):
        comment["severity"] = "LOW"
        return comment

    # fallback
    comment["severity"] = "MEDIUM"
    return comment

def severity_priority(severity):
    mapping = {
        "HIGH": 3,
        "MEDIUM": 2,
        "LOW": 1
    }
    return mapping.get(severity, 0)