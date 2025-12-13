import ast
from analysis.common import make_issue

def rule_nesting(code: str):
    MAX_DEPTH = 4   # configure as needed
    tree = ast.parse(code)
    issues = []

    # These AST node types increase nesting level
    nesting_nodes = (
        ast.If,
        ast.For,
        ast.While,
        ast.With,
        ast.Try,
        ast.AsyncFor,
        ast.AsyncWith,
        ast.ExceptHandler,
    )

    def visit(node, depth):
        # If this node increases nesting:
        if isinstance(node, nesting_nodes):
            depth += 1
            if depth > MAX_DEPTH:
                issues.append(
                    make_issue(
                        issue_type="deep-nesting",
                        message=f"Code is nested too deeply (depth = {depth}).",
                        line=node.lineno,
                        severity="low" if depth <= 6 else "high",
                        suggestion="Reduce nesting by refactoring or extracting functions."
                    )
                )
                
        for child in ast.iter_child_nodes(node):
            visit(child, depth)

    # Start recursion at module level with depth = 0
    visit(tree, depth=0)

    return issues
