from typing import Literal

from ooklept.base import Element
from ooklept.webtypes import CSSPropertyTypes
from ooklept.tags.tags_dump import *

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
