# ooklept/tags_gen.py

from pathlib import Path

from ooklept.utility import convert_thing_to_python_identifier
from ooklept.webtype_gen import htmlTags, literal_from_vs


def create_tag(
    fname: str | None, tname: str | None, params: dict[str, list[str]]
) -> str | None:
    if not fname or not tname:
        return None
    result = ""
    tab = " " * 4
    kpl = []
    for k, v in params.items():
        v = [f'"{vi}"' for vi in v]
        x = ", ".join(v)
        if x:
            x = f"Literal[{x}]"
        pl = [i for i in (x, "str", "None") if i != ""]
        p = " | ".join(pl) + " = None"
        kp = f"{k}:{p}"
        kpl.append(kp)
    head = f"def {fname}({', '.join(kpl)}) -> Element:"
    body = f'{tab}return Element("{tname}").attr({", ".join([k + " = " + k for k in params.keys() if k != "text"])}){".text(text)" if "text" in params else ""}'
    result = f"{head}\n{body}"
    return result


def create_tags_dump():
    result = "from ooklept.base import Element\nfrom typing import Literal\n\n"
    fs = []
    for tag in htmlTags:
        fname = ""
        params = {}
        tname = ""
        if tname := tag.get("name"):
            fname = convert_thing_to_python_identifier(tname)
        for attr in tag.get("attributes"):
            if aname := attr.get("name"):
                if params.get(aname) is None:
                    params[convert_thing_to_python_identifier(aname)] = []
                if vs := attr.get("valueSet"):
                    params[convert_thing_to_python_identifier(aname)] = literal_from_vs(
                        vs
                    )
        if not tag.get("void"):
            params = {"text": [], **params}
        fs.append(create_tag(fname, tname, params))
    result += "\n\n\n".join(fs)
    return result


def main():
    (Path(__file__).parent / "tags_dump.py").write_text(create_tags_dump())


if __name__ == "__main__":
    main()
