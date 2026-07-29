<p align="center">
<img src="https://raw.githubusercontent.com/dr-sandipan-chowdhury/ooklept/refs/heads/main/ooklept-banner-logo.svg" alt="ooklept banner">
</p>


```
                      [ OOKLEPT ]
                     ( Egg Thief )
                           |
         +----------------+----------------+
         |                                 |
     [ oo- ]                         [ -klept ]
 (Combining Form)                 (Combining Form)
         |                                 |
   Ancient Greek                     Ancient Greek
    ᾠόν (ōión)                       κλέπτης (kléptēs)
     "an egg"                           "a thief"
```

## Definition:
Ooklept is a backend only full stack development library that ships:
* a html+css generation mechanism from pythonic classes, methods, `with` based childing and ui creation with conditional statements and loops with full typing hint of standard html, css specs. 
* a directory and page based `serve` mechanism to run pages that contains ui and logic altogether following the philosophy of PHP i.e. "page is logic".

## How to use
- install with `pip install ooklept`
- make a new directory `helloworld`
- create a new file `index.py` inside `helloworld` directory.
- put some pythonic html inside it:   
```python
from ooklept import o
from ooklept.stores import stores


name = stores.post_store.setdefault("name", "John Doe")


if name == "John Doe":
    o.h1("Hi, John")
else:
    o.h1(f"Hello {name}")


with o.form():
    o.input(name="name", placeholder="enter name")
    o.button("greet me")

```

- run this using `ooklept -m serve` in your `helloworld` directory.
