def analyze_maintainability(code: str):
    slices = []
    penalty = 0

    # SPLIT CODE INTO LINES
    current_line = ""
    for ch in code:
        if ch == "\n":
            slices.append(current_line)
            current_line = ""
        else:
            current_line += ch
    if current_line:
        slices.append(current_line)

    # 1. FUNCTION LENGTH CALCULATION
    functions = []
    n = len(slices)
    i = 0

    while i < n:
        if slices[i].lstrip().startswith("def "):
            start = i
            def_indent = len(slices[i]) - len(slices[i].lstrip())

            i += 1
            # find the end of this function
            while i < n:
                current_indent = len(slices[i]) - len(slices[i].lstrip())

                # if indentation returns → function ends
                if current_indent <= def_indent and slices[i].strip() != "":
                    break
                i += 1

            end = i - 1
            length = end - start + 1

            functions.append((start, end, length))
        else:
            i += 1

    # Apply function length penalty
    for fn in functions:
        if fn[2] > 30:
            penalty += 10   # correct value per spec

    # 2. REPEATED LOGIC DETECTION
    seen_blocks = set()

    for i in range(len(slices) - 2):
        block = (
            slices[i].strip(),
            slices[i+1].strip(),
            slices[i+2].strip()
        )

        if all(line == "" for line in block):
            continue

        if block in seen_blocks:
            penalty += 10
            break
        else:
            seen_blocks.add(block)

    # 3. DEEP NESTING DETECTION
    max_depth = 0

    for line in slices:
        stripped = line.strip()
        if stripped == "":
            continue

        space_count = len(line) - len(line.lstrip())
        depth = space_count // 4

        if depth > max_depth:
            max_depth = depth

    if max_depth >= 6:
        penalty += 10
    elif max_depth >= 4:
        penalty += 5

    # 4. BRANCH COUNTING
    branch_count = 0
    branches = ["if ", "elif ", "else:", "match ", "case "]

    for line in slices:
        stripped = line.strip()
        for b in branches:
            if stripped.startswith(b):
                branch_count += 1
                break

    if branch_count >= 4:
        penalty += 10
    elif branch_count >= 3:
        penalty += 5

    score = max(0, 25 - penalty)

    return {"maintainability_score": score}
