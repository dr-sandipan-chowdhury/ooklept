import html
import json
import re
from contextvars import ContextVar
from typing import Unpack
from warnings import warn
import keyword

from ooklept.webtypes import CSSProperty, HTMLAttribute, HTMLTag


def preprocess(non_py_word: str) -> str | None:
    if not non_py_word.isidentifier():
        if "-" in non_py_word:
            if non_py_word.rindex("-") == len(non_py_word) - 1:
                raise ValueError(
                    f"`-` in end of non_py_word `{non_py_word}` creates opening for ambiguity."
                )
            non_py_word = non_py_word.replace("-", "_")
        else:
            raise ValueError(
                f"non_py_word `{non_py_word}` contains characters that can't be casted to python identifier without data loss."
            )

    while non_py_word in keyword.kwlist:
        non_py_word += "_"
    return non_py_word


class Element:
    current_context: ContextVar["Element | None"] = ContextVar(
        "current_context", default=None
    )

    def __init__(self, name: HTMLTag | str):
        self.name = name
        self._attrs_dict = {}
        self._style_dict = {}
        self._classes = []
        self._children = []
        self._context_cache = None

        current = Element.current_context.get()
        if (
            current is not None and current is not self
        ):  # Fixed: Infinite recursion: a.children.append(a)
            current._children.append(self)

    def attr(self, d: dict[str, str] | None = None, **kwargs: Unpack[HTMLAttribute]):
        d = dict[str, str](d or {})

        if "style" in kwargs or "style" in d:
            raise KeyError("Please use .style() method instead.")
        if "class_" in kwargs or "class" in d:
            raise KeyError("Please use .classes() method instead.")

        to_be_preprocessed = {}
        for k, v in kwargs.items():
            if k in HTMLAttribute.__annotations__:
                to_be_preprocessed[k] = v
            else:
                if d.get(k) is None:
                    d[k] = v  # preference d > kwargs
                else:
                    warn(
                        f"html attr {k} in kwargs is wasted as it is already in `d`. Data lost."
                    )
        processed = {preprocess(k): v for k, v in to_be_preprocessed.items()}
        processed.update(d)  # prefernce d > kwargs
        self._attrs_dict.update(processed)
        return self

    def class_(self, cls_str: str = "", *classes):
        classes = [*cls_str.split(), *classes]

        for c in classes:
            if not Helper.is_css_identifier(c):
                raise re.PatternError(f"{c} is not a valid CSS Identifier.")

        if len(classes) > 0:
            for c in classes:
                if c not in self._classes:
                    self._classes.append(c)
                else:
                    self._classes.remove(c)
                    self._classes.append(c)  # Respects insertion orders.
        return self

    def style(self, d: dict[str, str] | None = None, **kwargs: Unpack[CSSProperty]):
        d = dict[str, str](d or {})
        to_be_processed = {}
        for k, v in kwargs.items():
            if k in CSSProperty.__annotations__:
                to_be_processed[k] = v
            else:
                if d.get(k) is None:
                    d[k] = v  # preference d > kwargs
                else:
                    warn(
                        f"css prop {k} in kwargs is wasted as it is already in `d`. Data lost."
                    )
        processed = {preprocess(k): v for k, v in to_be_processed.items()}
        d.update(processed)  # preference d > kwargs
        self._style_dict.update(d)
        return self

    def text(self, data: str):
        with self:
            Text(data)
        return self

    def __enter__(self):
        self._token = Element.current_context.set(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        Element.current_context.reset(self._token)

    def __str__(self):
        attr_str = " ".join(
            [f"{k}={json.dumps(str(v))}" for k, v in self._attrs_dict.items()]
        )

        if len(self._style_dict) > 0:
            style_str = json.dumps(
                " ".join([f"{k}:{v};" for k, v in self._style_dict.items()])
            )
            attr_str += f" style={style_str}"

        if len(self._classes) > 0:
            class_str = json.dumps(" ".join(self._classes))
            attr_str += f" class={class_str}"

        if len(attr_str) > 0:
            attr_str = " " + attr_str

        return f"<{self.name}{attr_str}>{''.join([str(i) for i in self._children])}</{self.name}>"


class Text:
    def __init__(self, text: str) -> None:
        self.value = html.escape(text)
        current = Element.current_context.get()
        if current is not None:
            current._children.append(self)

    def __str__(self):
        return self.value
