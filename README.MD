# DiffLens

DiffLens is a context-aware, AI-powered pull request reviewer that analyzes code changes with retrieval-augmented generation (RAG) and posts automated review comments directly on GitHub pull requests.

The service ingests a PR diff, fetches repository context from GitHub, retrieves semantically similar code from a local ChromaDB vector store, and asks an LLM to review only the changed code. The final output is a small set of prioritized review comments focused on bugs, security issues, performance problems, and maintainability risks.

## What The Project Does

- Accepts unified diff input through an upload endpoint.
- Fetches pull request diffs and metadata from GitHub.
- Builds or reuses a repository-specific vector index for semantic code retrieval.
- Combines current file content, related files, and similar code snippets to provide grounded review context.
- Uses an LLM to generate structured review comments with severity and confidence.
- Filters, validates, deduplicates, and posts review comments back to GitHub PRs.
- Supports GitHub webhook-based automation for newly opened or updated pull requests.

## How It Works

1. A pull request is submitted directly through the API or received through the GitHub webhook.
2. DiffLens fetches the PR diff and file contents from GitHub.
3. The analyzer retrieves nearby and semantically related code context using the local vector store.
4. The LLM reviews the changed code in context and returns strict JSON findings.
5. Findings are validated, normalized, filtered by confidence, and ranked by severity.
6. DiffLens creates a GitHub review with inline comments on the pull request.

## Tech Stack

- FastAPI for the HTTP API and webhook handler
- OpenAI API for code review generation
- ChromaDB for vector storage and semantic retrieval
- Requests for GitHub API integration
- Pydantic for request and response models

## API Endpoints

- `GET /health` - health check endpoint
- `POST /analyze` - upload a diff file and return generated review comments
- `POST /review-pr` - analyze a GitHub pull request and post a review
- `POST /webhook` - receive GitHub webhook events for automated PR review

## Environment Variables

Create a `.env` file in the project root with the following values:

```env
OPENAI_API_KEY=your_openai_api_key
GITHUB_TOKEN=your_github_token
GITHUB_WEBHOOK_SECRET=your_github_webhook_secret
```

## Local Setup

# Clone Repository 

git clone https://github.com/your-username/DiffLens.git
cd DiffLens

# Create Virtual Environment
python -m venv .venv

# Install Dependencies
pip install -r requirements.txt

# Configure Environment Variables
OPENAI_API_KEY=your_openai_api_key
GITHUB_TOKEN=your_github_token
GITHUB_WEBHOOK_SECRET=your_secret

# Run FastAPI Server
uvicorn app.main:app --reload
```

## Running The Service

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.


# Deployment

DiffLens is deployed using:

Render
GitHub Webhooks
OpenAI APIs

The deployed system processes GitHub Pull Request events asynchronously and posts automated AI review comments directly into PR discussions.

## Indexing Notes

DiffLens uses a repository-specific ChromaDB collection to retrieve semantically similar code during review. The index is built automatically when a repository is processed for the first time and its collection is still empty.

There is also a helper script in `scripts/build_index.py` for manual indexing, but it currently expects the repository owner and name to be filled in before execution.

## Folder Structure

```text
DiffLens/
│
├── app/
│   ├── analyzer.py
│   ├── chunker.py
│   ├── diff_parser.py
│   ├── embedder.py
│   ├── github.py
│   ├── indexer.py
│   ├── llm.py
│   ├── main.py
│   ├── retriever.py
│   ├── severity.py
│   ├── validator.py
│   └── vector_store.py
│
├── chroma_db/
├── scripts/
├── requirements.txt
└── README.md
```

## Core Modules

- `app/main.py` - FastAPI entrypoint and webhook orchestration
- `app/analyzer.py` - diff analysis pipeline and prompt construction
- `app/github.py` - GitHub API helpers for diffs, files, and PR details
- `app/github_review.py` - GitHub review and inline comment publishing
- `app/indexer.py` - repository indexing and vector population
- `app/retriever.py` - context retrieval for related code
- `app/vector_store.py` - ChromaDB integration for semantic search
- `app/validator.py` - output validation for generated comments

## Typical Use Cases

- Automating first-pass reviews on GitHub pull requests
- Catching regressions with repository-aware context instead of diff-only analysis
- Highlighting risky changes in security-sensitive or complex codebases
- Providing consistent review feedback for teams handling large PR volumes

## Current Behavior Summary

The system is designed to keep feedback focused and conservative:

- Reviews only changed code, not the entire repository
- Prioritizes high-confidence findings
- Limits the number of generated issues per file
- Posts a compact set of high and medium severity comments to GitHub

# Current Limitations

- Full repository indexing on cold start
- ChromaDB persistence limitations on Render free tier
- No incremental indexing yet
- Designed primarily for learning and experimentation rather than production-scale multi-tenant usage


# Future Improvements
- Incremental indexing for changed files only
- Persistent vector storage
- GitHub App authentication
- Smarter duplicate suppression
- Multi-repository indexing support
- Background indexing workers