# ooklept/helper.py

import keyword
import re
import sys
from dataclasses import dataclass

_html_attr_looks_like = re.compile(r"^[a-zA-Z-_][a-zA-Z0-9_-]*$")


def convert_thing_to_python_identifier(thing: str) -> str | None:
    if thing == "":
        return None
    if "_" in thing or thing[-1] == "-":
        return None

    if not thing.isidentifier():
        thing = thing.replace("-", "_")
        if not thing.isidentifier():
            return None  # some other characters causes this failure rather than hyphen

    if thing in keyword.kwlist:
        thing += "_"
    return thing


def recover_thing_from_python_identifier(python_identifier: str) -> str | None:
    "recovers what converted using `convert_thing_to_python_identifier`"
    if python_identifier == "":
        return None

    if python_identifier[-1] == "_":
        if python_identifier[-1] == "_":
            python_identifier = python_identifier[:-1]

        if python_identifier not in keyword.kwlist:
            return None

    thing = python_identifier.replace("_", "-")
    return thing


@dataclass
class MultiDict:
    _GET: dict[str, str]
    _POST: dict[str, str]


def get_multi_dict():
    return MultiDict(
        _GET=sys._getframe(1).f_globals.get("_GET", {}),
        _POST=sys._getframe(1).f_globals.get("_POST", {}),
    )


def is_valid_attr_name(attr_name: str):
    return _html_attr_looks_like.match(attr_name)
