def chunk_code(file_path: str, content: str, chunk_size: int = 40):
    """
    Split code into line-based chunks.

    Example:
    Every 40 lines becomes one chunk.

    Returns:
    [
        {
            "id": "...",
            "file": "...",
            "content": "...",
            "start_line": 1,
            "end_line": 40
        }
    ]
    """

    lines = content.splitlines()
    chunks = []

    for i in range(0, len(lines), chunk_size):
        chunk_lines = lines[i:i + chunk_size]

        chunk = {
            "id": f"{file_path}_{i}",
            "file": file_path,
            "content": "\n".join(chunk_lines),
            "start_line": i + 1,
            "end_line": i + len(chunk_lines)
        }

        chunks.append(chunk)

    return chunks