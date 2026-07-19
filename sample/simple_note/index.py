# ooklept/index.py

from ooklept import o
from ooklept.stores import stores

# memory setup

stores.Global.setdefault("notes", [])
stores.Local.setdefault("notes", [])

# update memory
if nl:=stores.Post.get("note_local"):
    stores.Local["notes"].append(nl)
if ng:=stores.Post.get("note_global"):
    stores.Global["notes"].append(ng)

with o.row(gap="2rem"):
    with o.column(gap="2rem"):
        with o.form(method="post"):
            with o.row():
                o.input(name="note_local")
                o.button("+ Add Local")
        o.h1("Local Notes")
        with o.ul():
            # for note in _LOCAL_MEMORY.get("notes"):
            #     o.li(note)
            for note in stores.Local["notes"]:
                o.li(note)

    with o.column(gap="2rem"):
        with o.form(method="post"):
            with o.row():
                o.input(name="note_global")
                o.button("+ Add Global")
        o.h1("Global Notes")
        with o.ul():
            # for note in _GLOBAL_MEMORY.get("notes"):
            #     o.li(note)
            for note in stores.Global["notes"]:
                o.li(note)
