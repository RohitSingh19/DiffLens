import threading

from fastapi import FastAPI, File, HTTPException, Request, UploadFile, logger
from app.analyzer import analyze_diff
from app.github import fetch_pr_diff
from app.models import ReviewPRRequest
from app.github_review import create_review, post_review_comment
from app.github import fetch_pr_details
from app.review_decision import decide_review
from app.review_state import is_already_processed
from app.security import verify_signature
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = FastAPI()


@app.get("/")
def health():
    return {"status": "healthy"}


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    content = await file.read()
    diff = content.decode("utf-8")
    
    result = analyze_diff(diff)
    return {"comments": result}

@app.post("/review-pr")
def review_pr(request: ReviewPRRequest):
    diff = fetch_pr_diff(request.owner, request.repo, request.pull_number)

    comments = analyze_diff(
        full_diff=diff,
        owner=request.owner,
        repo=request.repo
    )

    # Get commit SHA
    pr_data = fetch_pr_details(request.owner, request.repo, request.pull_number)
    commit_id = pr_data["head"]["sha"]
    pr_author = pr_data["user"]["login"]

    decision = decide_review(comments)

    if decision == "REQUEST_CHANGES" and pr_author == request.owner:
        decision = "COMMENT"

    create_review(
        owner=request.owner,
        repo=request.repo,
        pull_number=request.pull_number,
        commit_id=commit_id,
        comments=comments,
        decision=decision
    )

    return {
        "pull_request": request.pull_number,
        "comments_posted": len(comments),
        "review_decision": decision
    }


def process_review(owner, repo, pull_number, commit_id):
    diff = fetch_pr_diff(owner, repo, pull_number)
    comments = analyze_diff(diff, owner, repo)
    decision = decide_review(comments)

    if decision == "REQUEST_CHANGES":
        decision = "COMMENT"

    comments = unique_comments(comments)
    comments = [
        c for c in comments
        if c["severity"] in ["HIGH", "MEDIUM"]
    ][:3] # limit to top 3 comments with HIGH/MEDIUM severity

    create_review(owner, repo, pull_number, commit_id, comments, decision)


@app.post("/webhook")
async def github_webhook(request: Request):
    logger.info("Received webhook event")
    
    body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256")

    
    if not verify_signature(body, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    payload = await request.json()

    if payload.get("action") not in ["opened", "synchronize"]:
        return {"message": "Ignored"}

    pr = payload["pull_request"]

    owner = payload["repository"]["owner"]["login"]
    repo = payload["repository"]["name"]
    pull_number = pr["number"]
    commit_id = pr["head"]["sha"]

    if is_already_processed(commit_id):
        logger.info("Already processed this commit, skipping.")
        return {"message": "Already processed"}
    
    threading.Thread(
        target=process_review,
        args=(owner, repo, pull_number, commit_id)
    ).start()

    return {"message": "Processing in background"}



def unique_comments(comments):
    seen = set()
    result = []

    for c in comments:
        key = (c["file"], c["line"], c["issue"])
        if key not in seen:
            seen.add(key)
            result.append(c)

    return result