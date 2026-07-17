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
