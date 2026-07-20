# ooklept/serve.py
# Serves a directory containing python files that uses ooklept Elements

#!TODO: Thread-Safety for open datas

import argparse
import runpy
import time
import uuid  # updated here
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.requests import Request
from fastapi.responses import HTMLResponse

from ooklept.base import Element
from ooklept.stores import stores

app = FastAPI()

ROOT = Path.cwd()


COOKIE_NAME = "ooklet_id"  # updated here
SESSION_STORAGE_DELETE_TIME = 60*60 # 1 hour
LAST_CLEAN_UP = 0
CLEAN_UP_INTERVAL = 10*60 # 10 min

def execute(path: str | Path, request_context: dict) -> str:
    """
    Execute an Ooklept page and return the generated HTML.
    """

    path = Path(path)

    root = Element("__root__")

    BROWSER_UUID = request_context["BROWSER_UUID"]


    get_token = stores.Get._set_context(request_context["GET"].copy())
    post_token = stores.Post._set_context(request_context["POST"].copy())
    local_token = stores.Local._set_context(BROWSER_UUID)

    try:
        with root:
            runpy.run_path(path, run_name="__main__")
    finally:
        stores.Get._reset_context(get_token)
        stores.Post._reset_context(post_token)
        stores.Local._reset_context(local_token)

    return "".join(str(child) for child in root._children)


@app.api_route("/{path:path}", methods=["GET", "POST"], response_class=HTMLResponse)
async def serve(path: str, request: Request):
    global ROOT, LAST_CLEAN_UP

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
    if time.monotonic() - LAST_CLEAN_UP > 60:
        to_remove_ks = []
        for k, v in stores.Local._data.items():
            if ls:=v.get("last_seen"):
                if time.monotonic() - ls > SESSION_STORAGE_DELETE_TIME:
                    to_remove_ks.append(k)
        for k in to_remove_ks:
            stores.Local._data.pop(k)
        LAST_CLEAN_UP = time.monotonic()

    get_params = dict(request.query_params)
    post_params = {}

    if request.method == "POST":
        form_data = await request.form()
        post_params = dict(form_data)

    # updated here
    cookies = dict(request.cookies)

    if COOKIE_NAME not in cookies:
        cookies[COOKIE_NAME] = str(uuid.uuid4())

    context = {
        "GET": get_params,
        "POST": post_params,
        "BROWSER_UUID": cookies[COOKIE_NAME],  # updated here
    }

    html = execute(file, context)  # updated here

    response = HTMLResponse(html)  # updated here

    response.set_cookie(  # updated here
        key=COOKIE_NAME,
        value=cookies[COOKIE_NAME],
        httponly=True,
        samesite="lax",
    )

    return response  # updated here

    return execute(file, context)


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
