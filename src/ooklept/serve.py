# ooklept/serve.py
# Serves a directory containing python files that uses ooklept Elements

import argparse
import runpy
from pathlib import Path

from fastapi.requests import Request
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from ooklept.base import Element


app = FastAPI()

ROOT = Path.cwd()


def execute(path: str | Path, request_context:dict) -> str:
    """
    Execute an Ooklept page and return the generated HTML.
    """

    path = Path(path)

    root = Element("__root__")

    # Inject variables directly into the script's global execution state
    init_vars = {
        "_GET": request_context.get("GET", {}).copy(),
        "_POST": request_context.get("POST", {}).copy(),
    }

    with root:
        runpy.run_path(path,init_globals=init_vars, run_name="__main__")

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

    get_params = dict(request.query_params)
    post_params = {}

    if request.method == "POST":
        form_data = await request.form()
        post_params = dict(form_data)

    context = {
        "GET": get_params,
        "POST": post_params
    }

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

    args = parser.parse_args()

    ROOT = Path(args.directory).resolve()

    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
