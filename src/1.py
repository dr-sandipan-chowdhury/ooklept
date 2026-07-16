from ooklept import Element as e

my_div = e("div")
my_div.attr(id="mine")

my_div.style(
    dislay = "flex", 
    justify_content="center", 
    align_items="center"
)

my_div.classes("first-class", "this-class-not-exists")
with my_div:
    e("input").attr(type="text", placeholder="username")
    e("input").attr(type="password", placeholder="your mom's name")
    with e("div").style(display="flex"):
        e("button").text("back")
        e("button").text("ok")
print(my_div)


