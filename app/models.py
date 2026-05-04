from pydantic import BaseModel
from typing import List


class ReviewPRRequest(BaseModel):
    owner: str
    repo: str
    pull_number: int

class ReviewComment(BaseModel):
    file: str
    line: str
    severity: str #LOW | MEDIUM | HIGH
    issue: str
    suggestions: str
    confidence: float

class ReviewResponse(BaseModel):
    comments: List[ReviewComment]
    