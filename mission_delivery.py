
"""Consegna prudente dei programmi generati da AI Company."""

from __future__ import annotations

import ast
from datetime import datetime
from pathlib import Path
import re
import uuid


BLOCK = re.compile(
    r"```[ \t]*(?:python|py)[ \t]*\r?\n(.*?)```",
    re.IGNORECASE | re.DOTALL,
)

GENERIC_BLOCK = re.compile(
    r"```[ \t]*\r?\n(.*?)```",
    re.DOTALL,
)


def extract_python(response: str) -> list[str]:
    """Estrae codice Python senza confondere testo e codice."""

    response = (response or "").strip()

    # 1. Blocchi esplicitamente Python
    blocks = BLOCK.findall(response)

    if blocks:
        return [code.strip() for code in blocks if code.strip()]

    # 2. Blocchi senza linguaggio dichiarato
    blocks = GENERIC_BLOCK.findall(response)

    valid = []

    for code in blocks:
        code = code.strip()
        try:
            ast.parse(code)
            valid.append(code)
        except SyntaxError:
            continue

    if valid:
        return valid

    # 3. Risposta composta interamente da codice Python
    try:
        tree = ast.parse(response)

        if tree.body and not all(
            isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
            for node in tree.body
        ):
            return [response]

    except SyntaxError:
        pass

    return []


def deliver(response: str, root: Path) -> dict:
    blocks = extract_python(response)

    if not blocks:
        return {
            "status": "no_files",
            "message": (
                "Nessun codice Python riconoscibile. "
                "Controllare il formato della risposta dell'agente."
            ),
            "files": [],
        }

    base = root / "projects" / "company_missions"

    folder = base / (
        datetime.now().strftime("%Y%m%d_%H%M%S_")
        + uuid.uuid4().hex[:6]
    )

    folder.mkdir(parents=True, exist_ok=False)

    files = []

    for i, code in enumerate(blocks, 1):
        name = (
            "main.py"
            if len(blocks) == 1
            else f"modulo_{i:02d}.py"
        )

        path = folder / name

        path.write_text(
            code.rstrip() + "\n",
            encoding="utf-8",
        )

        try:
            ast.parse(code, filename=name)
            status = "syntax_ok"
            error = ""

        except SyntaxError as exc:
            status = "syntax_error"
            error = f"{exc.msg} (riga {exc.lineno})"

        files.append({
            "name": name,
            "path": str(path),
            "status": status,
            "error": error,
        })

    return {
        "status": "created",
        "folder": str(folder),
        "files": files,
        "message": (
            f"Creati {len(files)} file. "
            "Nessun programma avviato."
        ),
    }
