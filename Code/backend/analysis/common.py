import ast

def make_issue(issue_type: str, message: str, line: int, severity: str = "low", suggestion: str = ""):
    return {
        "type": issue_type,
        "message": message,
        "line": line,
        "severity": severity,
        "suggestion": suggestion
    }


def parse_code_safely(code: str):
    try:
        tree = ast.parse(code)
        return tree, None

    except SyntaxError as e:
        error_issue = make_issue(
            issue_type="syntax-error",
            message=str(e),
            line=e.lineno if e.lineno else 1,
            severity="high",
            suggestion="Fix syntax error before analysis"
        )
        return None, error_issue



