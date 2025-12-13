import ast
from analysis.common import make_issue

def rule_docstrings(code: str):
    issues = []
    tree = ast.parse(code)

    for node in ast.walk(tree):

        # MODULE docstring
        if isinstance(node, ast.Module):
            if ast.get_docstring(node) is None:
                issues.append(
                    make_issue(
                        issue_type="missing-docstring",
                        message="Module is missing a top-level docstring.",
                        line=1,
                        severity="low",
                        suggestion="Add a docstring at the top of the file."
                    )
                )

        # FUNCTION docstring
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            name = node.name

            # skip dunder methods
            if name.startswith("__") and name.endswith("__"):
                continue

            if ast.get_docstring(node) is None:
                issues.append(
                    make_issue(
                        issue_type="missing-docstring",
                        message=f"Function '{name}' is missing a docstring.",
                        line=node.lineno,
                        severity="low",
                        suggestion="Add a docstring that describes this function."
                    )
                )

        # CLASS docstring
        if isinstance(node, ast.ClassDef):
            name = node.name
            if ast.get_docstring(node) is None:
                issues.append(
                    make_issue(
                        issue_type="missing-docstring",
                        message=f"Class '{name}' is missing a docstring.",
                        line=node.lineno,
                        severity="low",
                        suggestion="Add a docstring that describes this class."
                    )
                )

    return issues
