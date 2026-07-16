import html
import json
import re
from contextvars import ContextVar
from typing import Unpack
from ooklept.webtypes import HTMLAttribute, CSSProperty, HTMLTag


class Helper:
    class_regices = (
        re.compile(r"^[A-Za-z_][A-Za-z0-9_-]*$"),
        re.compile(r"^-[A-Za-z_-][A-Za-z0-9_-]*$"),
    )
    attr_name_regex = re.compile(r'^[^\s\x00-\x1f\x7f-\x9f"\'<>/=]+$')

    @staticmethod
    def is_css_identifier(s: str):
        if any([i.match(s) for i in Helper.class_regices]):
            return True
        return False

    @staticmethod
    def is_html_attr_name(s: str):
        m = Helper.attr_name_regex.match(s)
        if m:
            return True
        return False


class Element:
    current_context: ContextVar["Element | None"] = ContextVar(
        "current_context", default=None
    )

    def __init__(self, name: HTMLTag | str):
        self.name = name
        self._attrs_dict = dict({})
        self._style_dict = dict({})  # To avoid decompilation of css strings to dict
        self._classes = list([])
        self._children = list([])
        self._context_cache = None

        current = Element.current_context.get()
        if (
            current is not None and current is not self
        ):  # Fixed: Infinite recursion: a.children.append(a)
            current._children.append(self)

    def attr(self, d: dict[str, str] | None = None, **kwargs:Unpack[HTMLAttribute]):
        d = dict(d or {})

        if kwargs.pop("style", None) or d.pop("style", None):
            raise KeyError("Please use .style() method instead.")
        if kwargs.pop("class", None) or d.pop("class", None):
            raise KeyError("Please use .classes() method instead.")

        kwargs.update(d)

        nkwargs = {}

        for k, v in kwargs.items():
            if not Helper.is_html_attr_name(k):
                raise re.PatternError(f"Invalid HTML Attribute name: `{k}`")
            nkwargs[k] = html.escape(str(v))

        self._attrs_dict.update(nkwargs)
        return self

    def remove_attr(self, *attrs):
        for attr in attrs:
            if not Helper.is_html_attr_name(attr):
                raise re.PatternError(f"Invalid HTML Attribute name: `{attr}`")

        for attr in attrs:
            self._attrs_dict.pop(attr, None)

        return self

    def classes(self, cls_str: str = "", *classes):
        classes = [*cls_str.split(), *classes]

        for c in classes:
            if not Helper.is_css_identifier(c):
                raise re.PatternError(f"{c} is not a valid CSS Identifier.")

        if len(classes) > 0:
            for c in classes:
                if c not in self._classes:
                    self._classes.append(c)
        return self

    def remove_classes(self, cls_str: str = "", *classes):
        classes = [*cls_str.split(), *classes]

        for c in classes:
            if not Helper.is_css_identifier(c):
                raise re.PatternError(f"{c} is not a valid CSS Identifier.")

        if len(classes) > 0:
            for c in classes:
                while c in self._classes:
                    self._classes.remove(c)
        return self

    def style(self, d: dict[str, str] | None = None, **kwargs:Unpack[CSSProperty]):
        d = dict(d or {})
        kwargs.update(d)
        nkwargs = {}
        for k, v in kwargs.items():
            nk = k.replace("_", "-")
            if Helper.is_css_identifier(nk):
                nkwargs[nk] = str(v)
            else:
                raise re.PatternError(
                    f"style kwarg `{k}` upon being converted to CSS property `{nk}` is not a valid CSS Identifier."
                )

        self._style_dict.update(nkwargs)
        return self

    def remove_style(self, *styles):
        nstyles = []

        for style in styles:
            style = style.replace("_", "-")
            if not Helper.is_css_identifier(style):
                raise re.PatternError(f"{style} is not a valid CSS Identifier.")
            nstyles.append(style)

        for style in nstyles:
            self._style_dict.pop(style, None)

        return self

    def __enter__(self):
        self._token = Element.current_context.set(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        Element.current_context.reset(self._token)

        if exc_type:
            print(f"An error occurred: {exc_val}")
            return False

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

        return f"<{self.name} {attr_str}>{''.join([str(i) for i in self._children])}</{self.name}>"


class Text:
    def __init__(self, text: str) -> None:
        self.value = html.escape(text)
        current = Element.current_context.get()
        if current is not None:
            current._children.append(self)

    def __str__(self):
        return self.value
