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

# Installation

```bash
pip install ooklept
```

## Basic Usage

- create a new directory e.g. `hello_project`
- in the directory create a file `index.py`
- write some code in `index.py`

```python
from ooklept import o

o.h1("Helloworld")
o.p("This is a helloworld project from ooklept.")

```

- run this command in the `hello_project` directory to serve:

```bash
python -m ooklept.serve
```

- go to `http://127.0.0.1:8000` in browser and see it

## DSL

- to create children under a tag

```python
from ooklept import o

with o.div():
    o.span("1st children")
    o.span("2nd children")
    with o.div(): #3rd children
        o.span("Grand children")

```

- use a for loop for children

```python
from ooklept import o

with o.ul():
    for i in range(10):
        o.li(f"Child No. {i}")

```

- use conditional tag creation

```python
from ooklept import o

if 3>2:
    o.span("3 is greater than 2!!!")
else:
    o.span("You will never see this.")

```

- to add style

```python
from ooklept import o

with o.div().style(display="flex", align_items="center", justify_content="space-evenly", width="100vw"):
    o.span("Hello")
    o.span("World")

```

- to add a attribute

```python
from ooklept import o

o.input(type="text", placeholder="enter name")

# or you can do
o.input().attr(type="text", placeholder="enter name")

# or hybrid
o.input(id="ip1", name="username").attr(type="text", placeholder="enter name")
```

- add any custom attribute

```python
from ooklept import o

o.div().attr(
    my_custom_attr_name="my_custom_attr_value",
    my_custom_attr_name_2="my_custom_attr_value_2"
)

# custom attribute names that are not valid python python identifier e.g. my-hyphened-attr
o.div().attr({"my-hyphened-attr": "custom-value"})

# hybrid
o.div().attr(
    {"my-hyphened-attr": "custom-value"},
    my_custom_attr_name="my_custom_attr_value",
    my_custom_attr_name_2="my_custom_attr_value_2"
)

```

- add class

```python
from ooklept import o

o.div().class_("cls1", "cls2", "cls3")

# this also works
o.div().class_("cls_1 cls_2 cls_3")

# hybrid approach
o.div().class_("cls_1 cls_2 cls_3", "cls_4", "cls_5")

```

- chaining

```python
from ooklept import o

o.div(id="x").attr(data_icon="icon.svg").class_("profile-icon").style(display="flex", justify_content="center", align_items="center")

```

## Routing
Directory and file based routing is supported
```
# path                                # page
mysite/
  |--index.py                         # /
  |--about.py                         # /about
  |--tools/                           
      |--index.py                     # /tools
      |--image_crop.py                # /tools/image_crop
      |--pdf_to_html.py               # /pdf_to_html
      |--video_tools/
            |--index.py               # /video_tools
            |--sound_extractor.py     # /video_tools/sound_extractor
```


## Stores

- Get/Post Stores
  - store the data passed in Request Object/ Form Data in every get/post request

```python
from ooklept import o, stores 

username = stores.get_store.get('username')

if username is None:
    with o.form(method="get"):
        o.input(name="username", placeholder="Enter your name")
else:
    o.h1(f"Welcome {username}")

# store.post_store works exactly like same just uses post 
```

- Session Stores: 
  - Clinet specific
  - Lives until a session is timed out e.g. Client closed his browser
```python
from ooklept import o, stores 

session_notes = store.session_store.setdefault("notes", [])

if note:=store.post_store.get("note"):
    session_notes.append(note)

with form(method="post"):
    o.input(name="note", placeholder="enter your note")

o.h1("Your Session Notes")
with o.ol():
    for note in session_notes:
        o.li(note)

```

- App Stores: 
  - Parmanent Global Storage
  - available to every page of the app

```python
from ooklept import o, stores 

app_notes = store.app_store.setdefault("notes", [])

if note:=store.post_store.get("note"):
    app_notes.append(note)

with form(method="post"):
    o.input(name="note", placeholder="enter your note")

o.h1("Your App Notes")
with o.ol():
    for note in app_notes:
        o.li(note)

```
  - Every client will see the same notes

- Page Stores
  - Page specific
  - One page can not access other pages storage
  - Otherwise Pretty much same as App Store
