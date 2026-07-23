from ooklept import o


def use_pico_css():
    return o.link(
        rel="stylesheet",
        href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css",
    )
