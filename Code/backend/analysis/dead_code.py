import ast
from analysis.common import make_issue

TERMINATORS = (ast.Return, ast.Raise, ast.Break, ast.Continue)


def rule_dead_code(code: str):
    issues = []
    tree = ast.parse(code)

    # Helper to scan any list of statements
    def scan_block(statements):
        found_terminator = False
        terminator_line = None

        for stmt in statements:
            # If we already saw a terminator → everything now is unreachable
            if found_terminator:
                issues.append(
                    make_issue(
                        issue_type="unreachable-code",
                        message=f"This line is unreachable due to a previous terminator on line {terminator_line}.",
                        line=stmt.lineno,
                        severity="medium",
                        suggestion="Remove or restructure unreachable code."
                    )
                )
                continue

            # Detect the first terminator
            if isinstance(stmt, TERMINATORS):
                found_terminator = True
                terminator_line = stmt.lineno

    # Walk every node and scan every block of statements
    for node in ast.walk(tree):

        # 1. node.body
        if hasattr(node, "body") and isinstance(node.body, list):
            scan_block(node.body)

        # 2. node.orelse
        if hasattr(node, "orelse") and isinstance(node.orelse, list):
            scan_block(node.orelse)

        # 3. node.finalbody
        if hasattr(node, "finalbody") and isinstance(node.finalbody, list):
            scan_block(node.finalbody)

        # 4. node.handlers (except blocks)
        if hasattr(node, "handlers"):
            for handler in node.handlers:
                scan_block(handler.body)

    return issues
