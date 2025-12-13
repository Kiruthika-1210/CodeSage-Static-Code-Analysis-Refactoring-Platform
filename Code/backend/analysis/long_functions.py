import ast
from analysis.common import make_issue

def rule_long_function(code: str):
    issues = []
    tree = ast.parse(code)

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            
            # Try using end_lineno
            if hasattr(node, "end_lineno") and node.end_lineno:
                function_length = node.end_lineno - node.lineno
            else:
                # Fallback: last child line - start line
                if node.body:
                    function_length = node.body[-1].lineno - node.lineno
                else:
                    function_length = 0

            if function_length > 50:
                issues.append(
                    make_issue(
                        issue_type="long-function",
                        message=f"Function '{node.name}' is too long ({function_length} lines).",
                        line=node.lineno,
                        severity="medium",
                        suggestion="Break the function into smaller units."
                    )
                )
    
    return issues
