# ooklept/base.py

import html
from contextvars import ContextVar
from typing import Unpack, get_args
from warnings import warn

from ooklept.utility import is_valid_attr_name, recover_thing_from_python_identifier
from ooklept.webtypes import CSSProperty, HTMLAttribute, HTMLTag, HTMLVoidTag


class Element:
    current_context: ContextVar["Element | None"] = ContextVar(
        "current_context", default=None
    )

    VOID_TAGS_SET = frozenset(get_args(HTMLVoidTag))

    def __init__(self, name: HTMLTag | str):
        self._name = name
        self._is_void = self._name in Element.VOID_TAGS_SET
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

    def attr(
        self, d: dict[str, str | bool] | None = None, **kwargs: Unpack[HTMLAttribute]
    ):
        "Values None or False are removed."
        d = dict(d or {})
        d = {k: v for k, v in d.items() if v is not None and v is not False}
        kwargs = {k: v for k, v in kwargs.items() if v is not None and v is not False}

        # you can't set style or class from attr to remove confusions
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
        processed = {
            recover_thing_from_python_identifier(k): v
            for k, v in to_be_preprocessed.items()
        }
        processed.update(d)  # prefernce d > kwargs
        self._attrs_dict.update(processed)
        return self

    def class_(self, cls_str: str = "", *classes):
        classes = [*cls_str.split(), *classes]

        if len(classes) > 0:
            for c in classes:
                if c not in self._classes:
                    self._classes.append(c)
                else:
                    self._classes.remove(c)
                    self._classes.append(c)  # Respects insertion orders.
        return self

    def style(
        self, d: dict[str, str | None] | None = None, **kwargs: Unpack[CSSProperty]
    ):
        d = dict[str, str | None](d or {})

        # None --> none
        nd = {}
        nkwargs = {}

        for k, v in d.items():
            if v is None:
                v = "none"
            nd[k] = v

        for k, v in kwargs.items():
            if v is None:
                v = "none"
            nkwargs[k] = v

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
        processed = {
            recover_thing_from_python_identifier(k): v
            for k, v in to_be_processed.items()
        }
        d.update(processed)  # preference d > kwargs
        self._style_dict.update(d)
        return self

    def text(self, data: str | None = None):
        if data is None:
            return self
        with self:
            Text(data)
        return self

    def __enter__(self):
        if self._is_void:
            raise Exception(
                f"`{self._name}` is a void tag hence can not have children. "
            )
        self._token = Element.current_context.set(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        Element.current_context.reset(self._token)

    def __str__(self):
        if not is_valid_attr_name(self._name):
            raise SyntaxError(f"{self._name} is not a valid html tag name")

        attr_str = ""
        for k, v in self._attrs_dict.items():
            if not is_valid_attr_name(k):
                raise SyntaxError(f"{k} is not a valid html attribute.")

            if isinstance(v, bool):
                if v is True:
                    attr_str += k + " "
            else:
                v = str(v)
                attr_str += k + "=" + f'"{html.escape(v, quote=True)}"' + " "

        if len(self._style_dict) > 0:
            style_val = " ".join([f"{k}:{v};" for k, v in self._style_dict.items()])
            attr_str += f' style="{html.escape(style_val, quote=True)}"'

        if len(self._classes) > 0:
            class_val = " ".join(self._classes)
            attr_str += f' class="{html.escape(class_val, quote=True)}"'

        if len(attr_str) > 0:
            attr_str = " " + attr_str

        if self._is_void:
            return f"<{self._name}{attr_str} />"

        return f"<{self._name}{attr_str}>{''.join([str(i) for i in self._children])}</{self._name}>"


class Text:
    def __init__(self, text: str) -> None:
        self.value = html.escape(text)
        current = Element.current_context.get()
        if current is not None:
            current._children.append(self)

    def __str__(self):
        return self.value
