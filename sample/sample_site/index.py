# sample/sample_site/index.py

import ooklept as o


username = _POST.get("username") # type: ignore

if username:
    o.h1("Hey")
    o.p(username)

else:
    with o.form(method="post"):
        o.input(name="username", placeholder="User Name")
        o.input(type="submit")
