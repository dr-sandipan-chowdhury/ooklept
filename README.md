# ooklept

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

# How to use
Import it
```python
from ooklept import Element as e
```
Create an element
```python
my_div = e("div")
```
Add attributes
```python
my_div.attr(id="mine")
```
Add some styles
```python
my_div.style(
    dislay = "flex", 
    justify_content="center", 
    align_items="center"
)
```
Add some classes
```python
my_div.classes("first-class", "this-class-not-exists")
```

Now print it
```python
print(my_div)
```

which prints to:
```html
<div id="mine" style="dislay:flex; justify-content:center; align-items:center;" class="first-class this-class-not-exists"></div>
```

Already awesome isn't it? If not, follow up...

To add a child use `with` statement:
```python
with my_div:
    e("input").attr(type="text", placeholder="username")
    e("input").attr(type="password", placeholder="your mom's name")
    with e("div").style(display="flex"):
        e("button").text("back")
        e("button").text("ok")

```
which upon printing give us:
```html
<div id="mine" style="dislay:flex; justify-content:center; align-items:center;" class="first-class this-class-not-exists"><input type="text" placeholder="username"></input><input type="password" placeholder="your mom&#x27;s name"></input><div  style="display:flex;"><button >back</button><button >ok</button></div></div>
```
# Enjoy Already