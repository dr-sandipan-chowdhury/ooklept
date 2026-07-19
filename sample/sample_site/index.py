# sample/sample_site/index.py

from ooklept import o

_GET = globals()["_GET"]
_POST = globals()["_POST"]

username = str(_POST.get("username", ""))

if username:
    o.h1("Hello")
    o.p(username)

else:
    with o.form(method="post"):
        o.input(name="username", placeholder="User Name")
        o.input(type="submit")
