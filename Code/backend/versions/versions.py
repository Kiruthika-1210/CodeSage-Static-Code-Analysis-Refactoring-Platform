"""
Phase 8 — Version History Logic (implementation)

Provides:
- init_db(db_path)             : create tables if missing
- save_version(...)            : save a new version (commit-like snapshot)
- get_version_history(session_id): list of compact summaries (timeline)
- get_version(version_id)      : full details for a single version
- generate_diff(old, new)      : unified diff + summary

Notes:
- Uses SQLite (file-based). Default DB path: backend/versions/versions.db
- Stores JSON/TEXT fields as JSON strings in the DB.
- Functions return JSON-friendly dicts/lists (ready for API responses).
"""
import sqlite3
import json
import os
import uuid
from datetime import datetime
import difflib
from typing import Optional, Dict, Any, List, Tuple

DEFAULT_DB_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "database", "versions.db")
)


# ---------------------------
# Database initialization
# ---------------------------
def get_conn(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, timeout=30, isolation_level=None)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = DEFAULT_DB_PATH) -> None:
    """
    Create tables if they do not exist. Safe to call multiple times.
    """
    conn = get_conn(db_path)
    try:
        cur = conn.cursor()
        # code_sessions table
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS code_sessions (
                id TEXT PRIMARY KEY,
                filename TEXT,
                created_at TEXT
            )
            """
        )

        # version_history table
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS version_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                parent_id INTEGER,
                original_code TEXT,
                refactored_code TEXT,
                diff TEXT,
                diff_summary TEXT,
                issues TEXT,
                complexity TEXT,
                quality_score INTEGER,
                created_at TEXT,
                FOREIGN KEY(session_id) REFERENCES code_sessions(id),
                FOREIGN KEY(parent_id) REFERENCES version_history(id)
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


# Ensure DB is initialized when module is imported
init_db()


# ---------------------------
# Utility helpers
# ---------------------------
def iso_now() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _json_dumps_safe(obj: Any) -> str:
    try:
        return json.dumps(obj, ensure_ascii=False)
    except Exception:
        # fallback: convert to string
        return json.dumps(str(obj))


def _json_loads_safe(s: Optional[str]) -> Any:
    if s is None:
        return None
    try:
        return json.loads(s)
    except Exception:
        return s


def generate_diff(old_code: str, new_code: str) -> Tuple[str, str]:
    """
    Generate unified diff text and a short summary string.
    Returns (diff_text, diff_summary).

    Rules:
    - If codes are identical => return ("", "")
    - Uses difflib.unified_diff internally.
    """
    if old_code is None:
        old_code = ""
    if new_code is None:
        new_code = ""

    if old_code == new_code:
        return "", ""

    # Ensure lines end with newline for unified_diff
    old_lines = old_code.splitlines(keepends=True)
    new_lines = new_code.splitlines(keepends=True)

    diff_lines = list(
        difflib.unified_diff(old_lines, new_lines, fromfile="original.py", tofile="refactored.py", lineterm="")
    )
    diff_text = "\n".join(diff_lines)

    # Simple summary: count additions and deletions (lines starting with + / - excluding headers)
    additions = 0
    deletions = 0
    for ln in diff_lines:
        if ln.startswith("+++ ") or ln.startswith("--- ") or ln.startswith("@@"):
            continue
        if ln.startswith("+"):
            additions += 1
        elif ln.startswith("-"):
            deletions += 1

    parts = []
    if additions:
        parts.append(f"{additions} additions")
    if deletions:
        parts.append(f"{deletions} deletions")
    diff_summary = ", ".join(parts) if parts else "modified"

    return diff_text, diff_summary


# ---------------------------
# Core functions
# ---------------------------
def save_version(
    session_id: str,
    original_code: str,
    refactored_code: str,
    issues: Any,
    complexity: Any,
    quality_score: Optional[int],
    diff: Optional[str] = None,
    db_path: str = DEFAULT_DB_PATH,
) -> Dict[str, Any]:
    """
    Save a new version snapshot into version_history.

    Inputs:
      - session_id (str)            : session to attach this version to
      - original_code (str)
      - refactored_code (str)
      - issues (any JSON-serializable)
      - complexity (any JSON-serializable)
      - quality_score (int)
      - diff (optional)             : if provided, will be stored; otherwise generated
    Returns:
      - { "ok": True, "version_id": int, "created_at": ISO, "parent_id": int_or_none }
      - or { "ok": False, "error": "..."}
    Fault-tolerance rules:
      - If refactored_code == original_code -> diff stored as empty string
      - If DB write fails -> return error dict (no corrupt data inserted)
    """
    conn = get_conn(db_path)
    try:
        cur = conn.cursor()

        # Ensure session exists; if not, create a minimal session row
        cur.execute("SELECT id FROM code_sessions WHERE id = ?", (session_id,))
        row = cur.fetchone()
        if row is None:
            created_at = iso_now()
            cur.execute("INSERT INTO code_sessions (id, filename, created_at) VALUES (?, ?, ?)", (session_id, None, created_at))

        # Determine parent_id (latest version for that session)
        cur.execute(
            "SELECT id FROM version_history WHERE session_id = ? ORDER BY created_at DESC LIMIT 1",
            (session_id,),
        )
        parent_row = cur.fetchone()
        parent_id = parent_row["id"] if parent_row is not None else None

        # Diff handling
        if original_code == refactored_code:
            final_diff_text = ""
            diff_summary = ""
        else:
            if diff is not None:
                final_diff_text = diff
                # Try to produce a lightweight summary if none passed
                _, diff_summary = generate_diff(original_code, refactored_code) if not diff else ("", "")
                if not diff_summary:
                    # compute from provided diff text
                    additions = sum(1 for ln in diff.splitlines() if ln.startswith("+") and not ln.startswith("+++"))
                    deletions = sum(1 for ln in diff.splitlines() if ln.startswith("-") and not ln.startswith("---"))
                    parts = []
                    if additions:
                        parts.append(f"{additions} additions")
                    if deletions:
                        parts.append(f"{deletions} deletions")
                    diff_summary = ", ".join(parts) if parts else ""
            else:
                final_diff_text, diff_summary = generate_diff(original_code, refactored_code)

        created_at = iso_now()

        # Insert row inside transaction
        try:
            cur.execute(
                """
                INSERT INTO version_history
                (session_id, parent_id, original_code, refactored_code, diff, diff_summary, issues, complexity, quality_score, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    parent_id,
                    original_code,
                    refactored_code,
                    final_diff_text,
                    diff_summary,
                    _json_dumps_safe(issues),
                    _json_dumps_safe(complexity),
                    quality_score,
                    created_at,
                ),
            )
            # Fetch the auto-generated id
            version_id = cur.lastrowid
            # Commit (connection in autocommit mode; explicit commit for clarity)
            conn.commit()

            return {"ok": True, "version_id": version_id, "parent_id": parent_id, "created_at": created_at}
        except Exception as e:
            # Rollback and return safe error; do not leave corrupt partial data
            try:
                conn.rollback()
            except Exception:
                pass
            return {"ok": False, "error": f"DB insert failed: {str(e)}"}
    except Exception as outer_e:
        return {"ok": False, "error": f"save_version failed: {str(outer_e)}"}
    finally:
        conn.close()


def get_version_history(session_id: str, db_path: str = DEFAULT_DB_PATH) -> Dict[str, Any]:
    """
    Retrieve a chronological list of compact version summaries for the given session_id.

    Returns:
      { "ok": True, "history": [ {version summary}, ... ] }
      or { "ok": False, "error": "..." }

    Each version summary contains:
      - version_id
      - parent_id
      - created_at
      - summary (string)       -> prefer diff_summary; fallback to simple text
      - diff_summary
    """
    conn = get_conn(db_path)
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, parent_id, created_at, diff_summary
            FROM version_history
            WHERE session_id = ?
            ORDER BY datetime(created_at) ASC
            """,
            (session_id,),
        )
        rows = cur.fetchall()
        history = []
        for r in rows:
            version_id = r["id"]
            parent_id = r["parent_id"]
            created_at = r["created_at"]
            diff_summary = r["diff_summary"] or ""
            # Derive a human-friendly summary:
            if diff_summary:
                summary = diff_summary
            else:
                # fallback summary if none present
                summary = "Snapshot"
            history.append(
                {
                    "version_id": version_id,
                    "parent_id": parent_id,
                    "created_at": created_at,
                    "summary": summary,
                    "diff_summary": diff_summary,
                }
            )

        return {"ok": True, "history": history}
    except Exception as e:
        return {"ok": False, "error": f"get_version_history failed: {str(e)}"}
    finally:
        conn.close()


def get_version(version_id: int, db_path: str = DEFAULT_DB_PATH) -> Dict[str, Any]:
    """
    Retrieve full details for a single version_id.

    Returns:
      { "ok": True, "version": { ...fields... } } or { "ok": False, "error": ... }

    Version object contains:
      - id
      - session_id
      - parent_id
      - original_code
      - refactored_code
      - diff
      - diff_summary
      - issues (parsed JSON)
      - complexity (parsed JSON)
      - quality_score
      - created_at
    """
    conn = get_conn(db_path)
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT *
            FROM version_history
            WHERE id = ?
            """,
            (version_id,),
        )
        row = cur.fetchone()
        if row is None:
            return {"ok": False, "error": "version not found"}

        version = {
            "id": row["id"],
            "session_id": row["session_id"],
            "parent_id": row["parent_id"],
            "original_code": row["original_code"],
            "refactored_code": row["refactored_code"],
            "diff": row["diff"] or "",
            "diff_summary": row["diff_summary"] or "",
            "issues": _json_loads_safe(row["issues"]),
            "complexity": _json_loads_safe(row["complexity"]),
            "quality_score": row["quality_score"],
            "created_at": row["created_at"],
        }
        return {"ok": True, "version": version}
    except Exception as e:
        return {"ok": False, "error": f"get_version failed: {str(e)}"}
    finally:
        conn.close()


# ---------------------------
# Small demo / test helpers (optional)
# ---------------------------
if __name__ == "__main__":
    # Quick demo for manual testing — runs only when executed directly.
    db = DEFAULT_DB_PATH
    print("DB path:", db)
    init_db(db)

    # create a session id
    session = str(uuid.uuid4())
    print("Demo session id:", session)

    original = "def add(a, b):\n    return a + b\n"
    refactored = "def add_numbers(a: int, b: int) -> int:\n    return a + b\n"

    print("Saving first version...")
    res1 = save_version(session, original, original, issues={"issues": []}, complexity={"big_o": "O(1)"}, quality_score=80)
    print(res1)

    print("Saving refactored version...")
    res2 = save_version(session, original, refactored, issues=[{"line": 1, "msg": "add type hints"}], complexity={"big_o": "O(1)"}, quality_score=88)
    print(res2)

    print("History:")
    hist = get_version_history(session)
    print(json.dumps(hist, indent=2))

    if res2.get("ok"):
        vid = res2["version_id"]
        full = get_version(vid)
        print("Full version details:")
        print(json.dumps(full, indent=2))
