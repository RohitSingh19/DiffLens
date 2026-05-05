import os
import logging
import requests
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
logger = logging.getLogger(__name__)


def post_review_comment(owner, repo, pull_number, commit_id, comment):
    """
    Post inline comment to PR
    """

    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}/comments"

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    payload = {
        "body": format_comment_body(comment),
        "commit_id": commit_id,
        "path": comment["file"],
        "line": comment["line"],
        "side": "RIGHT"
    }

    logger.info(
        "github_review.post_review_comment.start owner=%s repo=%s pull_number=%s commit_id=%s file=%s line=%s",
        owner,
        repo,
        pull_number,
        commit_id,
        comment["file"],
        comment["line"]
    )

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 201:
        logger.error(
            "github_review.post_review_comment.failed owner=%s repo=%s pull_number=%s commit_id=%s status_code=%s response=%s",
            owner,
            repo,
            pull_number,
            commit_id,
            response.status_code,
            response.text
        )
    else:
        logger.info(
            "github_review.post_review_comment.done owner=%s repo=%s pull_number=%s commit_id=%s file=%s line=%s",
            owner,
            repo,
            pull_number,
            commit_id,
            comment["file"],
            comment["line"]
        )

def create_review(owner, repo, pull_number, commit_id, comments, decision):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}/reviews"

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    review_comments = [
        {
            "path": c["file"],
            "line": c["line"],
            "side": "RIGHT",
            "body": format_comment_body(c)
        }
        for c in comments
    ]

    payload = {
        "commit_id": commit_id,
        "event": decision,
        "comments": review_comments
    }

    logger.info(
        "github_review.create_review.start owner=%s repo=%s pull_number=%s commit_id=%s decision=%s comments=%s",
        owner,
        repo,
        pull_number,
        commit_id,
        decision,
        len(review_comments)
    )

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code not in [200, 201]:
        logger.error(
            "github_review.create_review.failed owner=%s repo=%s pull_number=%s commit_id=%s status_code=%s response=%s",
            owner,
            repo,
            pull_number,
            commit_id,
            response.status_code,
            response.text
        )
    else:
        logger.info(
            "github_review.create_review.done owner=%s repo=%s pull_number=%s commit_id=%s decision=%s comments=%s",
            owner,
            repo,
            pull_number,
            commit_id,
            decision,
            len(review_comments)
        )

def format_comment_body(comment):
    return f"""
    **AI Code Review**

    **Issue:** {comment['issue']}

    **Suggestion:** {comment['suggestion']}

    **Severity:** {comment['severity']}
    **Confidence:** {comment['confidence']}
    """