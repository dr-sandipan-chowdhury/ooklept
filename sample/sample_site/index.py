# index.py
from ooklept import Element as el

_GET = globals()["_GET"]
_POST = globals()["_POST"]

username = str(_POST.get("username", ""))

# Explicitly verify that a non-empty string exists before displaying the welcome screen
if username:
    el("h1").text("Welcome")
    el("p").text(username)
else:
    # Fallback to rendering the form if username is missing or empty
    with el("form").attr(method="post"):
        el("input").attr(name="username", placeholder="User Name")
        el("input").attr(type="submit")
