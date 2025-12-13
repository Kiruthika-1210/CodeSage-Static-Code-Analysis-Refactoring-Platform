import ast
from analysis.common import make_issue


def rule_bad_naming(code: str):
    issues = []
    tree = ast.parse(code)

    # Helper: check if node is inside module (for constants)
    def is_module_level(node):
        return isinstance(node, ast.Module)

    # Find parent map to detect module-level targets
    parent = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parent[child] = node

    # ---- FUNCTION NAME CHECK (snake_case) ----
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            name = node.name
            valid = True

            # ignore magic methods: __init__, __str__, etc.
            if name.startswith("__") and name.endswith("__"):
                continue

            # 1. Must start lowercase letter
            if not (name[0].islower() and name[0].isalpha()):
                valid = False

            # 2. All characters must be lowercase/digit/underscore
            for char in name:
                if not (char.islower() or char.isdigit() or char == "_"):
                    valid = False

            # 3. No uppercase anywhere
            if any(c.isupper() for c in name):
                valid = False

            if not valid:
                issues.append(
                    make_issue(
                        issue_type="naming-convention",
                        message=f"Function name '{name}' is not snake_case.",
                        line=node.lineno,
                        severity="low",
                        suggestion=f"Rename the function '{name}' to snake_case."
                    )
                )

    # ---- CLASS NAME CHECK (PascalCase) ----
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            name = node.name
            valid = True

            # 1. Must start with uppercase
            if not (name[0].isupper() and name[0].isalpha()):
                valid = False

            # 2. Remaining characters must be alphanumeric (no underscores)
            for char in name:
                if not char.isalnum():
                    valid = False

            # 3. Cannot be ALL CAPS (those are constants)
            if name.isupper():
                valid = False

            if not valid:
                issues.append(
                    make_issue(
                        issue_type="naming-convention",
                        message=f"Class name '{name}' is not PascalCase.",
                        line=node.lineno,
                        severity="low",
                        suggestion=f"Rename the class '{name}' to PascalCase."
                    )
                )

    # ---- VARIABLE NAME CHECK (snake_case) ----
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            name = node.id
            valid = True

            # Skip constants (ALL CAPS)
            if name.isupper():
                continue  # Constant rule handles it

            # 1. Must start lowercase or underscore
            if not (name[0].islower() or name[0] == "_"):
                valid = False

            # 2. All characters must be lowercase/digit/underscore
            for char in name:
                if not (char.islower() or char.isdigit() or char == "_"):
                    valid = False

            # 3. No uppercase anywhere
            if any(c.isupper() for c in name):
                valid = False

            if not valid:
                issues.append(
                    make_issue(
                        issue_type="naming-convention",
                        message=f"Variable name '{name}' is not snake_case.",
                        line=node.lineno,
                        severity="low",
                        suggestion=f"Rename the variable '{name}' to snake_case."
                    )
                )

    # ---- CONSTANT NAME CHECK (UPPER_CASE) ----
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            # Only constants at module-level
            if not is_module_level(parent.get(node, None)):
                continue

            for target in node.targets:
                if isinstance(target, ast.Name):
                    name = target.id
                    valid = True

                    # Must be ALL CAPS to qualify as constant
                    if name.isupper():
                        # 1. Must contain only A-Z, digits, underscore
                        for char in name:
                            if not (char.isupper() or char.isdigit() or char == "_"):
                                valid = False

                        # 2. Cannot start with a digit
                        if name[0].isdigit():
                            valid = False

                        if not valid:
                            issues.append(
                                make_issue(
                                    issue_type="naming-convention",
                                    message=f"Constant '{name}' should be UPPER_CASE.",
                                    line=target.lineno,
                                    severity="low",
                                    suggestion=f"Rename '{name}' to UPPER_CASE format."
                                )
                            )

    return issues
