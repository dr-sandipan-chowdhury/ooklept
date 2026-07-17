"""
ooklept: A Thread-Safe Declarative Python DSL for HTML/CSS Generation.

This module implements a dynamic, object-oriented Domain Specific Language (DSL)
designed to construct HTML trees using standard Python syntax. By leveraging
Python's `with` statement and standard library `contextvars`, ooklept enables developers
to build nested layouts that mirror actual HTML hierarchy without manual nesting.

Key Features:
    - **Context-Aware Nesting**: Nest elements cleanly using context managers.
    - **Automatic Escaping**: Prevents Cross-Site Scripting (XSS) by automatically escaping text and attributes.
    - **Fluent Interface**: Methods support chainable calls (e.g., `Element("div").classes("card").style(color="red")`).
    - **Sanitization & Validation**: Standard regex verification ensures all HTML and CSS identifiers match specs.

Typical Usage:
    >>> from ooklept import Element, Text
    >>> with Element("div").classes("container") as container:
    ...     with Element("header"):
    ...         Element("h1").classes("title").text("Welcome!")
    ...     with Element("main"):
    ...         Text("Explore our custom declarative DSL framework.")
    >>> print(str(container))
    <div  class="container"><header ><h1  class="title">Welcome!</h1></header><main >Explore our custom declarative DSL framework.</main></div>
"""

import html
import json
import re
from contextvars import ContextVar
from typing import Unpack

from ooklept.webtypes import CSSProperty, HTMLAttribute, HTMLTag


class Helper:
    class_regices = (
        re.compile(r"^[A-Za-z_][A-Za-z0-9_-]*$"),
        re.compile(r"^-[A-Za-z_-][A-Za-z0-9_-]*$"),
    )
    attr_name_regex = re.compile(r'^[^\s\x00-\x1f\x7f-\x9f"\'<>/=]+$')

    @staticmethod
    def is_css_identifier(s: str) -> bool:
        if any([i.match(s) for i in Helper.class_regices]):
            return True
        return False

    @staticmethod
    def is_html_attr_name(s: str) -> bool:
        m = Helper.attr_name_regex.match(s)
        if m:
            return True
        return False


class Element:
    """
    Core of Everything.
    This class is used to build, modify, remove, rebuild tree of HTML elements.

    Attributes:
        public:
            name (HTMLTag | str): The tag element type (e.g. "div", "section").
        private:
            current_context (ContextVar[Element | None]): Global state tracker managing parent elements in the active execution context.
            _attrs_dict (dict): Map of element attribute keys to escaped values.
            _style_dict (dict): Map of kebab-case inline style declarations.
            _classes (list): Ordered list of distinct style class strings.
            _children (list): Sub-nodes (Elements or Text instances) contained inside this node.
    """

    current_context: ContextVar["Element | None"] = ContextVar(
        "current_context", default=None
    )

    def __init__(self, name: HTMLTag | str):
        """
        Creates a-live `Element`.

        If instantiated inside an active context block of another `Element`,
        it automatically registers itself as a child of that context.

        Args:
            name: The HTML tag identifier (e.g., 'div', 'p', or a webtypes HTMLTag enum).

        Examples:
            >>> print(Element("ul"))
            <ul></ul>
            >>> with Element("ul") as list_container:
            ...     Element("li")
            >>> print(list_container)
            <ul><li></li></ul>
        """
        self.name = name
        self._attrs_dict = dict({})
        self._style_dict = dict({})  # To avoid decompilation of css strings to dict
        self._classes = list([])
        self._children = list([])

        current = Element.current_context.get()
        if (
            current is not None and current is not self
        ):  # Fixed: Infinite recursion: a.children.append(a)
            current._children.append(self)

    def attr(
        self, d: dict[str, str] | None = None, **kwargs: Unpack[HTMLAttribute]
    ) -> "Element":
        """
        Apply or update HTML attributes on this element.

        Accepts arguments as a dictionary mapping or as keywords. Values are
        html-escaped by default.

        Note:
            - Hyphenated attributes (e.g., `data-id`) are syntax-invalid as direct keyword
            arguments in Python. To set them, pass them inside a dictionary: `.attr({"data-id": "123"})`.
            - You can not set `class` or `style` attribute of a tag using `.attr()`. To set `class` use `.classes()`
            and to set `style` use `.style()` method.

        Args:
            d: Optional dictionary containing raw attribute keys and values.
            **kwargs: Keyword arguments for easy inline attribute specification.

        Returns:
            The parent Element instance to support syntax chaining.

        Raises:
            KeyError: If elements attempt to define "style" or "class" via attributes (use `.style()` or `.classes()`).
            re.PatternError: If any attribute key fails HTML attribute syntax matching rules.

        Examples:
            >>> img = Element("img").attr(src="logo.png", alt="My Logo")
            >>> button = Element("button").attr({"data-role": "action", "aria-label": "Close"})
        """
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

    def remove_attr(self, *attrs: str) -> "Element":
        """
        Remove specified HTML attributes from this element's internal configuration.

        Args:
            *attrs: The labels of attributes to delete from the element.

        Returns:
            The parent Element instance to support syntax chaining.

        Raises:
            re.PatternError: If any provided attribute name fails validation.

        Examples:
            >>> link = Element("a").attr(href="#", rel="nofollow").remove_attr("rel")
        """
        for attr in attrs:
            if not Helper.is_html_attr_name(attr):
                raise re.PatternError(f"Invalid HTML Attribute name: `{attr}`")

        for attr in attrs:
            self._attrs_dict.pop(attr, None)

        return self

    def classes(self, cls_str: str = "", *classes: str) -> "Element":
        """
        Add one or more CSS class names to the element.

        Supports space-separated class names or flat positional lists. Duplicate class
        additions are silently filtered out.

        Args:
            cls_str: A stringcontaining one or more space-separated class designations.
            *classes: Extra positional arguments specifying standalone class strings.

        Returns:
            The parent Element instance to support syntax chaining.

        Raises:
            re.PatternError: If an argument is not a valid CSS identifier.

        Examples:
            >>> div = Element("div").classes("d-flex px-4", "border-rounded")
        """
        classes = [*cls_str.split(), *classes]

        for c in classes:
            if not Helper.is_css_identifier(c):
                raise re.PatternError(f"{c} is not a valid CSS Identifier.")

        if len(classes) > 0:
            for c in classes:
                if c not in self._classes:
                    self._classes.append(c)
        return self

    def remove_classes(self, cls_str: str = "", *classes: str) -> "Element":
        """
        Remove designated class definitions from the element's class collection.

        Args:
            cls_str: Space-separated collection of classes to omit.
            *classes: Variadic strings of target classes to clean.

        Returns:
            The parent Element instance to support syntax chaining.

        Raises:
            re.PatternError: If any clean target is structurally invalid.

        Examples:
            >>> div = Element("div").classes("active show").remove_classes("show")
        """
        classes = [*cls_str.split(), *classes]

        for c in classes:
            if not Helper.is_css_identifier(c):
                raise re.PatternError(f"{c} is not a valid CSS Identifier.")

        if len(classes) > 0:
            for c in classes:
                while c in self._classes:
                    self._classes.remove(c)
        return self

    def style(
        self, d: dict[str, str] | None = None, **kwargs: Unpack[CSSProperty]
    ) -> "Element":
        """
        Define inline CSS parameters for the current element.

        Accepts arguments as a dict mapping or keyword elements. Python snake_case keys
        (e.g., `background_color`) are translated automatically to CSS kebab-case (`background-color`).

        Args:
            d: Dictionary mapping of CSS properties to values.
            **kwargs: CSS attributes and parameters passed as keyword options.

        Returns:
            The parent Element instance to support syntax chaining.

        Raises:
            re.PatternError: If target CSS parameter keys form invalid CSS syntax.

        Examples:
            >>> block = Element("div").style(margin_top="10px", display="block")
        """
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

    def remove_style(self, *styles: str) -> "Element":
        """
        Delete specified style specifications from this element.

        Supports passing either snake_case (e.g. `font_size`) or kebab-case (e.g. `font-size`) attributes.

        Args:
            *styles: Style keys to strip.

        Returns:
            The parent Element instance to support syntax chaining.

        Raises:
            re.PatternError: If any query key does not validate as a CSS identifier structure.

        Examples:
            >>> box = Element("div").style(border="none").remove_style("border")
        """
        nstyles = []

        for style in styles:
            style = style.replace("_", "-")
            if not Helper.is_css_identifier(style):
                raise re.PatternError(f"{style} is not a valid CSS Identifier.")
            nstyles.append(style)

        for style in nstyles:
            self._style_dict.pop(style, None)

        return self

    def text(self, data: str) -> "Element":
        """
        Add a text leaf node inside this element's tree.

        Args:
            data: Raw text string to append. Special characters are auto-escaped.

        Returns:
            The parent Element instance to support syntax chaining.

        Examples:
            >>> paragraph = Element("p").text("Hello, World!")
        """
        with self:
            Text(data)
        return self

    def __enter__(self):
        self._token = Element.current_context.set(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        Element.current_context.reset(self._token)

        if exc_type:
            print(f"An error occurred: {exc_val}")
            return False

    def __str__(self) -> str:
        """
        Render this element and all downstream children to an HTML string format.

        Returns:
            Formatted, valid HTML string content.

        Examples:
            >>> doc = Element("span").classes("badge").text("New")
            >>> print(str(doc))
            <span  class="badge">New</span>
        """
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
    """
    A plain text node in the declarative HTML structure.

    This class automatically sanitizes content by running HTML escape sequences
    on init, preventing security layout injection risks.
    """

    def __init__(self, text: str) -> None:
        """
        Instantiate a new escaped Text node.

        If declared inside an active `with` statement belonging to an `Element`,
        it registers as a child automatically.

        Args:
            text: The unescaped input string.
        """
        self.value = html.escape(text)
        current = Element.current_context.get()
        if current is not None:
            current._children.append(self)

    def __str__(self) -> str:
        """
        Render the escaped string content of the node.

        Returns:
            An HTML-safe string block.
        """
        return self.value
