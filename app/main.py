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
from app.indexer import build_vector_index
from app.vector_store import VectorStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = FastAPI()


@app.get("/health")
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
    
    try:

        repo_key = f"{owner}_{repo}"
        vector_store = VectorStore(repo_key)

        if vector_store.collection.count() == 0:
            logger.info("index.build.start repo=%s/%s", owner, repo)
            build_vector_index(owner, repo)
            logger.info("index.build.complete repo=%s/%s", owner, repo)
        else:
            logger.info("index.exists repo=%s/%s", owner, repo)

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

    except Exception:
        logger.exception("process_review.failed")
        raise


@app.post("/webhook")
async def github_webhook(request: Request):
    body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256")

    event = request.headers.get("X-GitHub-Event", "unknown")
    delivery = request.headers.get("X-GitHub-Delivery", "unknown")
    logger.info(
        "webhook.received event=%s delivery=%s body_size=%s",
        event,
        delivery,
        len(body)
    )

    if not verify_signature(body, signature):
        logger.warning("webhook.signature_invalid event=%s delivery=%s", event, delivery)
        raise HTTPException(status_code=401, detail="Invalid signature")

    
    payload = await request.json()
    action = payload.get("action")
    

    if action not in ["opened", "synchronize"]:
        logger.info("webhook.ignored event=%s delivery=%s action=%s", event, delivery, action)
        return {"message": "Ignored"}

    pr = payload["pull_request"]

    owner = payload["repository"]["owner"]["login"]
    repo = payload["repository"]["name"]
    pull_number = pr["number"]
    commit_id = pr["head"]["sha"]
      

    if is_already_processed(commit_id):    
        return {"message": "Already processed"}

    thread = threading.Thread(
        target=process_review,
        args=(owner, repo, pull_number, commit_id),
        name=f"review-{pull_number}-{commit_id[:7]}"
    )
    thread.start()
    
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