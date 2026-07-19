# ooklept/webtype_gen.py

import json
from pathlib import Path

from ooklept.helper import convert_thing_to_python_identifier

# Define and Validate `webdata
webdata_dir = Path(__file__).parent / "webdata"

if not webdata_dir.is_dir():
    raise NotADirectoryError(
        "FatalError: Can't find `webdata` dir in the project root."
    )

htmlEventsFile = webdata_dir / "htmlEvents.json"
htmlGlobalAttributesFile = webdata_dir / "htmlGlobalAttributes.json"
htmlTagsFile = webdata_dir / "htmlTags.json"
valueSetsFile = webdata_dir / "valueSets.json"
css_schemaFile = webdata_dir / "css-schema.json"

if not htmlEventsFile.is_file():
    raise FileNotFoundError(f"Corrupted `webdata` dir. `{htmlEventsFile}` not found.")

if not htmlGlobalAttributesFile.is_file():
    raise FileNotFoundError(
        f"Corrupted `webdata` dir. `{htmlGlobalAttributesFile}` not found."
    )

if not htmlTagsFile.is_file():
    raise FileNotFoundError(f"Corrupted `webdata` dir. `{htmlTagsFile}` not found.")

if not valueSetsFile.is_file():
    raise FileNotFoundError(f"Corrupted `webdata` dir. `{valueSetsFile}` not found.")

if not css_schemaFile.is_file():
    raise FileNotFoundError(f"Corrupted `webdata` dir. `{css_schemaFile}` not found.")


# Loading as JSON
with open(htmlEventsFile) as f:
    htmlEvents = json.load(f)

with open(htmlGlobalAttributesFile) as f:
    htmlGlobalAttributes = json.load(f)

with open(htmlTagsFile) as f:
    htmlTags = json.load(f)

with open(valueSetsFile) as f:
    valueSets = json.load(f)

with open(css_schemaFile) as f:
    css_schema = json.load(f)


# Funs


def create_imports():
    return """from typing import Literal, TypedDict

"""


def create_HTMLTag():
    taglist = []
    for tag in htmlTags:
        if tname := tag.get("name"):
            taglist.append(tname)
    return f"""
HTMLTag = Literal{taglist}
"""


def create_HTMLVoidTag():
    taglist = []
    for tag in htmlTags:
        if tname := tag.get("name"):
            if tag.get("void"):
                taglist.append(tname)
    return f"""
HTMLVoidTag = Literal{taglist}
"""


def literal_from_vs(s: str) -> list[str]:
    result = []
    for v in valueSets:
        if v.get("name") == s:
            if vals := v.get("values"):
                for val in vals:
                    if vname := val.get("name"):
                        result.append(vname)
    return result


def create_HTMLAttribute():
    attrs = dict[str, list[str]]()
    # 1. Specific Attributes
    for tag in htmlTags:
        if attributes := tag.get("attributes"):
            for attribute in attributes:
                if aname := attribute.get("name"):
                    if attrs.get(aname) is None:
                        attrs[aname] = []
                    if vs := attribute.get("valueSet"):
                        attrs[aname].extend(literal_from_vs(vs))

    # 2. Global Attributes
    for attr in htmlGlobalAttributes:
        if aname := attr.get("name"):
            if attrs.get(aname) is None:
                attrs[aname] = []
            if vs := attr.get("valueSet"):
                attrs[aname].extend(literal_from_vs(vs))

    # 3. Events
    for attr in htmlEvents:
        if aname := attr.get("name"):
            if attrs.get(aname) is None:
                attrs[aname] = []
            if vs := attr.get("valueSet"):
                attrs[aname].extend(literal_from_vs(vs))

    # compressing
    nattrs = {}
    for k, v in attrs.items():
        v2 = list(set(v))
        v2.sort()
        nattrs[k] = v2
    attrs = nattrs

    # with open("xxx.json", "w") as f:
    #     import json
    #     json.dump(attrs, f, indent=4)
    result = """
class HTMLAttribute(TypedDict, total=False):
"""
    for k, v in attrs.items():
        result += f"    {convert_thing_to_python_identifier(k)}: "
        if len(v) > 0:
            result += "Literal["
            for vi in v:
                result += f'"{vi}", '
            result += "] | "
        if "true" in v and "false" in v:
            result += "bool | "
        result += "str | None\n"

    return result


def create_CSSProperty():
    result = """
class CSSProperty(TypedDict, total=False):
"""
    kwlist = set()
    kw_val_dict = dict()
    if css := css_schema.get("css"):
        if properties := css.get("properties"):
            if properties := properties.get("entry"):
                for prop in properties:
                    if dollar_prop := prop.get("$"):
                        if pname := dollar_prop.get("name"):
                            kwlist.add(pname)
                            if "enum" in dollar_prop.get("restriction"):
                                if vals := prop.get("values"):
                                    if val := vals.get("value"):
                                        if isinstance(val, list):
                                            for v in val:
                                                if v_ := v.get("$"):
                                                    if vname := v_.get("name"):
                                                        if (
                                                            kw_val_dict.get(pname)
                                                            is None
                                                        ):
                                                            kw_val_dict[pname] = [vname]
                                                        else:
                                                            kw_val_dict[pname].append(
                                                                vname
                                                            )
                            if restriction := dollar_prop.get("restriction"):
                                rl = [restriction]
                                if kw_val_dict.get(pname) is None:
                                    kw_val_dict[pname] = rl
                                else:
                                    kw_val_dict[pname] = rl + kw_val_dict[pname]
    kwlist = list(kwlist)
    kwlist.sort()
    pylist = [i.replace("-", "_") for i in kwlist]
    for i, k in enumerate(pylist):
        typestr = ""
        pytypestr = "str"
        if ens := kw_val_dict.get(kwlist[i]):
            for i in ens:
                typestr += f'"{i}", '
        if len(typestr) > 0:
            typestr = f"Literal[{typestr}] | "
        result += f"    {k}: {typestr}{pytypestr.rstrip().rstrip('|')}\n"

    return result


def summate():
    return f"""# Autogenerated with `webdata` and `webtype_gen`

{create_imports()}
{create_HTMLTag()}
{create_HTMLVoidTag()}
{create_HTMLAttribute()}
{create_CSSProperty()}
"""


def main():
    with open(Path(__file__).parent / "webtypes.py", "w") as f:
        f.write(summate().strip() + "\n")


if __name__ == "__main__":
    main()
