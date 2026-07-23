# ooklept/index.py

from ooklept import o
from ooklept.nojsonlycss import use_pico_css
from ooklept.stores import stores, post_track

use_pico_css()

session_note = post_track("note_local", None, None)
global_note = post_track("note_global", None, None)


# memory setup
stores.session_store.setdefault("notes", [])
stores.global_store.setdefault("notes", [])

# update memory
if nl := stores.post_store.get("note_local"):
    notes = stores.session_store.get("notes")
    if notes is not None:
        notes.append(nl)
        stores.session_store.set("notes", notes)

if ng := stores.post_store.get("note_global"):
    notes = stores.global_store.get("notes")
    if notes is not None:
        notes.append(ng)
        stores.global_store.set("notes", notes)

with o.row(gap="2rem"):
    with o.column(gap="2rem"):
        with o.form(method="post"):
            with o.row():
                o.input(name="note_local")
                o.button("+ Add Local")
        o.h1("Local Notes")
        with o.ul():
            for note in stores.session_store.get("notes"):
                o.li(note)

    with o.column(gap="2rem"):
        with o.form(method="post"):
            with o.row():
                o.input(name="note_global")
                o.button("+ Add Global")
        o.h1("Global Notes")
        with o.ul():
            for note in stores.global_store.get("notes"):
                o.li(note)
