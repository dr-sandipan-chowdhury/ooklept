# ooklept/helper.py

import keyword


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
