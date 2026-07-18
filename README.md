<p align="center">
  <img src="logo.svg" width="180" alt="Ooklept logo">
  <center><h1 style="font-family: monospace;"><span style="color:goldenrod">oo</span><span style="color: rgba(0, 44, 126, 0.827)">klept</span></h1></center>
</p>



```

                      [ OOKLEPT ]
                     ( Egg Thief )
                          |
         +----------------+----------------+
         |                                 |
     [ oo- ]                          [ -klept ]
 (Combining Form)                  (Combining Form)
         |                                 |
   Ancient Greek                     Ancient Greek
    ᾠόν (ōión)                       κλέπτης (kléptēs)
     "an egg"                           "a thief"
```

**ooklept** or '*egg thief*' refers to python(🐍) the snake that steals bird's eggs(🪺/🥚). 

Here python(The programming language) steals HTML+CSS and makes a DSL for them.


# `ooklept.Element`

`Element` is the fundamental building block of Ooklept. Every HTML element—from a simple `<div>` to a complex nested page—is represented by an `Element` instance.

The API is designed around **method chaining**, **context managers**, and **typed attributes**, allowing HTML to be written in idiomatic Python.

---

# Creating an Element

Create an element by providing its HTML tag name.

```python
from ooklept import Element

div = Element("div")
print(div)
```

Output

```html
<div></div>
```

---

# Adding Attributes

Use `.attr()` to assign HTML attributes.

```python
div = (
    Element("div")
    .attr(id="main", title="Hello")
)

print(div)
```

Output

```html
<div id="main" title="Hello"></div>
```

Attributes may also be supplied using a dictionary.

```python
Element("div").attr({
    "data-user": "alice",
    "aria-hidden": "true",
})
```

Dictionary values take precedence over keyword arguments when the same attribute is provided.

---

# Boolean Attributes

Boolean HTML attributes are rendered only when their value is `True`.

```python
Element("input").attr(disabled=True)
```

Output

```html
<input disabled />
```

```python
Element("input").attr(disabled=False)
```

Output

```html
<input />
```

---

# CSS Classes

Use `.class_()` to assign CSS classes.

```python
Element("div").class_("container")
```

Output

```html
<div class="container"></div>
```

Multiple classes may be provided.

```python
Element("div").class_("container fluid", "shadow")
```

Output

```html
<div class="container fluid shadow"></div>
```

Calling `.class_()` repeatedly does not duplicate existing classes. If an existing class is added again, it is moved to the end while preserving uniqueness.

---

# Inline Styles

Use `.style()` to define inline CSS.

```python
Element("div").style(color="red")
```

Output

```html
<div style="color:red;"></div>
```

Multiple properties may be supplied.

```python
Element("div").style(
    color="white",
    background_color="black",
    margin="10px",
)
```

Output

```html
<div style="color:white; background-color:black; margin:10px;"></div>
```

Properties may also be provided as a dictionary.

```python
Element("div").style({
    "border-radius": "8px",
    "padding": "1rem",
})
```

Dictionary values override duplicate keyword arguments.

---

# Adding Text

Use `.text()` to insert escaped text into an element.

```python
Element("p").text("Hello, world!")
```

Output

```html
<p>Hello, world!</p>
```

Text is automatically HTML escaped.

```python
Element("p").text("<b>Hello</b>")
```

Output

```html
<p>&lt;b&gt;Hello&lt;/b&gt;</p>
```

---

# Nesting Elements

`Element` implements Python's context manager protocol, making deeply nested HTML easy to write.

```python
with Element("div") as page:
    Element("h1").text("Ooklept")
    Element("p").text("Hello!")

print(page)
```

Output

```html
<div>
    <h1>Ooklept</h1>
    <p>Hello!</p>
</div>
```

Nested contexts work naturally.

```python
with Element("div") as page:
    with Element("section"):
        Element("h2").text("Title")
        Element("p").text("Content")
```

Produces

```html
<div>
    <section>
        <h2>Title</h2>
        <p>Content</p>
    </section>
</div>
```

---

# Method Chaining

All modifier methods return the element itself, allowing concise fluent code.

```python
card = (
    Element("div")
    .attr(id="profile")
    .class_("card")
    .style(
        padding="1rem",
        border="1px solid #ddd",
    )
    .text("Hello!")
)
```

---

# Void Elements

Void elements (such as `img`, `br`, `input`, and `hr`) cannot contain children.

```python
Element("img")
```

Output

```html
<img />
```

Attempting to enter a void element as a context manager raises an exception.

```python
with Element("img"):
    ...
```

---

# Automatic Escaping

Ooklept automatically escapes HTML special characters inside:

* text nodes
* attribute values
* class values
* style attribute values

Example

```python
Element("div").attr(title='"Hello"')
```

Produces

```html
<div title="&quot;Hello&quot;"></div>
```

This prevents accidental HTML injection while keeping the API simple.

---

# Typed Keyword Arguments

If your editor supports static typing, Ooklept provides autocomplete for standard HTML attributes and CSS properties through Python type hints.

For example,

```python
Element("div").attr(
    hidden=True,
    draggable="true",
)

Element("div").style(
    background_color="red",
    font_size="18px",
)
```

Python identifiers are automatically converted into valid HTML/CSS names where necessary.

For example:

| Python             | HTML/CSS           |
| ------------------ | ------------------ |
| `class_`           | `class`            |
| `http_equiv`       | `http-equiv`       |
| `background_color` | `background-color` |

---

# Complete Example

```python
from ooklept import Element

with Element("main").class_("container") as page:

    Element("h1").text("Welcome")

    with Element("section").class_("content"):

        (
            Element("button")
            .class_("btn", "btn-primary")
            .style(
                background_color="#2563eb",
                color="white",
                padding="0.75rem 1rem",
            )
            .text("Click me")
        )

print(page)
```

Produces

```html
<main class="container">
    <h1>Welcome</h1>
    <section class="content">
        <button
            class="btn btn-primary"
            style="background-color:#2563eb; color:white; padding:0.75rem 1rem;"
        >
            Click me
        </button>
    </section>
</main>
```

---

# Summary

`Element` provides a Pythonic interface for generating HTML with:

* Fluent method chaining
* Automatic HTML escaping
* Typed HTML attributes and CSS properties
* Context-manager-based nesting
* Automatic child management
* Support for boolean attributes
* Unique CSS class handling
* Proper handling of HTML void elements

Together, these features enable expressive, readable, and type-safe HTML generation entirely in Python.

