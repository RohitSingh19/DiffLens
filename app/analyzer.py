import json
from app.diff_parser import split_diff_by_file
from app.github import fetch_file_content
from app.llm import analyze_code
from app.validator import validate_comments
from app.retriever import retrieve_related_context
from app.severity import normalize_severity, severity_priority
from app.vector_store import VectorStore


def build_prompt(filename, file_content, related_context, semantic_context, diff):
    related_text = "\n\n".join([
        f"RELATED FILE: {item['file']}\n{item['content'][:1000]}"
        for item in related_context
    ])

    semantic_text = "\n\n".join(semantic_context)

    return f"""
You are a strict senior code reviewer.

Review ONLY the changed code.

You MUST use the provided context:
- Current file
- Related imports
- Similar code patterns

IMPORTANT RULES:

1. If similar code shows an existing pattern (e.g. validation, error handling):
   - DO NOT suggest duplicating it
   - Instead mention inconsistency

2. If no such pattern exists:
   - Suggest improvement

3. Avoid generic advice like:
   - "add validation"
   - "add error handling"
   UNLESS it is clearly missing AND not implemented elsewhere

4. If you claim inconsistency or pattern violation:
   - You MUST reference where that pattern exists in the provided context
   - If no clear evidence is found, DO NOT report the issue

   Do NOT guess patterns.

   
Focus ONLY on:
- real bugs
- security issues
- performance problems
- maintainability risks

Ignore:
- style issues
- optional improvements
- generic best practices

Return maximum 2 issues only.
Return STRICT valid JSON only.

FILE:
{filename}

CURRENT FILE:
{file_content[:2000]}

RELATED CONTEXT:
{related_text}

SIMILAR CODE:
{semantic_text}

DIFF:
{diff[:1500]}

FORMAT:
[
  {{
    "file": "{filename}",
    "line": number,
    "severity": "LOW|MEDIUM|HIGH",
    "issue": "string",
    "suggestion": "string",
    "confidence": 0.0
  }}
]
"""



def analyze_diff(full_diff: str, owner: str, repo: str):
    files = split_diff_by_file(full_diff)
    all_comments = []

    for file_data in files:
        filename = file_data["file"]
        diff = file_data["diff"]


        file_content = fetch_file_content(owner, repo, filename)


        related_context = retrieve_related_context(
            owner=owner,
            repo=repo,
            file_content=file_content,
            current_file=filename
        )

        # Step 3: Semantic retrieval (IMPROVED QUERY)
        query = f"{filename}\n{diff[:400]}"

        repo_key = f"{owner}_{repo}"
        vector_store = VectorStore(repo_key)

        raw_semantic = vector_store.search_similar_text(
            query=query,
            top_k=5
        )

        semantic_context = trim_and_dedup_context(raw_semantic)

        
        print("\n--- SEMANTIC CONTEXT ---")
        for chunk in semantic_context:
            print(chunk[:200])
        print("------------------------\n")

        
        prompt = build_prompt(
            filename=filename,
            file_content=file_content,
            related_context=related_context,
            semantic_context=semantic_context,
            diff=diff
        )

        
        raw_output = analyze_code(prompt)

        
        parsed = safe_json_parse(raw_output)

        
        validated = validate_comments(parsed)
        filtered = filter_comments(validated)

        
        normalized = [
            normalize_severity(comment)
            for comment in filtered
        ]

        for comment in normalized:
            comment["file"] = filename

        all_comments.extend(normalized)

    
    all_comments.sort(
        key=lambda x: severity_priority(x.get("severity", "LOW")),
        reverse=True
    )

    return all_comments


def filter_comments(comments):
    return [
        comment
        for comment in comments
        if comment.get("confidence", 0) >= 0.75
    ]


def safe_json_parse(raw_output: str):
    try:
        cleaned = clean_llm_output(raw_output)
        return json.loads(cleaned)
    except Exception as e:
        print("JSON parsing failed")
        print(str(e))
        print("Raw output:")
        print(raw_output)
        return []


def clean_llm_output(output: str) -> str:
    output = output.strip()

    if output.startswith("```"):
        output = output.split("```")[1]
        if output.startswith("json"):
            output = output[4:]

    if output.endswith("```"):
        output = output[:-3]

    return output.strip()



def trim_and_dedup_context(chunks):
    seen = set()
    cleaned = []

    for chunk in chunks:
        snippet = chunk.strip()

        if not snippet:
            continue

        # Dedup
        if snippet in seen:
            continue

        seen.add(snippet)

        # Trim size
        cleaned.append(snippet[:800])

    return cleaned[:3]