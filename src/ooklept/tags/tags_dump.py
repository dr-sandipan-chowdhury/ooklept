from ooklept.base import Element
from typing import Literal

def html(text:str | None = None, manifest:str | None = None) -> Element:
    return Element("html").attr(manifest = manifest).text(text)


def head(text:str | None = None) -> Element:
    return Element("head").attr().text(text)


def title(text:str | None = None) -> Element:
    return Element("title").attr().text(text)


def base(href:str | None = None, target:Literal["_self", "_blank", "_parent", "_top"] | str | None = None) -> Element:
    return Element("base").attr(href = href, target = target)


def link(href:str | None = None, crossorigin:Literal["anonymous", "use-credentials"] | str | None = None, rel:str | None = None, media:str | None = None, hreflang:str | None = None, type:str | None = None, sizes:str | None = None) -> Element:
    return Element("link").attr(href = href, crossorigin = crossorigin, rel = rel, media = media, hreflang = hreflang, type = type, sizes = sizes)


def meta(name:str | None = None, http_equiv:str | None = None, content:str | None = None, charset:str | None = None) -> Element:
    return Element("meta").attr(name = name, http_equiv = http_equiv, content = content, charset = charset)


def style(text:str | None = None, media:str | None = None, nonce:str | None = None, type:str | None = None, scoped:Literal["true", "false"] | str | None = None) -> Element:
    return Element("style").attr(media = media, nonce = nonce, type = type, scoped = scoped).text(text)


def body(text:str | None = None, onafterprint:str | None = None, onbeforeprint:str | None = None, onbeforeunload:str | None = None, onhashchange:str | None = None, onlanguagechange:str | None = None, onmessage:str | None = None, onoffline:str | None = None, ononline:str | None = None, onpagehide:str | None = None, onpageshow:str | None = None, onpopstate:str | None = None, onstorage:str | None = None, onunload:str | None = None) -> Element:
    return Element("body").attr(onafterprint = onafterprint, onbeforeprint = onbeforeprint, onbeforeunload = onbeforeunload, onhashchange = onhashchange, onlanguagechange = onlanguagechange, onmessage = onmessage, onoffline = onoffline, ononline = ononline, onpagehide = onpagehide, onpageshow = onpageshow, onpopstate = onpopstate, onstorage = onstorage, onunload = onunload).text(text)


def article(text:str | None = None) -> Element:
    return Element("article").attr().text(text)


def section(text:str | None = None) -> Element:
    return Element("section").attr().text(text)


def nav(text:str | None = None) -> Element:
    return Element("nav").attr().text(text)


def aside(text:str | None = None) -> Element:
    return Element("aside").attr().text(text)


def h1(text:str | None = None) -> Element:
    return Element("h1").attr().text(text)


def h2(text:str | None = None) -> Element:
    return Element("h2").attr().text(text)


def h3(text:str | None = None) -> Element:
    return Element("h3").attr().text(text)


def h4(text:str | None = None) -> Element:
    return Element("h4").attr().text(text)


def h5(text:str | None = None) -> Element:
    return Element("h5").attr().text(text)


def h6(text:str | None = None) -> Element:
    return Element("h6").attr().text(text)


def header(text:str | None = None) -> Element:
    return Element("header").attr().text(text)


def footer(text:str | None = None) -> Element:
    return Element("footer").attr().text(text)


def address(text:str | None = None) -> Element:
    return Element("address").attr().text(text)


def p(text:str | None = None) -> Element:
    return Element("p").attr().text(text)


def hr() -> Element:
    return Element("hr").attr()


def pre(text:str | None = None) -> Element:
    return Element("pre").attr().text(text)


def blockquote(text:str | None = None, cite:str | None = None) -> Element:
    return Element("blockquote").attr(cite = cite).text(text)


def ol(text:str | None = None, reversed:Literal["true", "false"] | str | None = None, start:str | None = None, type:Literal["1", "a", "A", "i", "I"] | str | None = None) -> Element:
    return Element("ol").attr(reversed = reversed, start = start, type = type).text(text)


def ul(text:str | None = None) -> Element:
    return Element("ul").attr().text(text)


def li(text:str | None = None, value:str | None = None) -> Element:
    return Element("li").attr(value = value).text(text)


def dl(text:str | None = None) -> Element:
    return Element("dl").attr().text(text)


def dt(text:str | None = None) -> Element:
    return Element("dt").attr().text(text)


def dd(text:str | None = None) -> Element:
    return Element("dd").attr().text(text)


def figure(text:str | None = None) -> Element:
    return Element("figure").attr().text(text)


def figcaption(text:str | None = None) -> Element:
    return Element("figcaption").attr().text(text)


def main(text:str | None = None) -> Element:
    return Element("main").attr().text(text)


def div(text:str | None = None) -> Element:
    return Element("div").attr().text(text)


def a(text:str | None = None, href:str | None = None, target:Literal["_self", "_blank", "_parent", "_top"] | str | None = None, download:str | None = None, ping:str | None = None, rel:str | None = None, hreflang:str | None = None, type:str | None = None) -> Element:
    return Element("a").attr(href = href, target = target, download = download, ping = ping, rel = rel, hreflang = hreflang, type = type).text(text)


def em(text:str | None = None) -> Element:
    return Element("em").attr().text(text)


def strong(text:str | None = None) -> Element:
    return Element("strong").attr().text(text)


def small(text:str | None = None) -> Element:
    return Element("small").attr().text(text)


def s(text:str | None = None) -> Element:
    return Element("s").attr().text(text)


def cite(text:str | None = None) -> Element:
    return Element("cite").attr().text(text)


def q(text:str | None = None, cite:str | None = None) -> Element:
    return Element("q").attr(cite = cite).text(text)


def dfn(text:str | None = None) -> Element:
    return Element("dfn").attr().text(text)


def abbr(text:str | None = None) -> Element:
    return Element("abbr").attr().text(text)


def ruby(text:str | None = None) -> Element:
    return Element("ruby").attr().text(text)


def rb(text:str | None = None) -> Element:
    return Element("rb").attr().text(text)


def rt(text:str | None = None) -> Element:
    return Element("rt").attr().text(text)


def rp(text:str | None = None) -> Element:
    return Element("rp").attr().text(text)


def time(text:str | None = None, datetime:str | None = None) -> Element:
    return Element("time").attr(datetime = datetime).text(text)


def code(text:str | None = None) -> Element:
    return Element("code").attr().text(text)


def var(text:str | None = None) -> Element:
    return Element("var").attr().text(text)


def samp(text:str | None = None) -> Element:
    return Element("samp").attr().text(text)


def kbd(text:str | None = None) -> Element:
    return Element("kbd").attr().text(text)


def sub(text:str | None = None) -> Element:
    return Element("sub").attr().text(text)


def sup(text:str | None = None) -> Element:
    return Element("sup").attr().text(text)


def i(text:str | None = None) -> Element:
    return Element("i").attr().text(text)


def b(text:str | None = None) -> Element:
    return Element("b").attr().text(text)


def u(text:str | None = None) -> Element:
    return Element("u").attr().text(text)


def mark(text:str | None = None) -> Element:
    return Element("mark").attr().text(text)


def bdi(text:str | None = None) -> Element:
    return Element("bdi").attr().text(text)


def bdo(text:str | None = None) -> Element:
    return Element("bdo").attr().text(text)


def span(text:str | None = None) -> Element:
    return Element("span").attr().text(text)


def br() -> Element:
    return Element("br").attr()


def wbr() -> Element:
    return Element("wbr").attr()


def ins(text:str | None = None) -> Element:
    return Element("ins").attr().text(text)


def del_(text:str | None = None, cite:str | None = None, datetime:str | None = None) -> Element:
    return Element("del").attr(cite = cite, datetime = datetime).text(text)


def picture(text:str | None = None) -> Element:
    return Element("picture").attr().text(text)


def img(alt:str | None = None, src:str | None = None, srcset:str | None = None, crossorigin:Literal["anonymous", "use-credentials"] | str | None = None, usemap:str | None = None, ismap:Literal["true", "false"] | str | None = None, width:str | None = None, height:str | None = None, decoding:Literal["sync", "async", "auto"] | str | None = None, loading:Literal["eager", "lazy"] | str | None = None, fetchpriority:Literal["high", "low", "auto"] | str | None = None, referrerpolicy:Literal["no-referrer", "no-referrer-when-downgrade", "origin", "origin-when-cross-origin", "same-origin", "strict-origin", "strict-origin-when-cross-origin", "unsafe-url"] | str | None = None, sizes:str | None = None) -> Element:
    return Element("img").attr(alt = alt, src = src, srcset = srcset, crossorigin = crossorigin, usemap = usemap, ismap = ismap, width = width, height = height, decoding = decoding, loading = loading, fetchpriority = fetchpriority, referrerpolicy = referrerpolicy, sizes = sizes)


def iframe(text:str | None = None, src:str | None = None, srcdoc:str | None = None, name:str | None = None, sandbox:Literal["allow-forms", "allow-modals", "allow-pointer-lock", "allow-popups", "allow-popups-to-escape-sandbox", "allow-same-origin", "allow-scripts", "allow-top-navigation"] | str | None = None, seamless:Literal["true", "false"] | str | None = None, allowfullscreen:Literal["true", "false"] | str | None = None, width:str | None = None, height:str | None = None) -> Element:
    return Element("iframe").attr(src = src, srcdoc = srcdoc, name = name, sandbox = sandbox, seamless = seamless, allowfullscreen = allowfullscreen, width = width, height = height).text(text)


def embed(src:str | None = None, type:str | None = None, width:str | None = None, height:str | None = None) -> Element:
    return Element("embed").attr(src = src, type = type, width = width, height = height)


def object(text:str | None = None, data:str | None = None, type:str | None = None, typemustmatch:Literal["true", "false"] | str | None = None, name:str | None = None, usemap:str | None = None, form:str | None = None, width:str | None = None, height:str | None = None) -> Element:
    return Element("object").attr(data = data, type = type, typemustmatch = typemustmatch, name = name, usemap = usemap, form = form, width = width, height = height).text(text)


def param(name:str | None = None, value:str | None = None) -> Element:
    return Element("param").attr(name = name, value = value)


def video(text:str | None = None, src:str | None = None, crossorigin:Literal["anonymous", "use-credentials"] | str | None = None, poster:str | None = None, preload:Literal["none", "metadata", "auto"] | str | None = None, autoplay:Literal["true", "false"] | str | None = None, mediagroup:str | None = None, loop:Literal["true", "false"] | str | None = None, muted:Literal["true", "false"] | str | None = None, controls:Literal["true", "false"] | str | None = None, width:str | None = None, height:str | None = None) -> Element:
    return Element("video").attr(src = src, crossorigin = crossorigin, poster = poster, preload = preload, autoplay = autoplay, mediagroup = mediagroup, loop = loop, muted = muted, controls = controls, width = width, height = height).text(text)


def audio(text:str | None = None, src:str | None = None, crossorigin:Literal["anonymous", "use-credentials"] | str | None = None, preload:Literal["none", "metadata", "auto"] | str | None = None, autoplay:Literal["true", "false"] | str | None = None, mediagroup:str | None = None, loop:Literal["true", "false"] | str | None = None, muted:Literal["true", "false"] | str | None = None, controls:Literal["true", "false"] | str | None = None) -> Element:
    return Element("audio").attr(src = src, crossorigin = crossorigin, preload = preload, autoplay = autoplay, mediagroup = mediagroup, loop = loop, muted = muted, controls = controls).text(text)


def source(src:str | None = None, type:str | None = None) -> Element:
    return Element("source").attr(src = src, type = type)


def track(default:Literal["true", "false"] | str | None = None, kind:Literal["subtitles", "captions", "descriptions", "chapters", "metadata"] | str | None = None, label:str | None = None, src:str | None = None, srclang:str | None = None) -> Element:
    return Element("track").attr(default = default, kind = kind, label = label, src = src, srclang = srclang)


def map(text:str | None = None, name:str | None = None) -> Element:
    return Element("map").attr(name = name).text(text)


def area(alt:str | None = None, coords:str | None = None, shape:Literal["circle", "default", "poly", "rect"] | str | None = None, href:str | None = None, target:Literal["_self", "_blank", "_parent", "_top"] | str | None = None, download:str | None = None, ping:str | None = None, rel:str | None = None, hreflang:str | None = None, type:str | None = None) -> Element:
    return Element("area").attr(alt = alt, coords = coords, shape = shape, href = href, target = target, download = download, ping = ping, rel = rel, hreflang = hreflang, type = type)


def table(text:str | None = None, border:str | None = None) -> Element:
    return Element("table").attr(border = border).text(text)


def caption(text:str | None = None) -> Element:
    return Element("caption").attr().text(text)


def colgroup(text:str | None = None, span:str | None = None) -> Element:
    return Element("colgroup").attr(span = span).text(text)


def col(span:str | None = None) -> Element:
    return Element("col").attr(span = span)


def tbody(text:str | None = None) -> Element:
    return Element("tbody").attr().text(text)


def thead(text:str | None = None) -> Element:
    return Element("thead").attr().text(text)


def tfoot(text:str | None = None) -> Element:
    return Element("tfoot").attr().text(text)


def tr(text:str | None = None) -> Element:
    return Element("tr").attr().text(text)


def td(text:str | None = None, colspan:str | None = None, rowspan:str | None = None, headers:str | None = None) -> Element:
    return Element("td").attr(colspan = colspan, rowspan = rowspan, headers = headers).text(text)


def th(text:str | None = None, colspan:str | None = None, rowspan:str | None = None, headers:str | None = None, scope:Literal["row", "col", "rowgroup", "colgroup"] | str | None = None, sorted:str | None = None, abbr:str | None = None) -> Element:
    return Element("th").attr(colspan = colspan, rowspan = rowspan, headers = headers, scope = scope, sorted = sorted, abbr = abbr).text(text)


def form(text:str | None = None, accept_charset:str | None = None, action:str | None = None, autocomplete:Literal["on", "off"] | str | None = None, enctype:Literal["application/x-www-form-urlencoded", "multipart/form-data", "text/plain"] | str | None = None, method:Literal["get", "post", "dialog"] | str | None = None, name:str | None = None, novalidate:Literal["true", "false"] | str | None = None, target:Literal["_self", "_blank", "_parent", "_top"] | str | None = None) -> Element:
    return Element("form").attr(accept_charset = accept_charset, action = action, autocomplete = autocomplete, enctype = enctype, method = method, name = name, novalidate = novalidate, target = target).text(text)


def label(text:str | None = None, form:str | None = None, for_:str | None = None) -> Element:
    return Element("label").attr(form = form, for_ = for_).text(text)


def input(accept:str | None = None, alt:str | None = None, autocomplete:Literal["additional-name", "address-level1", "address-level2", "address-level3", "address-level4", "address-line1", "address-line2", "address-line3", "bday", "bday-year", "bday-day", "bday-month", "billing", "cc-additional-name", "cc-csc", "cc-exp", "cc-exp-month", "cc-exp-year", "cc-family-name", "cc-given-name", "cc-name", "cc-number", "cc-type", "country", "country-name", "current-password", "email", "family-name", "fax", "given-name", "home", "honorific-prefix", "honorific-suffix", "impp", "language", "mobile", "name", "new-password", "nickname", "off", "on", "organization", "organization-title", "pager", "photo", "postal-code", "sex", "shipping", "street-address", "tel-area-code", "tel", "tel-country-code", "tel-extension", "tel-local", "tel-local-prefix", "tel-local-suffix", "tel-national", "transaction-amount", "transaction-currency", "url", "username", "work"] | str | None = None, autofocus:Literal["true", "false"] | str | None = None, checked:Literal["true", "false"] | str | None = None, dirname:str | None = None, disabled:Literal["true", "false"] | str | None = None, form:str | None = None, formaction:str | None = None, formenctype:Literal["application/x-www-form-urlencoded", "multipart/form-data", "text/plain"] | str | None = None, formmethod:Literal["get", "post"] | str | None = None, formnovalidate:Literal["true", "false"] | str | None = None, formtarget:str | None = None, height:str | None = None, inputmode:Literal["verbatim", "latin", "latin-name", "latin-prose", "full-width-latin", "kana", "kana-name", "katakana", "numeric", "tel", "email", "url"] | str | None = None, list:str | None = None, max:str | None = None, maxlength:str | None = None, min:str | None = None, minlength:str | None = None, multiple:Literal["true", "false"] | str | None = None, name:str | None = None, pattern:str | None = None, placeholder:str | None = None, popovertarget:str | None = None, popovertargetaction:str | None = None, readonly:Literal["true", "false"] | str | None = None, required:Literal["true", "false"] | str | None = None, size:str | None = None, src:str | None = None, step:str | None = None, type:Literal["hidden", "text", "search", "tel", "url", "email", "password", "datetime", "date", "month", "week", "time", "datetime-local", "number", "range", "color", "checkbox", "radio", "file", "submit", "image", "reset", "button"] | str | None = None, value:str | None = None, width:str | None = None) -> Element:
    return Element("input").attr(accept = accept, alt = alt, autocomplete = autocomplete, autofocus = autofocus, checked = checked, dirname = dirname, disabled = disabled, form = form, formaction = formaction, formenctype = formenctype, formmethod = formmethod, formnovalidate = formnovalidate, formtarget = formtarget, height = height, inputmode = inputmode, list = list, max = max, maxlength = maxlength, min = min, minlength = minlength, multiple = multiple, name = name, pattern = pattern, placeholder = placeholder, popovertarget = popovertarget, popovertargetaction = popovertargetaction, readonly = readonly, required = required, size = size, src = src, step = step, type = type, value = value, width = width)


def button(text:str | None = None, autofocus:Literal["true", "false"] | str | None = None, disabled:Literal["true", "false"] | str | None = None, form:str | None = None, formaction:str | None = None, formenctype:Literal["application/x-www-form-urlencoded", "multipart/form-data", "text/plain"] | str | None = None, formmethod:Literal["get", "post"] | str | None = None, formnovalidate:Literal["true", "false"] | str | None = None, formtarget:str | None = None, name:str | None = None, popovertarget:str | None = None, popovertargetaction:str | None = None, type:Literal["button", "submit", "reset"] | str | None = None, value:str | None = None) -> Element:
    return Element("button").attr(autofocus = autofocus, disabled = disabled, form = form, formaction = formaction, formenctype = formenctype, formmethod = formmethod, formnovalidate = formnovalidate, formtarget = formtarget, name = name, popovertarget = popovertarget, popovertargetaction = popovertargetaction, type = type, value = value).text(text)


def select(text:str | None = None, autocomplete:Literal["additional-name", "address-level1", "address-level2", "address-level3", "address-level4", "address-line1", "address-line2", "address-line3", "bday", "bday-year", "bday-day", "bday-month", "billing", "cc-additional-name", "cc-csc", "cc-exp", "cc-exp-month", "cc-exp-year", "cc-family-name", "cc-given-name", "cc-name", "cc-number", "cc-type", "country", "country-name", "current-password", "email", "family-name", "fax", "given-name", "home", "honorific-prefix", "honorific-suffix", "impp", "language", "mobile", "name", "new-password", "nickname", "off", "on", "organization", "organization-title", "pager", "photo", "postal-code", "sex", "shipping", "street-address", "tel-area-code", "tel", "tel-country-code", "tel-extension", "tel-local", "tel-local-prefix", "tel-local-suffix", "tel-national", "transaction-amount", "transaction-currency", "url", "username", "work"] | str | None = None, autofocus:Literal["true", "false"] | str | None = None, disabled:Literal["true", "false"] | str | None = None, form:str | None = None, multiple:Literal["true", "false"] | str | None = None, name:str | None = None, required:Literal["true", "false"] | str | None = None, size:str | None = None) -> Element:
    return Element("select").attr(autocomplete = autocomplete, autofocus = autofocus, disabled = disabled, form = form, multiple = multiple, name = name, required = required, size = size).text(text)


def datalist(text:str | None = None) -> Element:
    return Element("datalist").attr().text(text)


def optgroup(text:str | None = None, disabled:Literal["true", "false"] | str | None = None, label:str | None = None) -> Element:
    return Element("optgroup").attr(disabled = disabled, label = label).text(text)


def option(text:str | None = None, disabled:Literal["true", "false"] | str | None = None, label:str | None = None, selected:Literal["true", "false"] | str | None = None, value:str | None = None) -> Element:
    return Element("option").attr(disabled = disabled, label = label, selected = selected, value = value).text(text)


def textarea(text:str | None = None, autocomplete:Literal["additional-name", "address-level1", "address-level2", "address-level3", "address-level4", "address-line1", "address-line2", "address-line3", "bday", "bday-year", "bday-day", "bday-month", "billing", "cc-additional-name", "cc-csc", "cc-exp", "cc-exp-month", "cc-exp-year", "cc-family-name", "cc-given-name", "cc-name", "cc-number", "cc-type", "country", "country-name", "current-password", "email", "family-name", "fax", "given-name", "home", "honorific-prefix", "honorific-suffix", "impp", "language", "mobile", "name", "new-password", "nickname", "off", "on", "organization", "organization-title", "pager", "photo", "postal-code", "sex", "shipping", "street-address", "tel-area-code", "tel", "tel-country-code", "tel-extension", "tel-local", "tel-local-prefix", "tel-local-suffix", "tel-national", "transaction-amount", "transaction-currency", "url", "username", "work"] | str | None = None, autofocus:Literal["true", "false"] | str | None = None, cols:str | None = None, dirname:str | None = None, disabled:Literal["true", "false"] | str | None = None, form:str | None = None, inputmode:Literal["verbatim", "latin", "latin-name", "latin-prose", "full-width-latin", "kana", "kana-name", "katakana", "numeric", "tel", "email", "url"] | str | None = None, maxlength:str | None = None, minlength:str | None = None, name:str | None = None, placeholder:str | None = None, readonly:Literal["true", "false"] | str | None = None, required:Literal["true", "false"] | str | None = None, rows:str | None = None, wrap:Literal["soft", "hard"] | str | None = None) -> Element:
    return Element("textarea").attr(autocomplete = autocomplete, autofocus = autofocus, cols = cols, dirname = dirname, disabled = disabled, form = form, inputmode = inputmode, maxlength = maxlength, minlength = minlength, name = name, placeholder = placeholder, readonly = readonly, required = required, rows = rows, wrap = wrap).text(text)


def output(text:str | None = None, for_:str | None = None, form:str | None = None, name:str | None = None) -> Element:
    return Element("output").attr(for_ = for_, form = form, name = name).text(text)


def progress(text:str | None = None, value:str | None = None, max:str | None = None) -> Element:
    return Element("progress").attr(value = value, max = max).text(text)


def meter(text:str | None = None, value:str | None = None, min:str | None = None, max:str | None = None, low:str | None = None, high:str | None = None, optimum:str | None = None) -> Element:
    return Element("meter").attr(value = value, min = min, max = max, low = low, high = high, optimum = optimum).text(text)


def fieldset(text:str | None = None, disabled:Literal["true", "false"] | str | None = None, form:str | None = None, name:str | None = None) -> Element:
    return Element("fieldset").attr(disabled = disabled, form = form, name = name).text(text)


def legend(text:str | None = None) -> Element:
    return Element("legend").attr().text(text)


def details(text:str | None = None, open:Literal["true", "false"] | str | None = None, name:str | None = None) -> Element:
    return Element("details").attr(open = open, name = name).text(text)


def summary(text:str | None = None) -> Element:
    return Element("summary").attr().text(text)


def dialog(text:str | None = None) -> Element:
    return Element("dialog").attr().text(text)


def script(text:str | None = None, src:str | None = None, type:str | None = None, charset:str | None = None, async_:Literal["true", "false"] | str | None = None, defer:Literal["true", "false"] | str | None = None, crossorigin:Literal["anonymous", "use-credentials"] | str | None = None, nonce:str | None = None) -> Element:
    return Element("script").attr(src = src, type = type, charset = charset, async_ = async_, defer = defer, crossorigin = crossorigin, nonce = nonce).text(text)


def noscript(text:str | None = None) -> Element:
    return Element("noscript").attr().text(text)


def template(text:str | None = None) -> Element:
    return Element("template").attr().text(text)


def canvas(text:str | None = None, width:str | None = None, height:str | None = None) -> Element:
    return Element("canvas").attr(width = width, height = height).text(text)


def slot(text:str | None = None, name:str | None = None) -> Element:
    return Element("slot").attr(name = name).text(text)


def data(text:str | None = None, value:str | None = None) -> Element:
    return Element("data").attr(value = value).text(text)


def hgroup(text:str | None = None) -> Element:
    return Element("hgroup").attr().text(text)


def menu(text:str | None = None) -> Element:
    return Element("menu").attr().text(text)


def search(text:str | None = None) -> Element:
    return Element("search").attr().text(text)


def fencedframe(text:str | None = None, allow:str | None = None, height:str | None = None, width:str | None = None) -> Element:
    return Element("fencedframe").attr(allow = allow, height = height, width = width).text(text)


def selectedcontent(text:str | None = None) -> Element:
    return Element("selectedcontent").attr().text(text)