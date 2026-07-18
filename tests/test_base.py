# tests/test_base.py

import pytest

from ooklept.base import Element, Text


# -----------------------------------------------------------------------------
# Basic rendering
# -----------------------------------------------------------------------------

def test_empty_element():
    assert str(Element("div")) == "<div></div>"


def test_void_element():
    assert str(Element("br")) == "<br />"


def test_text():
    e = Element("div").text("Hello")
    assert str(e) == "<div>Hello</div>"


def test_text_is_escaped():
    e = Element("div").text('<script>alert("x")</script>')
    assert (
        str(e)
        == "<div>&lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt;</div>"
    )


# -----------------------------------------------------------------------------
# Attributes
# -----------------------------------------------------------------------------

def test_attribute():
    e = Element("div").attr(id="abc")
    assert str(e) == '<div id="abc" ></div>'


def test_multiple_attributes():
    e = Element("div").attr(id="a", title="hello")
    s = str(e)

    assert 'id="a"' in s
    assert 'title="hello"' in s


def test_boolean_attribute_true():
    e = Element("input").attr(disabled=True)
    assert "<input disabled " in str(e)


def test_boolean_attribute_false():
    e = Element("input").attr(disabled=False)
    assert "disabled" not in str(e)


def test_attribute_escape():
    e = Element("div").attr(title='"<&>')
    assert '&quot;&lt;&amp;&gt;' in str(e)


def test_attr_rejects_style():
    with pytest.raises(KeyError):
        Element("div").attr(style="color:red")


def test_attr_rejects_class():
    with pytest.raises(KeyError):
        Element("div").attr(class_="abc")


# -----------------------------------------------------------------------------
# Style
# -----------------------------------------------------------------------------

def test_style():
    e = Element("div").style(color="red")
    s = str(e)

    assert 'style="' in s
    assert "color:red;" in s


def test_style_from_dict():
    e = Element("div").style({"margin": "10px"})
    assert "margin:10px;" in str(e)


def test_style_merge():
    e = Element("div")
    e.style(color="red")
    e.style(background="blue")

    s = str(e)

    assert "color:red;" in s
    assert "background:blue;" in s


# -----------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------

def test_single_class():
    e = Element("div").class_("container")
    assert 'class="container"' in str(e)


def test_multiple_classes():
    e = Element("div").class_("a b", "c")
    assert 'class="a b c"' in str(e)


def test_duplicate_class_moves_to_end():
    e = Element("div").class_("a b")
    e.class_("a")

    assert e._classes == ["b", "a"]


# -----------------------------------------------------------------------------
# Context manager
# -----------------------------------------------------------------------------

def test_context_children():
    with Element("div") as root:
        Element("span")

    assert str(root) == "<div><span></span></div>"


def test_nested_context():
    with Element("div") as root:
        with Element("span"):
            Element("b")

    assert str(root) == "<div><span><b></b></span></div>"


def test_text_inside_context():
    with Element("div") as root:
        Text("hello")

    assert str(root) == "<div>hello</div>"


def test_text_method():
    root = Element("div").text("abc")
    assert str(root) == "<div>abc</div>"


# -----------------------------------------------------------------------------
# Void elements
# -----------------------------------------------------------------------------

def test_void_element_cannot_have_children():
    with pytest.raises(Exception):
        with Element("img"):
            pass


# -----------------------------------------------------------------------------
# Chaining
# -----------------------------------------------------------------------------

def test_method_chaining():
    e = (
        Element("div")
        .attr(id="main")
        .style(color="red")
        .class_("container")
        .text("Hello")
    )

    s = str(e)

    assert 'id="main"' in s
    assert "color:red;" in s
    assert 'class="container"' in s
    assert ">Hello<" in s


# -----------------------------------------------------------------------------
# Context isolation
# -----------------------------------------------------------------------------

def test_element_created_outside_context_not_added():
    root = Element("div")
    Element("span")

    assert str(root) == "<div></div>"


def test_no_self_append():
    e = Element("div")
    assert e._children == []