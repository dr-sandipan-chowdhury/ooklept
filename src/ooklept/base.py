"""
ooklept: A Thread-Safe Declarative Python DSL for HTML/CSS Generation.

What it does
============
You write some python code that behaves like if you were writing HTML/CSS. Its known as DSL (Domain Specific Language).
Using this library you make python act like a DSL for HTML/CSS.
Better easy-to-understand term would be: HTML+inline-CSS string generation library that uses
fancy pythonic class, methods, parameters and strong type suggesting pythonic features like Literals, TypedDicts and hell of
HTML/CSS documentation.

What it tastes like
===================
`Examples`

What do it cares
================
It cares about the:
    * Pain from copy pasting html/css multiple times and change little bit everytime if necessary:
       - Solves by: You create a function with parameters, call it with different parameters and get your HTML curated with those parameters
    * Pain from unfamiliar xml's angular bracket hell
        - Solves by: Easy pythonic syntax and `with` context-based childing so you dont get into parenthesis hell of Flutter
    * HTML is not an programming language, so conditions,loops are out of questions
        - Solves by: Come on... You use python... this already solves those by its very nature of being a programming language.

Possible Usecases
=================
Anywhere when it requires:
    * generating HTML/CSS with condition/loop rich data manipulation inside HTML/CSS skeleton.
    * UI Libraries
    * Full Stack backend-first apps
    * Frontend Apps using py-script, transcript, brython basically where python runs
    * Hybrid apps with tauri and python
    * You add: _


Easiest explanations of How does it work
========================================
Single most important class here is `Element`.
You only need to use this class only to get 100% of the features.
`Element` contains 5 most important data:
    * tag name: This contains the name of the tag e.g. "div"
    * class list: This contains the list of classes the tag has. e.g. ["my-custom-class-1", "my-custom-class-2"]
    * style dict: This contains the CSS Properties with their values e.g. {"display": "flex", "justify-content":"center", "align-items":"center"}
    * attr dict: This contains HTML attributes except "class" and "style" e.g. {"role":"button", "id":"my-btn"}
    * children list: This contains other `Element` as its children.

Now when you cast the `Element` to `str` using `str(Element)` it calls the overloaded `__str__` method that performs:
    * Fetches tag name and forms <div></div> in our case
    * Fetches the class list and incorporates it into class attr like <div class="my-custom-class-1 my-custom-class-2"></div>
    * Fetches the style dict and incorporates it into style attr like <div class="my-custom-class-1 my-custom-class-2" style="display:flex;justify-content:center;align-items:center"></div>
    * Fetches the attr dict and incorporates into the tag like <div role="button" id="my-btn" class="my-custom-class-1 my-custom-class-2" style="display:flex;justify-content:center;align-items:center"></div>
    * Then it recursively does it for every child and put the resultant string in >...</ like:
       - ```<div role="button" id="my-btn" class="my-custom-class-1 my-custom-class-2" style="display:flex;justify-content:center;align-items:center">
            <child1></child1>
            <child2></child2>
            <child3></child3>
            ...
       </div>```
    * then returns the whole string formed

This is just string interpolation nothing special... But what is special is how you create and change this internal 5 datas using python's syntax.
So, the Architectures goes:
    ```
    +-------------------------------------+
    | Pythonic Syntactic Sugar coated API |         [with, attr(), classes(), style()]
    +-------------------------------------+
                    |
                    | (Pre-processing)
                    |
        +--------------------------+
        | Internal Representations |                [name-str, class-list, style-dict, attr-dict]
        +--------------------------+
                    |
                    | (String Interpolation, Recursions happens here)
                    |
            +-------------------+
            | HTML + inline CSS |                   [html-str]
            +-------------------+

    ```


Pre-processing: Made Dumber to Make Powerful
============================================
How one should connect elegant APIs to correctly cast syntactic sugar coated data into IR? There are many ways,
but it chooses the dumbest way, that by another way made it powerful and less ambiguious.

The main problem with attr-dict and style-dict was their keys, they can contain "-" and may clash with python keywords space.
So, there is no generalised rule like everytime a snake_case is converted to a kebab-case, because if user wants this:
    ```<div my_id="fancy"></div>```
    Always converting snake_case to kebab_case will cause it to be: ```<div my-id="fancy"></div>```, Thats confusing...
Also it does limits the power of user.

So, instead a TypedDict is maintained for possible **kwargs in attr() and style(), generated using HTML5 and CSS3 specification.
if you use anything from the TypedDict, it cast it using the `pre_process`, otherwise things are left as it is, no pre_processing.
So user should not assume we change custom their attr/prop, we only and only change what we provide and promise to change(things in the TypedDict)

Further more, if user need an exotic attr/prop he can just use the `d` arg in the attr() and style() that is directly reflected into the IR.

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
        """Creates a-live `Element`.

        If initialized within the context (`with` block) of another `Element`,
        this element will automatically register itself as a child of that active parent.

        Args:
            name: The HTML tag name (e.g., 'div', 'span') or an webtypes.HTMLTag type.
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
        self._context_cache = None

        current = Element.current_context.get()
        if (
            current is not None and current is not self
        ):  # Fixed: Infinite recursion: a.children.append(a)
            current._children.append(self)

    def attr(self, d: dict[str, str] | None = None, **kwargs: Unpack[HTMLAttribute]):
        """
        Apply or update HTML attributes on this element.

        Accepts arguments as a dictionary mapping or as keywords. Values are
        html-escaped by default.

        Note:
            - Hyphenated attributes (e.g., `data-id`) are syntax-invalid as direct keyword
            arguments in Python. To set them, pass them inside a dictionary: `.attr({"data-id": "123"})`.
            - Only the keyword that is defined in the `webtypes.HTMLAttribute` TypedDict are eligible for
            auto-conversion from snake_case to kebab-case e.g. `http_eqiv` to `http-equiv ` and `accept_charset`
            to `accept-charset`. Your custom attribute names that is in snake_case e.g. `my_attr` remains untouched
            and produces the same attribute name i.e. `my_attr` in HTML side and not `my-attr`. If you want to use
            `my-attr` you should pass it via `d` parameter e.g. d = {"my-attr":"my-value"}
            - There are some HTML attributes that creates conflicts with the python's keywords (e.g. async, for, is).
            This are available in the webtypes.HTMLAttribute with trailing underscore i.e. async_, for_, is_. But you
            are completely free to use this attributes(i.e. async, for, is) as-is if you are using `d`.
            - You can not set `class` or `style` attribute of a tag using `.attr()`.
            - To set `class` use `.classes()`.
            - To set `style` use `.style()`.

        Args:
            d: Optional dictionary containing raw attribute keys and values. No case conversion i.e. (snake_to-kebab) is applied on the `d`, stays as it is. To use python's keyword as html attribute you have to use this. In all the cases, where **kwargs does not allows you to create specific attribute, you have to use `d`. It gives you freedom of application of HTML-madness.
            **kwargs: These should be of type `webtypes.HTMLAttribute` that undergoes `pre-processing` but remember if you use kwargs to pass your own attribute that is not listed as `webtypes.HTMLAttribute`, pre-processing algorithm does not run on your attribute that means:
                - No snake_to-kebab conversion happens on your custom attribute meaning if your attribute is `my_attr` it stays as `my_attr` in the HTML side.
                - No trailing underscored python keyword decoding happens meaing if you wanted to use a python keyword as your html attribute e.g. `not`, and for it you passed `not_` in kwargs, your `not_` stays `not_` in the html side and does not get converted to `not`. To use `not` in HTML side, you must use `d`.

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

    def _remove_attr(self, *attrs):
        """Removes one or more HTML attributes from the element.

        Args:
            *attrs: Variable-length list of attribute names to remove.

        Returns:
            The current Element instance to support method chaining.

        Raises:
            re.PatternError: If any attribute name fails validation via Helper.is_html_attr_name.
        """
        for attr in attrs:
            if not Helper.is_html_attr_name(attr):
                raise re.PatternError(f"Invalid HTML Attribute name: `{attr}`")

        for attr in attrs:
            self._attrs_dict.pop(attr, None)

        return self

    def classes(self, cls_str: str = "", *classes):
        """
        Add one or more CSS class names to the element.

        Supports space-separated class names or flat positional lists. Does not stores any Duplicate. Order of classes is maintained my the insertion order i.e. inserted later means appears later (towards the end of the class string).
        When same class name is re-inserted later it changes its order to be in the end.

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
                else:
                    self._classes.remove(c)
                    self._classes.append(c)  # Respects insertion orders.
        return self

    def _remove_classes(self, cls_str: str = "", *classes):
        """Removes one or more CSS classes from the element.

        Args:
            cls_str: A string of space-separated class names to remove.
            *classes: Individual class name strings to remove.

        Returns:
            The current Element instance to support method chaining.

        Raises:
            re.PatternError: If any class name is not a valid CSS identifier.
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

    def style(self, d: dict[str, str] | None = None, **kwargs: Unpack[CSSProperty]):
        """Adds or updates inline CSS styles on the element.

        Args:
            d: An optional dictionary containing CSS property-value pairs. Remember the keys you provide in the `d` will be inserted unaltered into the HTML inline style string.
            **kwargs: They are listed as `webtypes.CSSProperty` and pre-processing happens on this(i.e. snake_to-kebab conversion). If you use something unlisted, pre-processing does not happens, so properties are casted as it is, like `my-arbitary_property` in python side will produce the same and not `my-arbitary-property` in CSS side.

        Returns:
            The current Element instance to support method chaining.

        Raises:
            re.PatternError: If a generated CSS property is not a valid CSS identifier.
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

    def _remove_style(self, *styles):
        """Removes one or more inline CSS styles from the element.

        Args:
            *styles: CSS property names to remove (supports snake_case or kebab-case).

        Returns:
            The current Element instance to support method chaining.

        Raises:
            re.PatternError: If any property name is not a valid CSS identifier.
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

    def text(self, data: str):
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

    def __str__(self):
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
    """Represents a plain text node in the declarative HTML tree.

    This class automatically escapes HTML special characters to prevent cross-site
    scripting (XSS) and formatting breaks. Like `Element`, instantiating this class
    inside an active `Element`'s context block automatically registers it as a child.
    """

    def __init__(self, text: str) -> None:
        """Initializes a new Text node with escaped content.

        If initialized within the context (`with` block) of an `Element`,
        this text node will automatically append itself to that active parent.

        Args:
            text: The raw string content to be displayed.
        """
        self.value = html.escape(text)
        current = Element.current_context.get()
        if current is not None:
            current._children.append(self)

    def __str__(self):
        """Renders the text node to its safe, escaped string value.

        Returns:
            The HTML-escaped string.
        """
        return self.value
