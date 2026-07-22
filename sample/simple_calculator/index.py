from ooklept import o
from ooklept.stores import post_track

num1 = post_track("num1", 0, float)
num2 = post_track("num2", 0, float)


def calc_result():
    return num1 + num2


with o.form(method="post"):
    with o.row(gap="1rem"):
        o.input(name="num1", type="number", value=f"{num1}")
        o.span("+")
        o.input(name= "num2", type="number", value=f"{num2}")
        o.button("=")
        o.span(f"{calc_result()}")
