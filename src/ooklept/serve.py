# ooklept/serve.py
# Serves a directory containing python files that uses ooklept Elements

#!TODO: Thread-Safety for open datas

import argparse
import runpy
import uuid
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.requests import Request
from fastapi.responses import HTMLResponse

from ooklept.base import Element
from ooklept.stores import stores

app = FastAPI()

ROOT = Path.cwd()


COOKIE_NAME = "ooklet_id"


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

    if file.is_dir():
        file = file / "index.py"

    if not file.exists():
        raise HTTPException(404)

    # clear local stores
    stores.session_store.cleanup_stale_sessions()

    get_params = dict(request.query_params)
    post_params = {}

    if request.method == "POST":
        form_data = await request.form()
        post_params = dict(form_data)

    cookies = dict(request.cookies)

    if COOKIE_NAME not in cookies:
        cookies[COOKIE_NAME] = str(uuid.uuid4())

    context = {
        "GET": get_params,
        "POST": post_params,
        "BROWSER_UUID": cookies[COOKIE_NAME],
    }

    html = execute(file, context)

    response = HTMLResponse(html)

    response.set_cookie(
        key=COOKIE_NAME,
        value=cookies[COOKIE_NAME],
        httponly=True,
        samesite="lax",
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
