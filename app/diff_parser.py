def split_diff_by_file(full_diff: str):
    files = []
    current_file = []
    current_filename = None

    for line in full_diff.splitlines():
        if line.startswith("diff --git"):
            if current_file and current_filename:
                files.append({
                    "file": current_filename,
                    "diff": "\n".join(current_file)
                })

            current_file = [line]

            parts = line.split(" ")
            if len(parts) >= 4:
                current_filename = parts[3].replace("b/", "")
            else:
                current_filename = "unknown"

        else:
            current_file.append(line)

    if current_file and current_filename:
        files.append({
            "file": current_filename,
            "diff": "\n".join(current_file)
        })

    return files