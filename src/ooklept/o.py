from typing import Literal

from ooklept.base import Element
from ooklept.csrf import CSRF_FIELD_NAME, get_or_create_csrf_token
from ooklept.tags.tags_dump import *
from ooklept.webtypes import CSSPropertyTypes

_form = form


def row(
    justify: CSSPropertyTypes.justify_content = None,
    align: CSSPropertyTypes.align_items = None,
    gap: str | None = None,
):
    e = Element("div").style(display="flex", flex_direction="row")
    if justify:
        e.style(justify_content=justify)
    if align:
        e.style(align_items=align)
    if gap:
        e.style(gap=gap)
    return e


def column(
    justify: CSSPropertyTypes.justify_content = None,
    align: CSSPropertyTypes.align_items = None,
    gap: str | None = None,
):
    e = Element("div").style(display="flex", flex_direction="column")
    if justify:
        e.style(justify_content=justify)
    if align:
        e.style(align_items=align)
    if gap:
        e.style(gap=gap)
    return e


def csrf_field():
    """Call inside a `with form():` block to embed the anti-CSRF token."""
    token = get_or_create_csrf_token()
    Element("input").attr(type="hidden", name=CSRF_FIELD_NAME, value=token)


# forms upgraded with CSRF
def form(
    text: str | None = None,
    accept_charset: str | None = None,
    action: str | None = None,
    autocomplete: Literal["on", "off"] | str | None = None,
    enctype: Literal[
        "application/x-www-form-urlencoded", "multipart/form-data", "text/plain"
    ]
    | str
    | None = None,
    method: Literal["get", "post", "dialog"] | str | None = None,
    name: str | None = None,
    novalidate: Literal["true", "false"] | str | None = None,
    target: Literal["_self", "_blank", "_parent", "_top"] | str | None = None,
) -> Element:
    el = (
        Element("form")
        .attr(
            accept_charset=accept_charset,
            action=action,
            autocomplete=autocomplete,
            enctype=enctype,
            method=method,
            name=name,
            novalidate=novalidate,
            target=target,
        )
        .text(text)
    )
    if method is not None and method.strip().lower() == "post":
        with el:
            csrf_field()

    return el
