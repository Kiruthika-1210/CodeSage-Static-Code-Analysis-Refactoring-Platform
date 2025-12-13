import ast
from analysis.common import make_issue


def rule_unused_names(code: str):
    tree = ast.parse(code)

    assigned_imports = []     
    issues = []

    # SCOPE STACK:
    # First scope = module level
    scope_stack = [{"assigned": {}, "used": set()}]

    def enter_scope():
        scope_stack.append({"assigned": {}, "used": set()})

    def exit_scope():
        return scope_stack.pop()

    def add_assigned_var(name, line):
        scope_stack[-1]["assigned"][name] = line

    def mark_used(name):
        # Walk upward: assign usage to nearest matching scope
        for scope in reversed(scope_stack):
            if name in scope["assigned"]:
                scope["used"].add(name)
                return
        return
    
    # WALK AST
    for node in ast.walk(tree):

        # Enter scopes
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            enter_scope()

        # Detect imports
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                assigned_imports.append({
                    "name": alias.asname or alias.name,
                    "line": node.lineno
                })

        # Detect assigned variables (var = ...)
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    add_assigned_var(target.id, target.lineno)

        # Annotated variable: x: int = 5
        if isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name):
                add_assigned_var(node.target.id, node.target.lineno)

        # For-loop variables
        if isinstance(node, ast.For):
            if isinstance(node.target, ast.Name):
                add_assigned_var(node.target.id, node.target.lineno)

        # With-block variables
        if isinstance(node, ast.With):
            for item in node.items:
                if isinstance(item.optional_vars, ast.Name):
                    add_assigned_var(item.optional_vars.id, item.optional_vars.lineno)

        # Exception handler: except Exception as e
        if isinstance(node, ast.ExceptHandler):
            if isinstance(node.name, str):
                add_assigned_var(node.name, node.lineno)

        # Detect used names
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            mark_used(node.id)

        # Exit scope: resolve unused vars inside functions/classes
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            finished_scope = exit_scope()

            for name, line in finished_scope["assigned"].items():

                # ignore intentionally unused variables
                if name.startswith("_"):
                    continue

                if name not in finished_scope["used"]:
                    issues.append(
                        make_issue(
                            issue_type="unused-variable",
                            message=f"Variable '{name}' is assigned but never used.",
                            line=line,
                            severity="low",
                            suggestion=f"Remove variable '{name}' or use it."
                        )
                    )

    # ⭐ HANDLE MODULE-LEVEL UNUSED VARIABLES
    module_scope = scope_stack[0]

    for name, line in module_scope["assigned"].items():

        # ignore intentionally unused variables
        if name.startswith("_"):
            continue

        if name not in module_scope["used"]:
            issues.append(
                make_issue(
                    issue_type="unused-variable",
                    message=f"Variable '{name}' is assigned but never used.",
                    line=line,
                    severity="low",
                    suggestion=f"Remove variable '{name}' or use it."
                )
            )

    # ⭐ UNUSED IMPORTS CHECK
    # Collect all used names across all scopes
    all_used = set().union(*(scope["used"] for scope in scope_stack))

    for imp in assigned_imports:
        if imp["name"] not in all_used:
            issues.append(
                make_issue(
                    issue_type="unused-import",
                    message=f"Import '{imp['name']}' is never used.",
                    line=imp["line"],
                    severity="low",
                    suggestion=f"Remove the unused import '{imp['name']}'."
                )
            )

    return issues
