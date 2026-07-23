# ooklept/serve.py
# Serves a directory containing python files that uses ooklept Elements

#!TODO: Thread-Safety for open datas

import argparse
import runpy
import uuid
from pathlib import Path

import anyio
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.requests import Request
from fastapi.responses import FileResponse, HTMLResponse

from ooklept.base import Element
from ooklept.cookies import sign_session_id, verify_session_cookie
from ooklept.csrf import (
    CSRF_EXEMPT_CONTENT_TYPES,
    CSRF_EXEMPT_PATHS,
    CSRF_FIELD_NAME,
    verify_csrf_token,
)
from ooklept.stores import stores

app = FastAPI()

ROOT = Path.cwd()


COOKIE_NAME = "ooklet_id"
EXECUTABLE_EXTENSION = ".py"
STATIC_PREFIX = "static/"


def execute(path: str | Path, request_context: dict) -> str:
    """
    Execute an Ooklept page and return the generated HTML.
    """

    path = Path(path)

    root = Element("__root__")

    BROWSER_UUID = request_context["BROWSER_UUID"]

    get_token = stores.get_store.set_context(request_context["GET"].copy())
    post_token = stores.post_store.set_context(request_context["POST"].copy())
    session_token = stores.session_store.set_context(BROWSER_UUID)

    try:
        with root:
            runpy.run_path(path, run_name="__main__")
            # if the page called stores.session_store.rotate(), reflect the
            # new id back to the caller before we tear the context down
            rotated = stores.session_store.get_rotated_id()
            if rotated is not None:
                request_context["BROWSER_UUID"] = rotated
    finally:
        stores.get_store.reset_context(get_token)
        stores.post_store.reset_context(post_token)
        stores.session_store.reset_context(session_token)

    return "".join(str(child) for child in root._children)


@app.api_route("/{path:path}", methods=["GET", "POST"], response_class=HTMLResponse)
async def serve(path: str, request: Request):
    global ROOT

    if path == "":
        path = "index.py"

    file = (ROOT / path).resolve()

    # Prevent directory traversal
    try:
        file.relative_to(ROOT.resolve())
    except ValueError:
        raise HTTPException(403)

    if not file.exists():
        raise HTTPException(404)

    # --- static branch: serve raw bytes, never touches runpy ---
    if path.startswith(STATIC_PREFIX):
        if file.is_dir():
            raise HTTPException(404)  # no directory listing
        return FileResponse(file)
        # --- end static branch ---

    if file.is_dir():
        file = file / "index.py"

    if not file.exists():
        raise HTTPException(404)

    if file.suffix != ".py":
        raise HTTPException(404)

    # clear local stores
    stores.session_store.cleanup_stale_sessions()

    get_params = dict(request.query_params)
    post_params = {}

    if request.method == "POST":
        form_data = await request.form()
        post_params = dict(form_data)

    raw_cookie = request.cookies.get(COOKIE_NAME)
    session_id = verify_session_cookie(raw_cookie) if raw_cookie else None

    if session_id is None:
        session_id = str(uuid.uuid4())

    # --- CSRF check ---
    # Must run before execute(), so a forged POST never reaches page code.
    if request.method == "POST" and path not in CSRF_EXEMPT_PATHS:
        content_type = request.headers.get("content-type", "").split(";")[0].strip()

        if content_type not in CSRF_EXEMPT_CONTENT_TYPES:
            # session_id here came from verify_session_cookie above — if it was
            # None, we just minted a fresh one, which can't have a token issued
            # against it yet, so any submitted token is necessarily invalid.
            check_token = stores.session_store.set_context(session_id)
            try:
                submitted = post_params.get(CSRF_FIELD_NAME)
                token_ok = verify_csrf_token(submitted)
            finally:
                stores.session_store.reset_context(check_token)

            if not token_ok:
                raise HTTPException(403, "CSRF token missing or invalid")
    # --- end CSRF check ---

    context = {
        "GET": get_params,
        "POST": post_params,
        "BROWSER_UUID": session_id,
    }

    html = await anyio.to_thread.run_sync(execute, file, context)
    final_session_id = context["BROWSER_UUID"]
    response = HTMLResponse(html)

    response.set_cookie(
        key=COOKIE_NAME,
        value=sign_session_id(final_session_id),
        httponly=True,
        samesite="lax",
        secure=True,
    )

    return response


def main():
    global ROOT

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory to serve",
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--reload", action="store_true")

    args = parser.parse_args()

    ROOT = Path(args.directory).resolve()

    uvicorn.run(
        "ooklept.serve:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        reload_dirs=[str(ROOT)],
    )


if __name__ == "__main__":
    main()
