import ast
from analysis.common import make_issue


def rule_duplicate_logic(code: str):
    tree = ast.parse(code)
    issues = []

    # Store: hash → first occurrence line
    seen = {}

    # Already reported duplicate hashes
    reported = set()

    DUPLICATE_NODE_TYPES = (
        ast.Assign,
        ast.Expr,
        ast.Return,
        ast.If,
        ast.For,
        ast.While,
        ast.With,
        ast.Try,
    )

    def normalize(node):
        if isinstance(node, ast.AST):
            fields = []
            for field_name in node._fields:
                value = getattr(node, field_name)
                if field_name in ("lineno", "col_offset", "end_lineno", "end_col_offset"):
                    continue
                fields.append((field_name, normalize(value)))
            return (node.__class__.__name__, tuple(fields))

        elif isinstance(node, list):
            return tuple(normalize(x) for x in node)

        else:
            return node

    for node in ast.walk(tree):

        if not isinstance(node, DUPLICATE_NODE_TYPES):
            continue

        norm = normalize(node)
        node_hash = hash(norm)

        if node_hash in seen:

            # Avoid spamming duplicates
            if node_hash not in reported:
                first_line = seen[node_hash]
                issues.append(
                    make_issue(
                        issue_type="duplicate-logic",
                        message=f"Duplicate logic found. First seen at line {first_line}.",
                        line=node.lineno,
                        severity="medium",
                        suggestion="Refactor repeated logic into a function or remove redundancy."
                    )
                )
                reported.add(node_hash)

        else:
            seen[node_hash] = node.lineno

    return issues
