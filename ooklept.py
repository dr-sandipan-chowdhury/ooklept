import argparse
import hashlib
import hmac
import html
import keyword
import os
import re
import runpy
import secrets
import uuid
from collections.abc import Iterator, MutableMapping
from contextvars import ContextVar, Token
from pathlib import Path
from typing import Literal, TypedDict, Unpack, get_args
from warnings import warn

import anyio
import uvicorn
from diskcache import Cache
from fastapi import FastAPI, HTTPException
from fastapi.requests import Request
from fastapi.responses import FileResponse, HTMLResponse

# WebTypes
HTMLTag = Literal[
    "html",
    "head",
    "title",
    "base",
    "link",
    "meta",
    "style",
    "body",
    "article",
    "section",
    "nav",
    "aside",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "header",
    "footer",
    "address",
    "p",
    "hr",
    "pre",
    "blockquote",
    "ol",
    "ul",
    "li",
    "dl",
    "dt",
    "dd",
    "figure",
    "figcaption",
    "main",
    "div",
    "a",
    "em",
    "strong",
    "small",
    "s",
    "cite",
    "q",
    "dfn",
    "abbr",
    "ruby",
    "rb",
    "rt",
    "rp",
    "time",
    "code",
    "var",
    "samp",
    "kbd",
    "sub",
    "sup",
    "i",
    "b",
    "u",
    "mark",
    "bdi",
    "bdo",
    "span",
    "br",
    "wbr",
    "ins",
    "del",
    "picture",
    "img",
    "iframe",
    "embed",
    "object",
    "param",
    "video",
    "audio",
    "source",
    "track",
    "map",
    "area",
    "table",
    "caption",
    "colgroup",
    "col",
    "tbody",
    "thead",
    "tfoot",
    "tr",
    "td",
    "th",
    "form",
    "label",
    "input",
    "button",
    "select",
    "datalist",
    "optgroup",
    "option",
    "textarea",
    "output",
    "progress",
    "meter",
    "fieldset",
    "legend",
    "details",
    "summary",
    "dialog",
    "script",
    "noscript",
    "template",
    "canvas",
    "slot",
    "data",
    "hgroup",
    "menu",
    "search",
    "fencedframe",
    "selectedcontent",
]


HTMLVoidTag = Literal[
    "base",
    "link",
    "meta",
    "hr",
    "br",
    "wbr",
    "img",
    "embed",
    "param",
    "source",
    "track",
    "area",
    "col",
    "input",
]


class HTMLAttribute(TypedDict, total=False):
    manifest: str | None
    href: str | None
    target: (
        Literal[
            "_blank",
            "_parent",
            "_self",
            "_top",
        ]
        | str
        | None
    )
    crossorigin: (
        Literal[
            "anonymous",
            "use-credentials",
        ]
        | str
        | None
    )
    rel: str | None
    media: str | None
    hreflang: str | None
    type: (
        Literal[
            "1",
            "A",
            "I",
            "a",
            "button",
            "checkbox",
            "color",
            "date",
            "datetime",
            "datetime-local",
            "email",
            "file",
            "hidden",
            "i",
            "image",
            "month",
            "number",
            "password",
            "radio",
            "range",
            "reset",
            "search",
            "submit",
            "tel",
            "text",
            "time",
            "url",
            "week",
        ]
        | str
        | None
    )
    sizes: str | None
    name: str | None
    http_equiv: str | None
    content: str | None
    charset: str | None
    nonce: str | None
    scoped: (
        Literal[
            "false",
            "true",
        ]
        | bool
        | str
        | None
    )
    onafterprint: str | None
    onbeforeprint: str | None
    onbeforeunload: str | None
    onhashchange: str | None
    onlanguagechange: str | None
    onmessage: str | None
    onoffline: str | None
    ononline: str | None
    onpagehide: str | None
    onpageshow: str | None
    onpopstate: str | None
    onstorage: str | None
    onunload: str | None
    cite: str | None
    reversed: (
        Literal[
            "false",
            "true",
        ]
        | bool
        | str
        | None
    )
    start: str | None
    value: str | None
    download: str | None
    ping: str | None
    datetime: str | None
    alt: str | None
    src: str | None
    srcset: str | None
    usemap: str | None
    ismap: (
        Literal[
            "false",
            "true",
        ]
        | bool
        | str
        | None
    )
    width: str | None
    height: str | None
    decoding: (
        Literal[
            "async",
            "auto",
            "sync",
        ]
        | str
        | None
    )
    loading: (
        Literal[
            "eager",
            "lazy",
        ]
        | str
        | None
    )
    fetchpriority: (
        Literal[
            "auto",
            "high",
            "low",
        ]
        | str
        | None
    )
    referrerpolicy: (
        Literal[
            "no-referrer",
            "no-referrer-when-downgrade",
            "origin",
            "origin-when-cross-origin",
            "same-origin",
            "strict-origin",
            "strict-origin-when-cross-origin",
            "unsafe-url",
        ]
        | str
        | None
    )
    srcdoc: str | None
    sandbox: (
        Literal[
            "allow-forms",
            "allow-modals",
            "allow-pointer-lock",
            "allow-popups",
            "allow-popups-to-escape-sandbox",
            "allow-same-origin",
            "allow-scripts",
            "allow-top-navigation",
        ]
        | str
        | None
    )
    seamless: (
        Literal[
            "false",
            "true",
        ]
        | bool
        | str
        | None
    )
    allowfullscreen: (
        Literal[
            "false",
            "true",
        ]
        | bool
        | str
        | None
    )
    data: str | None
    typemustmatch: (
        Literal[
            "false",
            "true",
        ]
        | bool
        | str
        | None
    )
    form: str | None
    poster: str | None
    preload: (
        Literal[
            "auto",
            "metadata",
            "none",
        ]
        | str
        | None
    )
    autoplay: (
        Literal[
            "false",
            "true",
        ]
        | bool
        | str
        | None
    )
    mediagroup: str | None
    loop: (
        Literal[
            "false",
            "true",
        ]
        | bool
        | str
        | None
    )
    muted: (
        Literal[
            "false",
            "true",
        ]
        | bool
        | str
        | None
    )
    controls: (
        Literal[
            "false",
            "true",
        ]
        | bool
        | str
        | None
    )
    default: (
        Literal[
            "false",
            "true",
        ]
        | bool
        | str
        | None
    )
    kind: (
        Literal[
            "captions",
            "chapters",
            "descriptions",
            "metadata",
            "subtitles",
        ]
        | str
        | None
    )
    label: str | None
    srclang: str | None
    coords: str | None
    shape: (
        Literal[
            "circle",
            "default",
            "poly",
            "rect",
        ]
        | str
        | None
    )
    border: str | None
    span: str | None
    colspan: str | None
    rowspan: str | None
    headers: str | None
    scope: (
        Literal[
            "col",
            "colgroup",
            "row",
            "rowgroup",
        ]
        | str
        | None
    )
    sorted: str | None
    abbr: str | None
    accept_charset: str | None
    action: str | None
    autocomplete: (
        Literal[
            "additional-name",
            "address-level1",
            "address-level2",
            "address-level3",
            "address-level4",
            "address-line1",
            "address-line2",
            "address-line3",
            "bday",
            "bday-day",
            "bday-month",
            "bday-year",
            "billing",
            "cc-additional-name",
            "cc-csc",
            "cc-exp",
            "cc-exp-month",
            "cc-exp-year",
            "cc-family-name",
            "cc-given-name",
            "cc-name",
            "cc-number",
            "cc-type",
            "country",
            "country-name",
            "current-password",
            "email",
            "family-name",
            "fax",
            "given-name",
            "home",
            "honorific-prefix",
            "honorific-suffix",
            "impp",
            "language",
            "mobile",
            "name",
            "new-password",
            "nickname",
            "off",
            "on",
            "organization",
            "organization-title",
            "pager",
            "photo",
            "postal-code",
            "sex",
            "shipping",
            "street-address",
            "tel",
            "tel-area-code",
            "tel-country-code",
            "tel-extension",
            "tel-local",
            "tel-local-prefix",
            "tel-local-suffix",
            "tel-national",
            "transaction-amount",
            "transaction-currency",
            "url",
            "username",
            "work",
        ]
        | str
        | None
    )
    enctype: (
        Literal[
            "application/x-www-form-urlencoded",
            "multipart/form-data",
            "text/plain",
        ]
        | str
        | None
    )
    method: (
        Literal[
            "dialog",
            "get",
            "post",
        ]
        | str
        | None
    )
    novalidate: (
        Literal[
            "false",
            "true",
        ]
        | bool
        | str
        | None
    )
    for_: str | None
    accept: str | None
    autofocus: (
        Literal[
            "false",
            "true",
        ]
        | bool
        | str
        | None
    )
    checked: (
        Literal[
            "false",
            "true",
        ]
        | bool
        | str
        | None
    )
    dirname: str | None
    disabled: (
        Literal[
            "false",
            "true",
        ]
        | bool
        | str
        | None
    )
    formaction: str | None
    formenctype: (
        Literal[
            "application/x-www-form-urlencoded",
            "multipart/form-data",
            "text/plain",
        ]
        | str
        | None
    )
    formmethod: (
        Literal[
            "get",
            "post",
        ]
        | str
        | None
    )
    formnovalidate: (
        Literal[
            "false",
            "true",
        ]
        | bool
        | str
        | None
    )
    formtarget: str | None
    inputmode: (
        Literal[
            "email",
            "full-width-latin",
            "kana",
            "kana-name",
            "katakana",
            "latin",
            "latin-name",
            "latin-prose",
            "numeric",
            "tel",
            "url",
            "verbatim",
        ]
        | str
        | None
    )
    list: str | None
    max: str | None
    maxlength: str | None
    min: str | None
    minlength: str | None
    multiple: (
        Literal[
            "false",
            "true",
        ]
        | bool
        | str
        | None
    )
    pattern: str | None
    placeholder: str | None
    popovertarget: str | None
    popovertargetaction: str | None
    readonly: (
        Literal[
            "false",
            "true",
        ]
        | bool
        | str
        | None
    )
    required: (
        Literal[
            "false",
            "true",
        ]
        | bool
        | str
        | None
    )
    size: str | None
    step: str | None
    selected: (
        Literal[
            "false",
            "true",
        ]
        | bool
        | str
        | None
    )
    cols: str | None
    rows: str | None
    wrap: (
        Literal[
            "hard",
            "soft",
        ]
        | str
        | None
    )
    low: str | None
    high: str | None
    optimum: str | None
    open: (
        Literal[
            "false",
            "true",
        ]
        | bool
        | str
        | None
    )
    async_: (
        Literal[
            "false",
            "true",
        ]
        | bool
        | str
        | None
    )
    defer: (
        Literal[
            "false",
            "true",
        ]
        | bool
        | str
        | None
    )
    allow: str | None
    accesskey: str | None
    autocapitalize: str | None
    autocorrect: (
        Literal[
            "off",
            "on",
        ]
        | str
        | None
    )
    class_: str | None
    contenteditable: str | None
    contextmenu: str | None
    dir: (
        Literal[
            "auto",
            "ltr",
            "rtl",
        ]
        | str
        | None
    )
    draggable: (
        Literal[
            "false",
            "true",
        ]
        | bool
        | str
        | None
    )
    dropzone: str | None
    enterkeyhint: (
        Literal[
            "done",
            "enter",
            "go",
            "next",
            "previous",
            "search",
            "send",
        ]
        | str
        | None
    )
    exportparts: str | None
    hidden: (
        Literal[
            "false",
            "true",
        ]
        | bool
        | str
        | None
    )
    id: str | None
    inert: str | None
    is_: str | None
    itemid: str | None
    itemprop: str | None
    itemref: str | None
    itemscope: (
        Literal[
            "false",
            "true",
        ]
        | bool
        | str
        | None
    )
    itemtype: str | None
    lang: str | None
    part: str | None
    popover: (
        Literal[
            "auto",
            "hint",
            "manual",
        ]
        | str
        | None
    )
    role: (
        Literal[
            "alert",
            "alertdialog",
            "application",
            "article",
            "banner",
            "button",
            "cell",
            "checkbox",
            "columnheader",
            "combobox",
            "complementary",
            "contentinfo",
            "definition",
            "dialog",
            "directory",
            "doc-abstract",
            "doc-acknowledgments",
            "doc-afterword",
            "doc-appendix",
            "doc-backlink",
            "doc-biblioentry",
            "doc-bibliography",
            "doc-biblioref",
            "doc-chapter",
            "doc-colophon",
            "doc-conclusion",
            "doc-cover",
            "doc-credit",
            "doc-credits",
            "doc-dedication",
            "doc-endnote",
            "doc-endnotes",
            "doc-epigraph",
            "doc-epilogue",
            "doc-errata",
            "doc-example",
            "doc-footnote",
            "doc-foreword",
            "doc-glossary",
            "doc-glossref",
            "doc-index",
            "doc-introduction",
            "doc-noteref",
            "doc-notice",
            "doc-pagebreak",
            "doc-pagelist",
            "doc-part",
            "doc-preface",
            "doc-prologue",
            "doc-pullquote",
            "doc-qna",
            "doc-subtitle",
            "doc-tip",
            "doc-toc",
            "document",
            "feed",
            "figure",
            "form",
            "grid",
            "gridcell",
            "group",
            "heading",
            "img",
            "link",
            "list",
            "listbox",
            "listitem",
            "log",
            "main",
            "marquee",
            "math",
            "menu",
            "menubar",
            "menuitem",
            "menuitemcheckbox",
            "menuitemradio",
            "navigation",
            "none",
            "note",
            "option",
            "presentation",
            "progressbar",
            "radio",
            "radiogroup",
            "region",
            "row",
            "rowgroup",
            "rowheader",
            "scrollbar",
            "search",
            "searchbox",
            "separator",
            "slider",
            "spinbutton",
            "status",
            "switch",
            "tab",
            "table",
            "tablist",
            "tabpanel",
            "term",
            "text",
            "textbox",
            "timer",
            "toolbar",
            "tooltip",
            "tree",
            "treegrid",
            "treeitem",
        ]
        | str
        | None
    )
    slot: str | None
    spellcheck: (
        Literal[
            "false",
            "true",
        ]
        | bool
        | str
        | None
    )
    style: str | None
    tabindex: str | None
    title: str | None
    translate: (
        Literal[
            "no",
            "yes",
        ]
        | str
        | None
    )
    virtualkeyboardpolicy: (
        Literal[
            "false",
            "true",
        ]
        | bool
        | str
        | None
    )
    onabort: str | None
    onanimationend: str | None
    onanimationiteration: str | None
    onanimationstart: str | None
    onappinstalled: str | None
    onaudioprocess: str | None
    onaudioend: str | None
    onaudiostart: str | None
    onbeginEvent: str | None
    onblocked: str | None
    onblur: str | None
    onboundary: str | None
    oncached: str | None
    oncanplay: str | None
    oncanplaythrough: str | None
    onchange: str | None
    onchargingchange: str | None
    onchargingtimechange: str | None
    onchecking: str | None
    onclick: str | None
    onclose: str | None
    oncomplete: str | None
    oncompositionend: str | None
    oncompositionstart: str | None
    oncompositionupdate: str | None
    oncontextmenu: str | None
    oncopy: str | None
    oncut: str | None
    ondblclick: str | None
    ondevicechange: str | None
    ondevicelight: str | None
    ondevicemotion: str | None
    ondeviceorientation: str | None
    ondeviceproximity: str | None
    ondischargingtimechange: str | None
    onDOMActivate: str | None
    onDOMAttributeNameChanged: str | None
    onDOMAttrModified: str | None
    onDOMCharacterDataModified: str | None
    onDOMContentLoaded: str | None
    onDOMElementNameChanged: str | None
    onDOMFocusIn: str | None
    onDOMFocusOut: str | None
    onDOMNodeInserted: str | None
    onDOMNodeInsertedIntoDocument: str | None
    onDOMNodeRemoved: str | None
    onDOMNodeRemovedFromDocument: str | None
    onDOMSubtreeModified: str | None
    ondownloading: str | None
    ondrag: str | None
    ondragend: str | None
    ondragenter: str | None
    ondragleave: str | None
    ondragover: str | None
    ondragstart: str | None
    ondrop: str | None
    ondurationchange: str | None
    onemptied: str | None
    onend: str | None
    onended: str | None
    onendEvent: str | None
    onerror: str | None
    onfocus: str | None
    onfocusin: str | None
    onfocusout: str | None
    onfullscreenchange: str | None
    onfullscreenerror: str | None
    ongamepadconnected: str | None
    ongamepaddisconnected: str | None
    ongotpointercapture: str | None
    onlostpointercapture: str | None
    oninput: str | None
    oninvalid: str | None
    onkeydown: str | None
    onkeypress: str | None
    onkeyup: str | None
    onlevelchange: str | None
    onload: str | None
    onloadeddata: str | None
    onloadedmetadata: str | None
    onloadend: str | None
    onloadstart: str | None
    onmark: str | None
    onmessageerror: str | None
    onmousedown: str | None
    onmouseenter: str | None
    onmouseleave: str | None
    onmousemove: str | None
    onmouseout: str | None
    onmouseover: str | None
    onmouseup: str | None
    onnomatch: str | None
    onnotificationclick: str | None
    onnoupdate: str | None
    onobsolete: str | None
    onopen: str | None
    onorientationchange: str | None
    onpaste: str | None
    onpause: str | None
    onpointercancel: str | None
    onpointerdown: str | None
    onpointerenter: str | None
    onpointerleave: str | None
    onpointerlockchange: str | None
    onpointerlockerror: str | None
    onpointermove: str | None
    onpointerout: str | None
    onpointerover: str | None
    onpointerup: str | None
    onplay: str | None
    onplaying: str | None
    onprogress: str | None
    onpush: str | None
    onpushsubscriptionchange: str | None
    onratechange: str | None
    onreadystatechange: str | None
    onrepeatEvent: str | None
    onreset: str | None
    onresize: str | None
    onresourcetimingbufferfull: str | None
    onresult: str | None
    onresume: str | None
    onscroll: str | None
    onseeked: str | None
    onseeking: str | None
    onselect: str | None
    onselectstart: str | None
    onselectionchange: str | None
    onshow: str | None
    onslotchange: str | None
    onsoundend: str | None
    onsoundstart: str | None
    onspeechend: str | None
    onspeechstart: str | None
    onstalled: str | None
    onstart: str | None
    onsubmit: str | None
    onsuccess: str | None
    onsuspend: str | None
    onSVGAbort: str | None
    onSVGError: str | None
    onSVGLoad: str | None
    onSVGResize: str | None
    onSVGScroll: str | None
    onSVGUnload: str | None
    onSVGZoom: str | None
    ontimeout: str | None
    ontimeupdate: str | None
    ontouchcancel: str | None
    ontouchend: str | None
    ontouchmove: str | None
    ontouchstart: str | None
    ontransitionend: str | None
    onupdateready: str | None
    onupgradeneeded: str | None
    onuserproximity: str | None
    onvoiceschanged: str | None
    onversionchange: str | None
    onvisibilitychange: str | None
    onvolumechange: str | None
    onwaiting: str | None
    onwheel: str | None
    onforminput: str | None
    onformchange: str | None
    onmousewheel: str | None


class CSSProperty(TypedDict, total=False):
    _moz_animation: (
        Literal[
            "time, enum, timing-function, identifier, number",
            "alternate",
            "alternate-reverse",
            "backwards",
            "both",
            "forwards",
            "infinite",
            "none",
            "normal",
            "reverse",
        ]
        | str
        | None
    )
    _moz_animation_delay: Literal["time",] | str | None
    _moz_animation_direction: (
        Literal[
            "enum",
            "alternate",
            "alternate-reverse",
            "normal",
            "reverse",
        ]
        | str
        | None
    )
    _moz_animation_duration: Literal["time",] | str | None
    _moz_animation_iteration_count: Literal["number, enum",] | str | None
    _moz_animation_name: Literal["identifier, enum",] | str | None
    _moz_animation_play_state: (
        Literal[
            "enum",
            "paused",
            "running",
        ]
        | str
        | None
    )
    _moz_animation_timing_function: Literal["timing-function",] | str | None
    _moz_appearance: (
        Literal[
            "enum",
            "button",
            "button-arrow-down",
            "button-arrow-next",
            "button-arrow-previous",
            "button-arrow-up",
            "button-bevel",
            "checkbox",
            "checkbox-container",
            "checkbox-label",
            "dialog",
            "groupbox",
            "listbox",
            "menuarrow",
            "menuimage",
            "menuitem",
            "menuitemtext",
            "menulist",
            "menulist-button",
            "menulist-text",
            "menulist-textfield",
            "menupopup",
            "menuradio",
            "menuseparator",
            "-moz-mac-unified-toolbar",
            "-moz-win-borderless-glass",
            "-moz-win-browsertabbar-toolbox",
            "-moz-win-communications-toolbox",
            "-moz-win-glass",
            "-moz-win-media-toolbox",
            "none",
            "progressbar",
            "progresschunk",
            "radio",
            "radio-container",
            "radio-label",
            "radiomenuitem",
            "resizer",
            "resizerpanel",
            "scrollbarbutton-down",
            "scrollbarbutton-left",
            "scrollbarbutton-right",
            "scrollbarbutton-up",
            "scrollbar-small",
            "scrollbartrack-horizontal",
            "scrollbartrack-vertical",
            "separator",
            "spinner",
            "spinner-downbutton",
            "spinner-textfield",
            "spinner-upbutton",
            "statusbar",
            "statusbarpanel",
            "tab",
            "tabpanels",
            "tab-scroll-arrow-back",
            "tab-scroll-arrow-forward",
            "textfield",
            "textfield-multiline",
            "toolbar",
            "toolbox",
            "tooltip",
            "treeheadercell",
            "treeheadersortarrow",
            "treeitem",
            "treetwistyopen",
            "treeview",
            "treewisty",
            "window",
        ]
        | str
        | None
    )
    _moz_backface_visibility: (
        Literal[
            "enum",
            "hidden",
            "visible",
        ]
        | str
        | None
    )
    _moz_background_clip: Literal["box, enum",] | str | None
    _moz_background_inline_policy: (
        Literal[
            "enum",
            "bounding-box",
            "continuous",
            "each-box",
        ]
        | str
        | None
    )
    _moz_background_origin: Literal["box",] | str | None
    _moz_border_bottom_colors: Literal["color",] | str | None
    _moz_border_image: (
        Literal[
            "length, percentage, number, url, enum",
            "auto",
            "fill",
            "none",
            "repeat",
            "round",
            "space",
            "stretch",
            "url()",
        ]
        | str
        | None
    )
    _moz_border_left_colors: Literal["color",] | str | None
    _moz_border_right_colors: Literal["color",] | str | None
    _moz_border_top_colors: Literal["color",] | str | None
    _moz_box_align: (
        Literal[
            "enum",
            "baseline",
            "center",
            "end",
            "start",
            "stretch",
        ]
        | str
        | None
    )
    _moz_box_direction: (
        Literal[
            "enum",
            "normal",
            "reverse",
        ]
        | str
        | None
    )
    _moz_box_flex: Literal["number",] | str | None
    _moz_box_flexgroup: Literal["integer",] | str | None
    _moz_box_ordinal_group: Literal["integer",] | str | None
    _moz_box_orient: (
        Literal[
            "enum",
            "block-axis",
            "horizontal",
            "inline-axis",
            "vertical",
        ]
        | str
        | None
    )
    _moz_box_pack: (
        Literal[
            "enum",
            "center",
            "end",
            "justify",
            "start",
        ]
        | str
        | None
    )
    _moz_box_sizing: (
        Literal[
            "enum",
            "border-box",
            "content-box",
            "padding-box",
        ]
        | str
        | None
    )
    _moz_column_count: Literal["integer",] | str | None
    _moz_column_gap: Literal["length",] | str | None
    _moz_column_rule: Literal["length, line-width, line-style, color",] | str | None
    _moz_column_rule_color: Literal["color",] | str | None
    _moz_column_rule_style: Literal["line-style",] | str | None
    _moz_column_rule_width: Literal["length, line-width",] | str | None
    _moz_column_width: Literal["length",] | str | None
    _moz_columns: Literal["length, integer",] | str | None
    _moz_font_feature_settings: Literal["string, integer",] | str | None
    _moz_hyphens: (
        Literal[
            "enum",
            "auto",
            "manual",
            "none",
        ]
        | str
        | None
    )
    _moz_perspective: Literal["length",] | str | None
    _moz_perspective_origin: Literal["position, percentage, length",] | str | None
    _moz_text_align_last: (
        Literal[
            "enum",
            "auto",
            "center",
            "end",
            "justify",
            "left",
            "right",
            "start",
        ]
        | str
        | None
    )
    _moz_text_decoration_color: Literal["color",] | str | None
    _moz_text_decoration_line: (
        Literal[
            "enum",
            "line-through",
            "none",
            "overline",
            "underline",
        ]
        | str
        | None
    )
    _moz_text_decoration_style: (
        Literal[
            "enum",
            "dashed",
            "dotted",
            "double",
            "none",
            "solid",
            "wavy",
        ]
        | str
        | None
    )
    _moz_text_size_adjust: (
        Literal[
            "enum, percentage",
            "auto",
            "none",
        ]
        | str
        | None
    )
    _moz_transform: (
        Literal[
            "enum",
            "matrix()",
            "matrix3d()",
            "none",
            "perspective",
            "rotate()",
            "rotate3d()",
            "rotateX('angle')",
            "rotateY('angle')",
            "rotateZ('angle')",
            "scale()",
            "scale3d()",
            "scaleX()",
            "scaleY()",
            "scaleZ()",
            "skew()",
            "skewX()",
            "skewY()",
            "translate()",
            "translate3d()",
            "translateX()",
            "translateY()",
            "translateZ()",
        ]
        | str
        | None
    )
    _moz_transform_origin: Literal["position, length, percentage",] | str | None
    _moz_transition: (
        Literal[
            "time, property, timing-function, enum",
            "all",
            "none",
        ]
        | str
        | None
    )
    _moz_transition_delay: Literal["time",] | str | None
    _moz_transition_duration: Literal["time",] | str | None
    _moz_transition_property: Literal["property",] | str | None
    _moz_transition_timing_function: Literal["timing-function",] | str | None
    _moz_user_focus: str | None
    _moz_user_select: (
        Literal[
            "enum",
            "all",
            "element",
            "elements",
            "-moz-all",
            "-moz-none",
            "none",
            "text",
            "toggle",
        ]
        | str
        | None
    )
    _ms_accelerator: (
        Literal[
            "enum",
            "false",
            "true",
        ]
        | str
        | None
    )
    _ms_behavior: Literal["url",] | str | None
    _ms_block_progression: (
        Literal[
            "enum",
            "bt",
            "lr",
            "rl",
            "tb",
        ]
        | str
        | None
    )
    _ms_content_zoom_chaining: str | None
    _ms_content_zoom_limit: Literal["percentage",] | str | None
    _ms_content_zoom_limit_max: Literal["percentage",] | str | None
    _ms_content_zoom_limit_min: Literal["percentage",] | str | None
    _ms_content_zoom_snap: str | None
    _ms_content_zoom_snap_points: str | None
    _ms_content_zoom_snap_type: (
        Literal[
            "enum",
            "mandatory",
            "none",
            "proximity",
        ]
        | str
        | None
    )
    _ms_content_zooming: (
        Literal[
            "enum",
            "none",
            "zoom",
        ]
        | str
        | None
    )
    _ms_filter: Literal["string",] | str | None
    _ms_flex: Literal["length, number, percentage",] | str | None
    _ms_flex_align: (
        Literal[
            "enum",
            "baseline",
            "center",
            "end",
            "start",
            "stretch",
        ]
        | str
        | None
    )
    _ms_flex_direction: (
        Literal[
            "enum",
            "column",
            "column-reverse",
            "row",
            "row-reverse",
        ]
        | str
        | None
    )
    _ms_flex_flow: (
        Literal[
            "enum",
            "column",
            "column-reverse",
            "nowrap",
            "row",
            "wrap",
            "wrap-reverse",
        ]
        | str
        | None
    )
    _ms_flex_item_align: (
        Literal[
            "enum",
            "auto",
            "baseline",
            "center",
            "end",
            "start",
            "stretch",
        ]
        | str
        | None
    )
    _ms_flex_line_pack: (
        Literal[
            "enum",
            "center",
            "distribute",
            "end",
            "justify",
            "start",
            "stretch",
        ]
        | str
        | None
    )
    _ms_flex_order: Literal["integer",] | str | None
    _ms_flex_pack: (
        Literal[
            "enum",
            "center",
            "distribute",
            "end",
            "justify",
            "start",
        ]
        | str
        | None
    )
    _ms_flex_wrap: (
        Literal[
            "enum",
            "nowrap",
            "wrap",
            "wrap-reverse",
        ]
        | str
        | None
    )
    _ms_flow_from: Literal["identifier",] | str | None
    _ms_flow_into: Literal["identifier",] | str | None
    _ms_grid_column: (
        Literal[
            "integer, string, enum",
            "auto",
            "end",
            "start",
        ]
        | str
        | None
    )
    _ms_grid_column_align: (
        Literal[
            "enum",
            "center",
            "end",
            "start",
            "stretch",
        ]
        | str
        | None
    )
    _ms_grid_column_span: Literal["integer",] | str | None
    _ms_grid_columns: str | None
    _ms_grid_layer: Literal["integer",] | str | None
    _ms_grid_row: (
        Literal[
            "integer, string, enum",
            "auto",
            "end",
            "start",
        ]
        | str
        | None
    )
    _ms_grid_row_align: (
        Literal[
            "enum",
            "center",
            "end",
            "start",
            "stretch",
        ]
        | str
        | None
    )
    _ms_grid_row_span: Literal["integer",] | str | None
    _ms_grid_rows: str | None
    _ms_high_contrast_adjust: (
        Literal[
            "enum",
            "auto",
            "none",
        ]
        | str
        | None
    )
    _ms_hyphenate_limit_chars: Literal["integer",] | str | None
    _ms_hyphenate_limit_lines: Literal["integer",] | str | None
    _ms_hyphenate_limit_zone: Literal["percentage, length",] | str | None
    _ms_hyphens: (
        Literal[
            "enum",
            "auto",
            "manual",
            "none",
        ]
        | str
        | None
    )
    _ms_ime_mode: (
        Literal[
            "enum",
            "active",
            "auto",
            "disabled",
            "inactive",
            "normal",
        ]
        | str
        | None
    )
    _ms_interpolation_mode: (
        Literal[
            "enum",
            "bicubic",
            "nearest-neighbor",
        ]
        | str
        | None
    )
    _ms_layout_grid: str | None
    _ms_layout_grid_char: (
        Literal[
            "enum, length, percentage",
            "auto",
            "none",
        ]
        | str
        | None
    )
    _ms_layout_grid_line: Literal["length",] | str | None
    _ms_layout_grid_mode: (
        Literal[
            "enum",
            "both",
            "char",
            "line",
            "none",
        ]
        | str
        | None
    )
    _ms_layout_grid_type: (
        Literal[
            "enum",
            "fixed",
            "loose",
            "strict",
        ]
        | str
        | None
    )
    _ms_line_break: (
        Literal[
            "enum",
            "auto",
            "keep-all",
            "newspaper",
            "normal",
            "strict",
        ]
        | str
        | None
    )
    _ms_overflow_style: (
        Literal[
            "enum",
            "auto",
            "-ms-autohiding-scrollbar",
            "none",
            "scrollbar",
        ]
        | str
        | None
    )
    _ms_perspective: Literal["length",] | str | None
    _ms_perspective_origin: Literal["position, percentage, length",] | str | None
    _ms_perspective_origin_x: Literal["position, percentage, length",] | str | None
    _ms_perspective_origin_y: Literal["position, percentage, length",] | str | None
    _ms_progress_appearance: (
        Literal[
            "enum",
            "bar",
            "ring",
        ]
        | str
        | None
    )
    _ms_scroll_chaining: (
        Literal[
            "enum, length",
            "chained",
            "none",
        ]
        | str
        | None
    )
    _ms_scroll_limit: Literal["length",] | str | None
    _ms_scroll_limit_x_max: Literal["length",] | str | None
    _ms_scroll_limit_x_min: Literal["length",] | str | None
    _ms_scroll_limit_y_max: Literal["length",] | str | None
    _ms_scroll_limit_y_min: Literal["length",] | str | None
    _ms_scroll_rails: (
        Literal[
            "enum, length",
            "none",
            "railed",
        ]
        | str
        | None
    )
    _ms_scroll_snap_points_x: (
        Literal[
            "enum",
            "snapInterval(100%, 100%)",
            "snapList()",
        ]
        | str
        | None
    )
    _ms_scroll_snap_points_y: (
        Literal[
            "enum",
            "snapInterval(100%, 100%)",
            "snapList()",
        ]
        | str
        | None
    )
    _ms_scroll_snap_type: (
        Literal[
            "enum",
            "none",
            "mandatory",
            "proximity",
        ]
        | str
        | None
    )
    _ms_scroll_snap_x: (
        Literal[
            "enum",
            "mandatory",
            "none",
            "proximity",
            "snapInterval(100%, 100%)",
            "snapList()",
        ]
        | str
        | None
    )
    _ms_scroll_snap_y: (
        Literal[
            "enum",
            "mandatory",
            "none",
            "proximity",
            "snapInterval(100%, 100%)",
            "snapList()",
        ]
        | str
        | None
    )
    _ms_scroll_translation: (
        Literal[
            "enum",
            "none",
            "vertical-to-horizontal",
        ]
        | str
        | None
    )
    _ms_scrollbar_3dlight_color: Literal["color",] | str | None
    _ms_scrollbar_arrow_color: Literal["color",] | str | None
    _ms_scrollbar_base_color: Literal["color",] | str | None
    _ms_scrollbar_darkshadow_color: Literal["color",] | str | None
    _ms_scrollbar_face_color: Literal["color",] | str | None
    _ms_scrollbar_highlight_color: Literal["color",] | str | None
    _ms_scrollbar_shadow_color: Literal["color",] | str | None
    _ms_scrollbar_track_color: Literal["color",] | str | None
    _ms_text_align_last: (
        Literal[
            "enum",
            "auto",
            "center",
            "end",
            "justify",
            "left",
            "right",
            "start",
        ]
        | str
        | None
    )
    _ms_text_autospace: (
        Literal[
            "enum",
            "ideograph-alpha",
            "ideograph-numeric",
            "ideograph-parenthesis",
            "ideograph-space",
            "none",
            "punctuation",
        ]
        | str
        | None
    )
    _ms_text_combine_horizontal: (
        Literal[
            "enum, integer",
            "all",
            "digits",
            "none",
        ]
        | str
        | None
    )
    _ms_text_justify: (
        Literal[
            "enum",
            "auto",
            "distribute",
            "inter-cluster",
            "inter-ideograph",
            "inter-word",
            "kashida",
            "none",
            "trim",
        ]
        | str
        | None
    )
    _ms_text_kashida_space: Literal["percentage",] | str | None
    _ms_text_overflow: (
        Literal[
            "enum",
            "clip",
            "ellipsis",
        ]
        | str
        | None
    )
    _ms_text_size_adjust: (
        Literal[
            "enum, percentage",
            "auto",
            "none",
        ]
        | str
        | None
    )
    _ms_text_underline_position: (
        Literal[
            "enum",
            "alphabetic",
            "auto",
            "over",
            "under",
        ]
        | str
        | None
    )
    _ms_touch_action: (
        Literal[
            "enum",
            "auto",
            "double-tap-zoom",
            "manipulation",
            "none",
            "pan-x",
            "pan-y",
            "pinch-zoom",
        ]
        | str
        | None
    )
    _ms_touch_select: (
        Literal[
            "enum",
            "grippers",
            "none",
        ]
        | str
        | None
    )
    _ms_transform: (
        Literal[
            "enum",
            "matrix()",
            "matrix3d()",
            "none",
            "rotate()",
            "rotate3d()",
            "rotateX('angle')",
            "rotateY('angle')",
            "rotateZ('angle')",
            "scale()",
            "scale3d()",
            "scaleX()",
            "scaleY()",
            "scaleZ()",
            "skew()",
            "skewX()",
            "skewY()",
            "translate()",
            "translate3d()",
            "translateX()",
            "translateY()",
            "translateZ()",
        ]
        | str
        | None
    )
    _ms_transform_origin: Literal["position, length, percentage",] | str | None
    _ms_transform_origin_x: Literal["length, percentage",] | str | None
    _ms_transform_origin_y: Literal["length, percentage",] | str | None
    _ms_transform_origin_z: Literal["length, percentage",] | str | None
    _ms_user_select: (
        Literal[
            "enum",
            "element",
            "none",
            "text",
        ]
        | str
        | None
    )
    _ms_word_break: (
        Literal[
            "enum",
            "break-all",
            "keep-all",
            "normal",
        ]
        | str
        | None
    )
    _ms_word_wrap: (
        Literal[
            "enum",
            "break-word",
            "hyphenate",
            "normal",
        ]
        | str
        | None
    )
    _ms_wrap_flow: (
        Literal[
            "enum",
            "auto",
            "both",
            "clear",
            "end",
            "maximum",
            "minimum",
            "start",
        ]
        | str
        | None
    )
    _ms_wrap_margin: Literal["length, percentage",] | str | None
    _ms_wrap_through: (
        Literal[
            "enum",
            "none",
            "wrap",
        ]
        | str
        | None
    )
    _ms_writing_mode: (
        Literal[
            "enum",
            "bt-lr",
            "bt-rl",
            "lr-bt",
            "lr-tb",
            "rl-bt",
            "rl-tb",
            "tb-lr",
            "tb-rl",
        ]
        | str
        | None
    )
    _ms_zoom: Literal["enum, integer, number, percentage",] | str | None
    _ms_zoom_animation: (
        Literal[
            "enum",
            "default",
            "none",
        ]
        | str
        | None
    )
    _o_animation: (
        Literal[
            "time, enum, timing-function, identifier, number",
            "alternate",
            "alternate-reverse",
            "backwards",
            "both",
            "forwards",
            "infinite",
            "none",
            "normal",
            "reverse",
        ]
        | str
        | None
    )
    _o_animation_delay: Literal["time",] | str | None
    _o_animation_direction: (
        Literal[
            "enum",
            "alternate",
            "alternate-reverse",
            "normal",
            "reverse",
        ]
        | str
        | None
    )
    _o_animation_duration: Literal["time",] | str | None
    _o_animation_fill_mode: (
        Literal[
            "enum",
            "backwards",
            "both",
            "forwards",
            "none",
        ]
        | str
        | None
    )
    _o_animation_iteration_count: Literal["number, enum",] | str | None
    _o_animation_name: Literal["identifier, enum",] | str | None
    _o_animation_play_state: (
        Literal[
            "enum",
            "paused",
            "running",
        ]
        | str
        | None
    )
    _o_animation_timing_function: Literal["timing-function",] | str | None
    _o_border_image: (
        Literal[
            "length, percentage, number, image, enum",
            "auto",
            "fill",
            "none",
            "repeat",
            "round",
            "space",
            "stretch",
        ]
        | str
        | None
    )
    _o_object_fit: (
        Literal[
            "enum",
            "contain",
            "cover",
            "fill",
            "none",
            "scale-down",
        ]
        | str
        | None
    )
    _o_object_position: Literal["position, length, percentage",] | str | None
    _o_tab_size: Literal["integer, length",] | str | None
    _o_table_baseline: Literal["integer",] | str | None
    _o_text_overflow: (
        Literal[
            "enum",
            "clip",
            "ellipsis",
        ]
        | str
        | None
    )
    _o_transform: (
        Literal[
            "enum",
            "matrix()",
            "matrix3d()",
            "none",
            "rotate()",
            "rotate3d()",
            "rotateX('angle')",
            "rotateY('angle')",
            "rotateZ('angle')",
            "scale()",
            "scale3d()",
            "scaleX()",
            "scaleY()",
            "scaleZ()",
            "skew()",
            "skewX()",
            "skewY()",
            "translate()",
            "translate3d()",
            "translateX()",
            "translateY()",
            "translateZ()",
        ]
        | str
        | None
    )
    _o_transform_origin: Literal["positon, length, percentage",] | str | None
    _o_transition: (
        Literal[
            "time, property, timing-function, enum",
            "all",
            "none",
        ]
        | str
        | None
    )
    _o_transition_delay: Literal["time",] | str | None
    _o_transition_duration: Literal["time",] | str | None
    _o_transition_property: Literal["property",] | str | None
    _o_transition_timing_function: Literal["timing-function",] | str | None
    _webkit_animation: (
        Literal[
            "time, enum, timing-function, identifier, number",
            "alternate",
            "alternate-reverse",
            "backwards",
            "both",
            "forwards",
            "infinite",
            "none",
            "normal",
            "reverse",
        ]
        | str
        | None
    )
    _webkit_animation_delay: Literal["time",] | str | None
    _webkit_animation_direction: (
        Literal[
            "enum",
            "alternate",
            "alternate-reverse",
            "normal",
            "reverse",
        ]
        | str
        | None
    )
    _webkit_animation_duration: Literal["time",] | str | None
    _webkit_animation_fill_mode: (
        Literal[
            "enum",
            "backwards",
            "both",
            "forwards",
            "none",
        ]
        | str
        | None
    )
    _webkit_animation_iteration_count: Literal["number, enum",] | str | None
    _webkit_animation_name: Literal["identifier, enum",] | str | None
    _webkit_animation_play_state: (
        Literal[
            "enum",
            "paused",
            "running",
        ]
        | str
        | None
    )
    _webkit_animation_timing_function: Literal["timing-function",] | str | None
    _webkit_appearance: (
        Literal[
            "enum",
            "button",
            "button-bevel",
            "caps-lock-indicator",
            "caret",
            "checkbox",
            "default-button",
            "listbox",
            "listitem",
            "media-fullscreen-button",
            "media-mute-button",
            "media-play-button",
            "media-seek-back-button",
            "media-seek-forward-button",
            "media-slider",
            "media-sliderthumb",
            "menulist",
            "menulist-button",
            "menulist-text",
            "menulist-textfield",
            "none",
            "push-button",
            "radio",
            "scrollbarbutton-down",
            "scrollbarbutton-left",
            "scrollbarbutton-right",
            "scrollbarbutton-up",
            "scrollbargripper-horizontal",
            "scrollbargripper-vertical",
            "scrollbarthumb-horizontal",
            "scrollbarthumb-vertical",
            "scrollbartrack-horizontal",
            "scrollbartrack-vertical",
            "searchfield",
            "searchfield-cancel-button",
            "searchfield-decoration",
            "searchfield-results-button",
            "searchfield-results-decoration",
            "slider-horizontal",
            "sliderthumb-horizontal",
            "sliderthumb-vertical",
            "slider-vertical",
            "square-button",
            "textarea",
            "textfield",
        ]
        | str
        | None
    )
    _webkit_backdrop_filter: (
        Literal[
            "enum, url",
            "none",
            "blur()",
            "brightness()",
            "contrast()",
            "drop-shadow()",
            "grayscale()",
            "hue-rotate()",
            "invert()",
            "opacity()",
            "saturate()",
            "sepia()",
            "url()",
        ]
        | str
        | None
    )
    _webkit_backface_visibility: (
        Literal[
            "enum",
            "hidden",
            "visible",
        ]
        | str
        | None
    )
    _webkit_background_clip: Literal["box",] | str | None
    _webkit_background_composite: (
        Literal[
            "enum",
            "border",
            "padding",
        ]
        | str
        | None
    )
    _webkit_background_origin: Literal["box",] | str | None
    _webkit_border_image: (
        Literal[
            "length, percentage, number, url, enum",
            "auto",
            "fill",
            "none",
            "repeat",
            "round",
            "space",
            "stretch",
            "url()",
        ]
        | str
        | None
    )
    _webkit_box_align: (
        Literal[
            "enum",
            "baseline",
            "center",
            "end",
            "start",
            "stretch",
        ]
        | str
        | None
    )
    _webkit_box_direction: (
        Literal[
            "enum",
            "normal",
            "reverse",
        ]
        | str
        | None
    )
    _webkit_box_flex: Literal["number",] | str | None
    _webkit_box_flex_group: Literal["integer",] | str | None
    _webkit_box_ordinal_group: Literal["integer",] | str | None
    _webkit_box_orient: (
        Literal[
            "enum",
            "block-axis",
            "horizontal",
            "inline-axis",
            "vertical",
        ]
        | str
        | None
    )
    _webkit_box_pack: (
        Literal[
            "enum",
            "center",
            "end",
            "justify",
            "start",
        ]
        | str
        | None
    )
    _webkit_box_reflect: str | None
    _webkit_box_sizing: (
        Literal[
            "enum",
            "border-box",
            "content-box",
        ]
        | str
        | None
    )
    _webkit_break_after: (
        Literal[
            "enum",
            "always",
            "auto",
            "avoid",
            "avoid-column",
            "avoid-page",
            "avoid-region",
            "column",
            "left",
            "page",
            "region",
            "right",
        ]
        | str
        | None
    )
    _webkit_break_before: (
        Literal[
            "enum",
            "always",
            "auto",
            "avoid",
            "avoid-column",
            "avoid-page",
            "avoid-region",
            "column",
            "left",
            "page",
            "region",
            "right",
        ]
        | str
        | None
    )
    _webkit_break_inside: (
        Literal[
            "enum",
            "auto",
            "avoid",
            "avoid-column",
            "avoid-page",
            "avoid-region",
        ]
        | str
        | None
    )
    _webkit_column_break_after: (
        Literal[
            "enum",
            "always",
            "auto",
            "avoid",
            "avoid-column",
            "avoid-page",
            "avoid-region",
            "column",
            "left",
            "page",
            "region",
            "right",
        ]
        | str
        | None
    )
    _webkit_column_break_before: (
        Literal[
            "enum",
            "always",
            "auto",
            "avoid",
            "avoid-column",
            "avoid-page",
            "avoid-region",
            "column",
            "left",
            "page",
            "region",
            "right",
        ]
        | str
        | None
    )
    _webkit_column_break_inside: (
        Literal[
            "enum",
            "auto",
            "avoid",
            "avoid-column",
            "avoid-page",
            "avoid-region",
        ]
        | str
        | None
    )
    _webkit_column_count: Literal["integer",] | str | None
    _webkit_column_gap: Literal["length",] | str | None
    _webkit_column_rule: Literal["length, line-width, line-style, color",] | str | None
    _webkit_column_rule_color: Literal["color",] | str | None
    _webkit_column_rule_style: Literal["line-style",] | str | None
    _webkit_column_rule_width: Literal["length, line-width",] | str | None
    _webkit_column_span: (
        Literal[
            "enum",
            "all",
            "none",
        ]
        | str
        | None
    )
    _webkit_column_width: Literal["length",] | str | None
    _webkit_columns: Literal["length, integer",] | str | None
    _webkit_filter: (
        Literal[
            "enum, url",
            "none",
            "blur()",
            "brightness()",
            "contrast()",
            "drop-shadow()",
            "grayscale()",
            "hue-rotate()",
            "invert()",
            "opacity()",
            "saturate()",
            "sepia()",
            "url()",
        ]
        | str
        | None
    )
    _webkit_flow_from: Literal["identifier",] | str | None
    _webkit_flow_into: Literal["identifier",] | str | None
    _webkit_font_feature_settings: Literal["string, integer",] | str | None
    _webkit_hyphens: (
        Literal[
            "enum",
            "auto",
            "manual",
            "none",
        ]
        | str
        | None
    )
    _webkit_line_break: str | None
    _webkit_margin_bottom_collapse: (
        Literal[
            "enum",
            "collapse",
            "discard",
            "separate",
        ]
        | str
        | None
    )
    _webkit_margin_collapse: (
        Literal[
            "enum",
            "collapse",
            "discard",
            "separate",
        ]
        | str
        | None
    )
    _webkit_margin_start: Literal["percentage, length",] | str | None
    _webkit_margin_top_collapse: (
        Literal[
            "enum",
            "collapse",
            "discard",
            "separate",
        ]
        | str
        | None
    )
    _webkit_mask_clip: Literal["box",] | str | None
    _webkit_mask_image: (
        Literal[
            "url, image, enum",
            "none",
            "url()",
        ]
        | str
        | None
    )
    _webkit_mask_origin: Literal["box",] | str | None
    _webkit_mask_repeat: Literal["repeat",] | str | None
    _webkit_mask_size: (
        Literal[
            "length, percentage, enum",
            "auto",
            "contain",
            "cover",
        ]
        | str
        | None
    )
    _webkit_nbsp_mode: str | None
    _webkit_overflow_scrolling: str | None
    _webkit_padding_start: Literal["percentage, length",] | str | None
    _webkit_perspective: Literal["length",] | str | None
    _webkit_perspective_origin: Literal["position, percentage, length",] | str | None
    _webkit_region_fragment: (
        Literal[
            "enum",
            "auto",
            "break",
        ]
        | str
        | None
    )
    _webkit_tap_highlight_color: Literal["color",] | str | None
    _webkit_text_fill_color: Literal["color",] | str | None
    _webkit_text_size_adjust: Literal["percentage",] | str | None
    _webkit_text_stroke: Literal["length, line-width, color, percentage",] | str | None
    _webkit_text_stroke_color: Literal["color",] | str | None
    _webkit_text_stroke_width: Literal["length, line-width, percentage",] | str | None
    _webkit_touch_callout: Literal["enum",] | str | None
    _webkit_transform: (
        Literal[
            "enum",
            "matrix()",
            "matrix3d()",
            "none",
            "perspective()",
            "rotate()",
            "rotate3d()",
            "rotateX('angle')",
            "rotateY('angle')",
            "rotateZ('angle')",
            "scale()",
            "scale3d()",
            "scaleX()",
            "scaleY()",
            "scaleZ()",
            "skew()",
            "skewX()",
            "skewY()",
            "translate()",
            "translate3d()",
            "translateX()",
            "translateY()",
            "translateZ()",
        ]
        | str
        | None
    )
    _webkit_transform_origin: Literal["position, length, percentage",] | str | None
    _webkit_transform_origin_x: Literal["length, percentage",] | str | None
    _webkit_transform_origin_y: Literal["length, percentage",] | str | None
    _webkit_transform_origin_z: Literal["length, percentage",] | str | None
    _webkit_transform_style: (
        Literal[
            "enum",
            "flat",
            "preserve-3d",
        ]
        | str
        | None
    )
    _webkit_transition: (
        Literal[
            "time, property, timing-function, enum",
            "all",
            "none",
        ]
        | str
        | None
    )
    _webkit_transition_delay: Literal["time",] | str | None
    _webkit_transition_duration: Literal["time",] | str | None
    _webkit_transition_property: Literal["property",] | str | None
    _webkit_transition_timing_function: Literal["timing-function",] | str | None
    _webkit_user_drag: (
        Literal[
            "enum",
            "auto",
            "element",
            "none",
        ]
        | str
        | None
    )
    _webkit_user_modify: (
        Literal[
            "enum",
            "read-only",
            "read-write",
            "read-write-plaintext-only",
        ]
        | str
        | None
    )
    _webkit_user_select: (
        Literal[
            "enum",
            "auto",
            "none",
            "text",
        ]
        | str
        | None
    )
    additive_symbols: Literal["integer, string, image, identifier",] | str | None
    align_content: (
        Literal[
            "enum",
            "center",
            "flex-end",
            "flex-start",
            "space-around",
            "space-between",
            "stretch",
            "start",
            "end",
            "normal",
            "baseline",
            "first baseline",
            "last baseline",
            "space-around",
            "space-between",
            "space-evenly",
            "stretch",
            "safe",
            "unsafe",
        ]
        | str
        | None
    )
    align_items: (
        Literal[
            "enum",
            "baseline",
            "center",
            "flex-end",
            "flex-start",
            "stretch",
            "normal",
            "start",
            "end",
            "self-start",
            "self-end",
            "first baseline",
            "last baseline",
            "stretch",
            "safe",
            "unsafe",
        ]
        | str
        | None
    )
    align_self: (
        Literal[
            "enum",
            "auto",
            "normal",
            "self-end",
            "self-start",
            "baseline",
            "center",
            "flex-end",
            "flex-start",
            "stretch",
            "baseline",
            "first baseline",
            "last baseline",
            "safe",
            "unsafe",
        ]
        | str
        | None
    )
    alignment_baseline: (
        Literal[
            "enum",
            "alphabetic",
            "baseline",
            "bottom",
            "center",
            "central",
            "mathematical",
            "middle",
            "text-bottom",
            "text-top",
            "top",
        ]
        | str
        | None
    )
    all: Literal["enum",] | str | None
    alt: Literal["string, enum",] | str | None
    animation: (
        Literal[
            "time, timing-function, enum, identifier, number",
            "alternate",
            "alternate-reverse",
            "backwards",
            "both",
            "forwards",
            "infinite",
            "none",
            "normal",
            "reverse",
        ]
        | str
        | None
    )
    animation_composition: (
        Literal[
            "enum",
            "accumulate",
            "add",
            "replace",
        ]
        | str
        | None
    )
    animation_delay: Literal["time",] | str | None
    animation_direction: (
        Literal[
            "enum",
            "alternate",
            "alternate-reverse",
            "normal",
            "reverse",
        ]
        | str
        | None
    )
    animation_duration: Literal["time",] | str | None
    animation_fill_mode: (
        Literal[
            "enum",
            "backwards",
            "both",
            "forwards",
            "none",
        ]
        | str
        | None
    )
    animation_iteration_count: Literal["number, enum",] | str | None
    animation_name: Literal["identifier, enum",] | str | None
    animation_play_state: (
        Literal[
            "enum",
            "paused",
            "running",
        ]
        | str
        | None
    )
    animation_timing_function: Literal["timing-function",] | str | None
    backdrop_filter: (
        Literal[
            "enum, url",
            "none",
            "blur()",
            "brightness()",
            "contrast()",
            "drop-shadow()",
            "grayscale()",
            "hue-rotate()",
            "invert()",
            "opacity()",
            "saturate()",
            "sepia()",
            "url()",
        ]
        | str
        | None
    )
    backface_visibility: (
        Literal[
            "enum",
            "hidden",
            "visible",
        ]
        | str
        | None
    )
    background: (
        Literal[
            "enum, image, color, position, length, repeat, percentage, box",
            "fixed",
            "local",
            "none",
            "scroll",
        ]
        | str
        | None
    )
    background_attachment: (
        Literal[
            "enum",
            "fixed",
            "local",
            "scroll",
        ]
        | str
        | None
    )
    background_blend_mode: (
        Literal[
            "enum",
            "normal",
            "multiply",
            "screen",
            "overlay",
            "darken",
            "lighten",
            "color-dodge",
            "color-burn",
            "hard-light",
            "soft-light",
            "difference",
            "exclusion",
            "hue",
            "saturation",
            "color",
            "luminosity",
        ]
        | str
        | None
    )
    background_clip: Literal["box",] | str | None
    background_color: Literal["color",] | str | None
    background_image: Literal["image, enum",] | str | None
    background_image_transform: (
        Literal[
            "enum",
            "logical",
            "physical",
            "rotate",
        ]
        | str
        | None
    )
    background_origin: Literal["box",] | str | None
    background_position: Literal["position, length, percentage",] | str | None
    background_position_x: Literal["length, percentage",] | str | None
    background_position_y: Literal["length, percentage",] | str | None
    background_repeat: Literal["repeat",] | str | None
    background_size: Literal["length, percentage",] | str | None
    baseline_shift: (
        Literal[
            "length, percentage, enum",
            "sub",
            "super",
        ]
        | str
        | None
    )
    behavior: Literal["url",] | str | None
    block_size: Literal["length, percentage",] | str | None
    border: Literal["length, line-width, line-style, color",] | str | None
    border_block_end: Literal["length, line-width, line-style, color",] | str | None
    border_block_end_color: Literal["color",] | str | None
    border_block_end_style: Literal["line-style",] | str | None
    border_block_end_width: Literal["length, line-width",] | str | None
    border_block_start: Literal["length, line-width, line-style, color",] | str | None
    border_block_start_color: Literal["color",] | str | None
    border_block_start_style: Literal["line-style",] | str | None
    border_block_start_width: Literal["length, line-width",] | str | None
    border_bottom: Literal["length, line-width, line-style, color",] | str | None
    border_bottom_color: Literal["color",] | str | None
    border_bottom_left_radius: Literal["length, percentage",] | str | None
    border_bottom_right_radius: Literal["length, percentage",] | str | None
    border_bottom_style: Literal["line-style",] | str | None
    border_bottom_width: Literal["length, line-width",] | str | None
    border_collapse: (
        Literal[
            "enum",
            "collapse",
            "separate",
        ]
        | str
        | None
    )
    border_color: Literal["color",] | str | None
    border_image: (
        Literal[
            "length, percentage, number, url, enum",
            "auto",
            "fill",
            "none",
            "repeat",
            "round",
            "space",
            "stretch",
            "url()",
        ]
        | str
        | None
    )
    border_image_outset: Literal["length, number",] | str | None
    border_image_repeat: (
        Literal[
            "enum",
            "repeat",
            "round",
            "space",
            "stretch",
        ]
        | str
        | None
    )
    border_image_slice: Literal["number, percentage",] | str | None
    border_image_source: Literal["image",] | str | None
    border_image_transform: (
        Literal[
            "enum",
            "logical",
            "physical",
            "rotate",
        ]
        | str
        | None
    )
    border_image_width: Literal["length, percentage, number",] | str | None
    border_inline_end: Literal["length, line-width, line-style, color",] | str | None
    border_inline_end_color: Literal["color",] | str | None
    border_inline_end_style: Literal["line-style",] | str | None
    border_inline_end_width: Literal["length, line-width",] | str | None
    border_inline_start: Literal["length, line-width, line-style, color",] | str | None
    border_inline_start_color: Literal["color",] | str | None
    border_inline_start_style: Literal["line-style",] | str | None
    border_inline_start_width: Literal["length, line-width",] | str | None
    border_left: Literal["length, line-width, line-style, color",] | str | None
    border_left_color: Literal["color",] | str | None
    border_left_style: Literal["line-style",] | str | None
    border_left_width: Literal["length, line-width",] | str | None
    border_radius: Literal["length, percentage",] | str | None
    border_right: Literal["length, line-width, line-style, color",] | str | None
    border_right_color: Literal["color",] | str | None
    border_right_style: Literal["line-style",] | str | None
    border_right_width: Literal["length, line-width",] | str | None
    border_spacing: Literal["length",] | str | None
    border_style: Literal["line-style",] | str | None
    border_top: Literal["length, line-width, line-style, color",] | str | None
    border_top_color: Literal["color",] | str | None
    border_top_left_radius: Literal["length, percentage",] | str | None
    border_top_right_radius: Literal["length, percentage",] | str | None
    border_top_style: Literal["line-style",] | str | None
    border_top_width: Literal["length, line-width",] | str | None
    border_width: Literal["length, line-width",] | str | None
    bottom: Literal["length, percentage",] | str | None
    box_decoration_break: (
        Literal[
            "enum",
            "clone",
            "slice",
        ]
        | str
        | None
    )
    box_shadow: (
        Literal[
            "length, color, enum",
            "inset",
            "none",
        ]
        | str
        | None
    )
    box_sizing: (
        Literal[
            "enum",
            "border-box",
            "content-box",
        ]
        | str
        | None
    )
    box_snap: (
        Literal[
            "enum",
            "none",
            "block-start",
            "block-end",
            "center",
            "baseline",
            "last-baseline",
        ]
        | str
        | None
    )
    box_suppress: (
        Literal[
            "enum",
            "show",
            "discard",
            "hide",
        ]
        | str
        | None
    )
    break_after: (
        Literal[
            "enum",
            "always",
            "auto",
            "avoid",
            "avoid-column",
            "avoid-page",
            "avoid-region",
            "column",
            "left",
            "page",
            "region",
            "right",
            "recto",
            "verso",
        ]
        | str
        | None
    )
    break_before: (
        Literal[
            "enum",
            "always",
            "auto",
            "avoid",
            "avoid-column",
            "avoid-page",
            "avoid-region",
            "column",
            "left",
            "page",
            "region",
            "right",
            "recto",
            "verso",
        ]
        | str
        | None
    )
    break_inside: (
        Literal[
            "enum",
            "auto",
            "avoid",
            "avoid-column",
            "avoid-page",
            "avoid-region",
        ]
        | str
        | None
    )
    caption_side: (
        Literal[
            "enum",
            "block-end",
            "block-start",
            "bottom",
            "inline-end",
            "inline-start",
            "top",
        ]
        | str
        | None
    )
    caret_color: Literal["color, enum",] | str | None
    clear: (
        Literal[
            "enum",
            "both",
            "inline-end",
            "inline-start",
            "left",
            "none",
            "right",
        ]
        | str
        | None
    )
    clip: (
        Literal[
            "enum",
            "auto",
            "rect()",
        ]
        | str
        | None
    )
    clip_path: (
        Literal[
            "url, shape, geometry-box, enum",
            "none",
            "url()",
        ]
        | str
        | None
    )
    clip_rule: (
        Literal[
            "enum",
            "evenodd",
            "nonzero",
        ]
        | str
        | None
    )
    color: Literal["color",] | str | None
    color_adjust: (
        Literal[
            "enum",
            "economy",
            "exact",
        ]
        | str
        | None
    )
    color_interpolation: (
        Literal[
            "enum",
            "auto",
            "linearRGB",
            "sRGB",
        ]
        | str
        | None
    )
    color_interpolation_filters: (
        Literal[
            "enum",
            "auto",
            "linearRGB",
            "sRGB",
        ]
        | str
        | None
    )
    color_rendering: (
        Literal[
            "enum",
            "auto",
            "optimizeQuality",
            "optimizeSpeed",
        ]
        | str
        | None
    )
    column_count: Literal["integer, enum",] | str | None
    column_fill: (
        Literal[
            "enum",
            "auto",
            "balance",
        ]
        | str
        | None
    )
    column_gap: Literal["length, enum",] | str | None
    column_rule: Literal["length, line-width, line-style, color",] | str | None
    column_rule_color: Literal["color",] | str | None
    column_rule_style: Literal["line-style",] | str | None
    column_rule_width: Literal["length, line-width",] | str | None
    column_span: (
        Literal[
            "enum",
            "all",
            "none",
        ]
        | str
        | None
    )
    column_width: (
        Literal[
            "length, enum",
            "auto",
            "fill",
            "fit-content",
            "max-content",
            "min-content",
        ]
        | str
        | None
    )
    columns: Literal["length, integer, enum",] | str | None
    contain: (
        Literal[
            "enum",
            "none",
            "strict",
            "content",
            "size",
            "layout",
            "style",
            "paint",
        ]
        | str
        | None
    )
    content: Literal["string, url",] | str | None
    counter_increment: Literal["identifier, integer",] | str | None
    counter_reset: Literal["identifier, integer",] | str | None
    crop: (
        Literal[
            "enum",
            "auto",
            "insert-rect(top, right, bottom, left)",
            "rect(top, right, bottom, left)",
        ]
        | str
        | None
    )
    cue: (
        Literal[
            "url, volume, enum",
            "none",
            "url()",
        ]
        | str
        | None
    )
    cue_after: (
        Literal[
            "url, volume, enum",
            "none",
            "url()",
        ]
        | str
        | None
    )
    cue_before: (
        Literal[
            "url, volume, enum",
            "none",
            "url()",
        ]
        | str
        | None
    )
    cursor: (
        Literal[
            "url, number, enum",
            "alias",
            "all-scroll",
            "auto",
            "cell",
            "col-resize",
            "context-menu",
            "copy",
            "crosshair",
            "default",
            "e-resize",
            "ew-resize",
            "grab",
            "grabbing",
            "help",
            "move",
            "-moz-grab",
            "-moz-grabbing",
            "-moz-zoom-in",
            "-moz-zoom-out",
            "ne-resize",
            "nesw-resize",
            "no-drop",
            "none",
            "not-allowed",
            "n-resize",
            "ns-resize",
            "nw-resize",
            "nwse-resize",
            "pointer",
            "progress",
            "row-resize",
            "se-resize",
            "s-resize",
            "sw-resize",
            "text",
            "vertical-text",
            "wait",
            "-webkit-grab",
            "-webkit-grabbing",
            "-webkit-zoom-in",
            "-webkit-zoom-out",
            "w-resize",
            "zoom-in",
            "zoom-out",
        ]
        | str
        | None
    )
    cx: Literal["length, percentage",] | str | None
    cy: Literal["length, percentage",] | str | None
    direction: (
        Literal[
            "enum",
            "ltr",
            "rtl",
        ]
        | str
        | None
    )
    display: (
        Literal[
            "enum",
            "block",
            "contents",
            "flex",
            "flexbox",
            "flow",
            "flow-root",
            "grid",
            "inline",
            "inline-block",
            "inline-flex",
            "inline-flexbox",
            "inline-grid",
            "inline-table",
            "list-item",
            "-moz-box",
            "-moz-deck",
            "-moz-grid",
            "-moz-grid-group",
            "-moz-grid-line",
            "-moz-groupbox",
            "-moz-inline-box",
            "-moz-inline-grid",
            "-moz-inline-stack",
            "-moz-marker",
            "-moz-popup",
            "-moz-stack",
            "-ms-flexbox",
            "-ms-grid",
            "-ms-inline-flexbox",
            "-ms-inline-grid",
            "none",
            "ruby",
            "ruby-base",
            "ruby-base-container",
            "ruby-base-group",
            "ruby-text",
            "ruby-text-container",
            "ruby-text-group",
            "run-in",
            "table",
            "table-caption",
            "table-cell",
            "table-column",
            "table-column-group",
            "table-footer-group",
            "table-header-group",
            "table-row",
            "table-row-group",
            "-webkit-box",
            "-webkit-flex",
            "-webkit-inline-box",
            "-webkit-inline-flex",
        ]
        | str
        | None
    )
    dominant_baseline: (
        Literal[
            "enum",
            "auto",
            "text-bottom",
            "alphabetic",
            "central",
            "mathematical",
            "hanging",
            "text-top",
        ]
        | str
        | None
    )
    empty_cells: (
        Literal[
            "enum",
            "hide",
            "-moz-show-background",
            "show",
        ]
        | str
        | None
    )
    enable_background: (
        Literal[
            "integer, length, percentage, enum",
            "accumulate",
            "new",
        ]
        | str
        | None
    )
    fallback: Literal["identifier",] | str | None
    fill: (
        Literal[
            "color, enum, url",
            "child",
            "child()",
            "context-fill",
            "context-stroke",
            "url()",
            "none",
        ]
        | str
        | None
    )
    fill_opacity: Literal["number(0-1)",] | str | None
    fill_rule: (
        Literal[
            "enum",
            "evenodd",
            "nonzero",
        ]
        | str
        | None
    )
    filter: (
        Literal[
            "enum, url",
            "none",
            "blur()",
            "brightness()",
            "contrast()",
            "drop-shadow()",
            "grayscale()",
            "hue-rotate()",
            "invert()",
            "opacity()",
            "saturate()",
            "sepia()",
            "url()",
        ]
        | str
        | None
    )
    flex: Literal["length, number, percentage",] | str | None
    flex_basis: Literal["length, number, percentage",] | str | None
    flex_direction: (
        Literal[
            "enum",
            "column",
            "column-reverse",
            "row",
            "row-reverse",
        ]
        | str
        | None
    )
    flex_flow: (
        Literal[
            "enum",
            "column",
            "column-reverse",
            "nowrap",
            "row",
            "row-reverse",
            "wrap",
            "wrap-reverse",
        ]
        | str
        | None
    )
    flex_grow: Literal["number",] | str | None
    flex_shrink: Literal["number",] | str | None
    flex_wrap: (
        Literal[
            "enum",
            "nowrap",
            "wrap",
            "wrap-reverse",
        ]
        | str
        | None
    )
    float: (
        Literal[
            "enum",
            "inline-end",
            "inline-start",
            "left",
            "none",
            "right",
        ]
        | str
        | None
    )
    flood_color: Literal["color",] | str | None
    flood_opacity: Literal["number(0-1), percentage",] | str | None
    flow_from: Literal["identifier",] | str | None
    flow_into: Literal["identifier",] | str | None
    font: Literal["font",] | str | None
    font_family: Literal["font",] | str | None
    font_feature_settings: Literal["string, integer",] | str | None
    font_kerning: (
        Literal[
            "enum",
            "auto",
            "none",
            "normal",
        ]
        | str
        | None
    )
    font_language_override: Literal["string",] | str | None
    font_size: Literal["length, percentage",] | str | None
    font_size_adjust: Literal["number",] | str | None
    font_stretch: (
        Literal[
            "enum",
            "condensed",
            "expanded",
            "extra-condensed",
            "extra-expanded",
            "narrower",
            "normal",
            "semi-condensed",
            "semi-expanded",
            "ultra-condensed",
            "ultra-expanded",
            "wider",
        ]
        | str
        | None
    )
    font_style: (
        Literal[
            "enum",
            "italic",
            "normal",
            "oblique",
        ]
        | str
        | None
    )
    font_synthesis: (
        Literal[
            "enum",
            "none",
            "style",
            "weight",
        ]
        | str
        | None
    )
    font_variant: (
        Literal[
            "enum",
            "normal",
            "small-caps",
        ]
        | str
        | None
    )
    font_variant_alternates: (
        Literal[
            "enum",
            "annotation()",
            "character-variant()",
            "historical-forms",
            "normal",
            "ornaments()",
            "styleset()",
            "stylistic()",
            "swash()",
        ]
        | str
        | None
    )
    font_variant_caps: (
        Literal[
            "enum",
            "all-petite-caps",
            "all-small-caps",
            "normal",
            "petite-caps",
            "small-caps",
            "titling-caps",
            "unicase",
        ]
        | str
        | None
    )
    font_variant_east_asian: (
        Literal[
            "enum",
            "full-width",
            "jis04",
            "jis78",
            "jis83",
            "jis90",
            "normal",
            "proportional-width",
            "ruby",
            "simplified",
            "traditional",
        ]
        | str
        | None
    )
    font_variant_ligatures: (
        Literal[
            "enum",
            "additional-ligatures",
            "common-ligatures",
            "contextual",
            "discretionary-ligatures",
            "historical-ligatures",
            "no-additional-ligatures",
            "no-common-ligatures",
            "no-contextual",
            "no-discretionary-ligatures",
            "no-historical-ligatures",
            "none",
            "normal",
        ]
        | str
        | None
    )
    font_variant_numeric: (
        Literal[
            "enum",
            "diagonal-fractions",
            "lining-nums",
            "normal",
            "oldstyle-nums",
            "ordinal",
            "proportional-nums",
            "slashed-zero",
            "stacked-fractions",
            "tabular-nums",
        ]
        | str
        | None
    )
    font_variant_position: (
        Literal[
            "enum",
            "normal",
            "sub",
            "super",
        ]
        | str
        | None
    )
    font_weight: (
        Literal[
            "enum",
            "100",
            "200",
            "300",
            "400",
            "500",
            "600",
            "700",
            "800",
            "900",
            "bold",
            "bolder",
            "lighter",
            "normal",
        ]
        | str
        | None
    )
    glyph_orientation_horizontal: Literal["angle, number",] | str | None
    glyph_orientation_vertical: Literal["angle, number, enum",] | str | None
    grid: Literal["identifier, length, percentage, string, enum",] | str | None
    grid_area: Literal["identifier, integer",] | str | None
    grid_auto_columns: Literal["length, percentage",] | str | None
    grid_auto_flow: (
        Literal[
            "enum",
            "row",
            "column",
            "dense",
        ]
        | str
        | None
    )
    grid_auto_rows: Literal["length, percentage",] | str | None
    grid_column: (
        Literal[
            "identifier, integer, enum",
            "auto",
            "span",
        ]
        | str
        | None
    )
    grid_column_end: (
        Literal[
            "identifier, integer, enum",
            "auto",
            "span",
        ]
        | str
        | None
    )
    grid_column_gap: Literal["length",] | str | None
    grid_column_start: (
        Literal[
            "identifier, integer, enum",
            "auto",
            "span",
        ]
        | str
        | None
    )
    grid_gap: Literal["length",] | str | None
    grid_row: (
        Literal[
            "identifier, integer, enum",
            "auto",
            "span",
        ]
        | str
        | None
    )
    grid_row_end: (
        Literal[
            "identifier, integer, enum",
            "auto",
            "span",
        ]
        | str
        | None
    )
    grid_row_gap: Literal["length",] | str | None
    grid_row_start: (
        Literal[
            "identifier, integer, enum",
            "auto",
            "span",
        ]
        | str
        | None
    )
    grid_template: (
        Literal[
            "identifier, length, percentage, string, enum",
            "none",
            "min-content",
            "max-content",
            "auto",
            "subgrid",
            "minmax()",
            "repeat()",
        ]
        | str
        | None
    )
    grid_template_areas: Literal["string",] | str | None
    grid_template_columns: (
        Literal[
            "identifier, length, percentage, enum",
            "none",
            "min-content",
            "max-content",
            "auto",
            "subgrid",
            "minmax()",
            "repeat()",
        ]
        | str
        | None
    )
    grid_template_rows: (
        Literal[
            "identifier, length, percentage, string, enum",
            "none",
            "min-content",
            "max-content",
            "auto",
            "subgrid",
            "minmax()",
            "repeat()",
        ]
        | str
        | None
    )
    hanging_punctuation: (
        Literal[
            "enum",
            "allow-end",
            "first",
            "force-end",
            "last",
            "none",
        ]
        | str
        | None
    )
    height: Literal["length, percentage",] | str | None
    hyphenate_character: Literal["string, enum",] | str | None
    hyphenate_limit_chars: Literal["integer, enum",] | str | None
    hyphenate_limit_last: (
        Literal[
            "enum",
            "none",
            "always",
            "column",
            "page",
            "spread",
        ]
        | str
        | None
    )
    hyphenate_limit_lines: Literal["integer",] | str | None
    hyphenate_limit_zone: Literal["percentage, length",] | str | None
    hyphens: (
        Literal[
            "enum",
            "auto",
            "manual",
            "none",
        ]
        | str
        | None
    )
    image_orientation: Literal["angle",] | str | None
    image_rendering: (
        Literal[
            "enum",
            "auto",
            "crisp-edges",
            "-moz-crisp-edges",
            "optimizeQuality",
            "optimizeSpeed",
            "pixelated",
        ]
        | str
        | None
    )
    image_resolution: Literal["resolution",] | str | None
    ime_mode: (
        Literal[
            "enum",
            "active",
            "auto",
            "disabled",
            "inactive",
            "normal",
        ]
        | str
        | None
    )
    initial_letter: Literal["number, integer, enum",] | str | None
    initial_letter_align: (
        Literal[
            "enum",
            "alphabetic",
            "ideographic",
            "hebrew",
            "hanging",
            "border-box",
        ]
        | str
        | None
    )
    initial_letter_wrap: (
        Literal[
            "length, percentage, enum",
            "none",
            "first",
            "all",
            "grid",
        ]
        | str
        | None
    )
    inline_size: Literal["length, percentage",] | str | None
    isolation: (
        Literal[
            "enum",
            "auto",
            "isolate",
        ]
        | str
        | None
    )
    justify_content: (
        Literal[
            "enum",
            "center",
            "start",
            "end",
            "left",
            "right",
            "safe",
            "unsafe",
            "stretch",
            "space-evenly",
            "flex-end",
            "flex-start",
            "space-around",
            "space-between",
            "baseline",
            "first baseline",
            "last baseline",
        ]
        | str
        | None
    )
    justify_items: (
        Literal[
            "enum",
            "auto",
            "normal",
            "end",
            "start",
            "flex-end",
            "flex-start",
            "self-end",
            "self-start",
            "center",
            "left",
            "right",
            "baseline",
            "first baseline",
            "last baseline",
            "stretch",
            "safe",
            "unsafe",
            "legacy",
        ]
        | str
        | None
    )
    justify_self: (
        Literal[
            "enum",
            "auto",
            "normal",
            "end",
            "start",
            "flex-end",
            "flex-start",
            "self-end",
            "self-start",
            "center",
            "left",
            "right",
            "baseline",
            "first baseline",
            "last baseline",
            "stretch",
            "save",
            "unsave",
        ]
        | str
        | None
    )
    kerning: Literal["length, enum",] | str | None
    left: Literal["length, percentage",] | str | None
    letter_spacing: Literal["length",] | str | None
    lighting_color: Literal["color",] | str | None
    line_break: (
        Literal[
            "enum",
            "auto",
            "loose",
            "normal",
            "strict",
            "anywhere",
        ]
        | str
        | None
    )
    line_grid: (
        Literal[
            "enum",
            "match-parent",
            "create",
        ]
        | str
        | None
    )
    line_height: Literal["number, length, percentage",] | str | None
    line_snap: (
        Literal[
            "enum",
            "none",
            "baseline",
            "contain",
        ]
        | str
        | None
    )
    list_style: (
        Literal[
            "image, enum, url",
            "armenian",
            "circle",
            "decimal",
            "decimal-leading-zero",
            "disc",
            "georgian",
            "hanging",
            "inside",
            "lower-alpha",
            "lower-greek",
            "lower-latin",
            "lower-roman",
            "none",
            "outside",
            "square",
            "symbols()",
            "upper-alpha",
            "upper-latin",
            "upper-roman",
            "url()",
        ]
        | str
        | None
    )
    list_style_image: Literal["image",] | str | None
    list_style_position: (
        Literal[
            "enum",
            "inside",
            "outside",
        ]
        | str
        | None
    )
    list_style_type: (
        Literal[
            "enum, string",
            "arabic-indic",
            "armenian",
            "bengali",
            "cambodian",
            "circle",
            "cjk-decimal",
            "cjk-earthly-branch",
            "cjk-heavenly-stem",
            "decimal",
            "decimal-leading-zero",
            "devanagari",
            "disc",
            "disclosure-closed",
            "disclosure-open",
            "georgian",
            "gujarati",
            "gurmukhi",
            "hebrew",
            "hiragana",
            "hiragana-iroha",
            "kannada",
            "katakana",
            "katakana-iroha",
            "khmer",
            "lao",
            "lower-alpha",
            "lower-armenian",
            "lower-greek",
            "lower-latin",
            "lower-roman",
            "malayalam",
            "mongolian",
            "myanmar",
            "none",
            "oriya",
            "persian",
            "square",
            "tamil",
            "telugu",
            "thai",
            "tibetan",
            "symbols()",
            "upper-alpha",
            "upper-armenian",
            "upper-latin",
            "upper-roman",
        ]
        | str
        | None
    )
    margin: Literal["length, percentage",] | str | None
    margin_block_end: Literal["length, percentage",] | str | None
    margin_block_start: Literal["length, percentage",] | str | None
    margin_bottom: Literal["length, percentage",] | str | None
    margin_inline_end: Literal["length, percentage",] | str | None
    margin_inline_start: Literal["length, percentage",] | str | None
    margin_left: Literal["length, percentage",] | str | None
    margin_right: Literal["length, percentage",] | str | None
    margin_top: Literal["length, percentage",] | str | None
    marker: Literal["url",] | str | None
    marker_end: Literal["url",] | str | None
    marker_mid: Literal["url",] | str | None
    marker_side: (
        Literal[
            "enum",
            "list-item",
            "list-container",
        ]
        | str
        | None
    )
    marker_start: Literal["url",] | str | None
    mask: (
        Literal[
            "url, image, length, percentage, position, repeat, geometry-box, enum",
            "none",
            "url()",
            "alpha",
            "auto",
            "luminance",
            "contain",
            "cover",
            "no-clip",
            "add",
            "exclude",
            "intersect",
            "subtract",
        ]
        | str
        | None
    )
    mask_border: (
        Literal[
            "image, length, number, percentage, enum",
            "none",
            "fill",
            "auto",
            "repeat",
            "round",
            "space",
            "stretch",
            "alpha",
            "luminance",
        ]
        | str
        | None
    )
    mask_border_mode: (
        Literal[
            "enum",
            "alpha",
            "luminance",
        ]
        | str
        | None
    )
    mask_border_outset: Literal["length, number",] | str | None
    mask_border_repeat: (
        Literal[
            "enum",
            "repeat",
            "round",
            "space",
            "stretch",
        ]
        | str
        | None
    )
    mask_border_slice: Literal["number, percentage, enum",] | str | None
    mask_border_source: Literal["image, enum",] | str | None
    mask_border_width: Literal["length, percentage, enum",] | str | None
    mask_clip: Literal["geometry-box, enum",] | str | None
    mask_composite: (
        Literal[
            "enum",
            "add",
            "exclude",
            "intersect",
            "subtract",
        ]
        | str
        | None
    )
    mask_image: (
        Literal[
            "url, image, enum",
            "none",
            "url()",
        ]
        | str
        | None
    )
    mask_mode: (
        Literal[
            "url, image, enum",
            "alpha",
            "auto",
            "luminance",
        ]
        | str
        | None
    )
    mask_origin: Literal["geometry-box, enum",] | str | None
    mask_position: Literal["position, length, percentage",] | str | None
    mask_repeat: Literal["repeat",] | str | None
    mask_size: (
        Literal[
            "length, percentage, enum",
            "auto",
            "contain",
            "cover",
        ]
        | str
        | None
    )
    mask_type: (
        Literal[
            "enum",
            "alpha",
            "luminance",
        ]
        | str
        | None
    )
    max_block_size: Literal["length, percentage",] | str | None
    max_height: Literal["length, percentage",] | str | None
    max_inline_size: Literal["length, percentage",] | str | None
    max_lines: Literal["integer, enum",] | str | None
    max_width: Literal["length, percentage",] | str | None
    max_zoom: Literal["number, percentage, enum",] | str | None
    min_block_size: Literal["length, percentage",] | str | None
    min_height: Literal["length, percentage",] | str | None
    min_inline_size: Literal["length, percentage",] | str | None
    min_width: Literal["length, percentage",] | str | None
    min_zoom: Literal["number, percentage, enum",] | str | None
    mix_blend_mode: (
        Literal[
            "enum",
            "normal",
            "multiply",
            "screen",
            "overlay",
            "darken",
            "lighten",
            "color-dodge",
            "color-burn",
            "hard-light",
            "soft-light",
            "difference",
            "exclusion",
            "hue",
            "saturation",
            "color",
            "luminosity",
        ]
        | str
        | None
    )
    motion: (
        Literal[
            "url, length, percentage, angle, shape, geometry-box, enum",
            "none",
            "path()",
            "url()",
            "auto",
            "reverse",
        ]
        | str
        | None
    )
    motion_offset: Literal["length, percentage",] | str | None
    motion_path: (
        Literal[
            "url, shape, geometry-box, enum",
            "none",
            "path()",
            "url()",
        ]
        | str
        | None
    )
    motion_rotation: Literal["angle",] | str | None
    move_to: Literal["identifier",] | str | None
    nav_down: (
        Literal[
            "enum, identifier, string",
            "auto",
            "current",
            "root",
        ]
        | str
        | None
    )
    nav_index: Literal["number",] | str | None
    nav_left: (
        Literal[
            "enum, identifier, string",
            "auto",
            "current",
            "root",
        ]
        | str
        | None
    )
    nav_right: (
        Literal[
            "enum, identifier, string",
            "auto",
            "current",
            "root",
        ]
        | str
        | None
    )
    nav_up: (
        Literal[
            "enum, identifier, string",
            "auto",
            "current",
            "root",
        ]
        | str
        | None
    )
    negative: Literal["image, identifier, string",] | str | None
    object_fit: (
        Literal[
            "enum",
            "contain",
            "cover",
            "fill",
            "none",
            "scale-down",
        ]
        | str
        | None
    )
    object_position: Literal["position, length, percentage",] | str | None
    offset_block_end: Literal["length, percentage",] | str | None
    offset_block_start: Literal["length, percentage",] | str | None
    offset_inline_end: Literal["length, percentage",] | str | None
    offset_inline_start: Literal["length, percentage",] | str | None
    opacity: Literal["number(0-1)",] | str | None
    order: Literal["integer",] | str | None
    orientation: (
        Literal[
            "enum",
            "auto",
            "landscape",
            "portrait",
        ]
        | str
        | None
    )
    orphans: Literal["integer",] | str | None
    outline: (
        Literal[
            "length, line-width, line-style, color, enum",
            "auto",
            "invert",
        ]
        | str
        | None
    )
    outline_color: Literal["enum, color",] | str | None
    outline_offset: Literal["length",] | str | None
    outline_style: Literal["line-style, enum",] | str | None
    outline_width: Literal["length, line-width",] | str | None
    overflow: (
        Literal[
            "enum",
            "auto",
            "clip",
            "hidden",
            "-moz-hidden-unscrollable",
            "scroll",
            "visible",
        ]
        | str
        | None
    )
    overflow_wrap: (
        Literal[
            "enum",
            "break-word",
            "normal",
            "anywhere",
        ]
        | str
        | None
    )
    overflow_x: (
        Literal[
            "enum",
            "auto",
            "clip",
            "hidden",
            "scroll",
            "visible",
        ]
        | str
        | None
    )
    overflow_y: (
        Literal[
            "enum",
            "auto",
            "clip",
            "hidden",
            "scroll",
            "visible",
        ]
        | str
        | None
    )
    pad: Literal["integer, image, string, identifier",] | str | None
    padding: Literal["length, percentage",] | str | None
    padding_block_end: Literal["length, percentage",] | str | None
    padding_block_start: Literal["length, percentage",] | str | None
    padding_bottom: Literal["length, percentage",] | str | None
    padding_inline_end: Literal["length, percentage",] | str | None
    padding_inline_start: Literal["length, percentage",] | str | None
    padding_left: Literal["length, percentage",] | str | None
    padding_right: Literal["length, percentage",] | str | None
    padding_top: Literal["length, percentage",] | str | None
    page: Literal["identifier",] | str | None
    page_break_after: (
        Literal[
            "enum",
            "always",
            "auto",
            "avoid",
            "left",
            "recto",
            "right",
            "verso",
        ]
        | str
        | None
    )
    page_break_before: (
        Literal[
            "enum",
            "always",
            "auto",
            "avoid",
            "left",
            "right",
        ]
        | str
        | None
    )
    page_break_inside: (
        Literal[
            "enum",
            "auto",
            "avoid",
        ]
        | str
        | None
    )
    page_policy: (
        Literal[
            "enum",
            "first",
            "last",
            "start",
        ]
        | str
        | None
    )
    paint_order: (
        Literal[
            "enum",
            "fill",
            "markers",
            "normal",
            "stroke",
        ]
        | str
        | None
    )
    pause: (
        Literal[
            "time, enum",
            "medium",
            "none",
            "strong",
            "weak",
            "x-strong",
            "x-weak",
        ]
        | str
        | None
    )
    pause_after: Literal["time",] | str | None
    pause_before: Literal["time",] | str | None
    perspective: Literal["length, enum",] | str | None
    perspective_origin: Literal["position, percentage, length",] | str | None
    pointer_events: (
        Literal[
            "enum",
            "all",
            "fill",
            "none",
            "painted",
            "stroke",
            "visible",
            "visibleFill",
            "visiblePainted",
            "visibleStroke",
        ]
        | str
        | None
    )
    position: (
        Literal[
            "enum",
            "absolute",
            "center",
            "fixed",
            "-ms-page",
            "page",
            "relative",
            "static",
            "sticky",
            "-webkit-sticky",
        ]
        | str
        | None
    )
    prefix: Literal["image, string, identifier",] | str | None
    quotes: Literal["string",] | str | None
    r: Literal["length, percentage",] | str | None
    range: (
        Literal[
            "integer, enum",
            "auto",
            "infinite",
        ]
        | str
        | None
    )
    region_fragment: (
        Literal[
            "enum",
            "auto",
            "break",
        ]
        | str
        | None
    )
    resize: (
        Literal[
            "enum",
            "both",
            "block",
            "horizontal",
            "inline",
            "none",
            "vertical",
        ]
        | str
        | None
    )
    rest: Literal["time",] | str | None
    rest_after: Literal["time",] | str | None
    rest_before: Literal["time",] | str | None
    right: Literal["length, percentage",] | str | None
    rotation: Literal["angle",] | str | None
    rotation_point: Literal["position, percentage, length",] | str | None
    ruby_align: (
        Literal[
            "enum",
            "auto",
            "center",
            "distribute-letter",
            "distribute-space",
            "left",
            "line-edge",
            "right",
            "start",
            "space-between",
            "space-around",
        ]
        | str
        | None
    )
    ruby_overhang: (
        Literal[
            "enum",
            "auto",
            "end",
            "none",
            "start",
        ]
        | str
        | None
    )
    ruby_position: (
        Literal[
            "enum",
            "after",
            "before",
            "inline",
            "right",
        ]
        | str
        | None
    )
    ruby_span: (
        Literal[
            "enum",
            "attr(x)",
            "none",
        ]
        | str
        | None
    )
    rx: Literal["length, percentage",] | str | None
    ry: Literal["length, percentage",] | str | None
    scroll_behavior: (
        Literal[
            "enum",
            "auto",
            "smooth",
        ]
        | str
        | None
    )
    scroll_snap_coordinate: (
        Literal[
            "position, length, percentage, enum",
            "none",
            "border-box",
            "margin-box",
        ]
        | str
        | None
    )
    scroll_snap_destination: Literal["position, length, percentage",] | str | None
    scroll_snap_points_x: (
        Literal[
            "enum",
            "none",
            "repeat()",
        ]
        | str
        | None
    )
    scroll_snap_points_y: (
        Literal[
            "enum",
            "none",
            "repeat()",
        ]
        | str
        | None
    )
    scroll_snap_type: (
        Literal[
            "enum",
            "none",
            "mandatory",
            "proximity",
        ]
        | str
        | None
    )
    scrollbar_3dlight_color: Literal["color",] | str | None
    scrollbar_arrow_color: Literal["color",] | str | None
    scrollbar_base_color: Literal["color",] | str | None
    scrollbar_darkshadow_color: Literal["color",] | str | None
    scrollbar_face_color: Literal["color",] | str | None
    scrollbar_highlight_color: Literal["color",] | str | None
    scrollbar_shadow_color: Literal["color",] | str | None
    scrollbar_track_color: Literal["color",] | str | None
    shape_image_threshold: Literal["number",] | str | None
    shape_inside: (
        Literal[
            "image, shape, box, enum",
            "auto",
            "display",
            "margin-box",
            "outside-shape",
            "url()",
        ]
        | str
        | None
    )
    shape_margin: Literal["url, length, percentage",] | str | None
    shape_outside: (
        Literal[
            "image, box, shape, enum",
            "margin-box",
            "none",
        ]
        | str
        | None
    )
    shape_padding: Literal["length",] | str | None
    shape_rendering: (
        Literal[
            "enum",
            "auto",
            "crispEdges",
            "geometricPrecision",
            "optimizeSpeed",
        ]
        | str
        | None
    )
    size: Literal["length",] | str | None
    speak: (
        Literal[
            "enum",
            "auto",
            "none",
            "normal",
        ]
        | str
        | None
    )
    speak_as: (
        Literal[
            "enum",
            "digits",
            "literal-punctuation",
            "no-punctuation",
            "normal",
            "spell-out",
        ]
        | str
        | None
    )
    src: (
        Literal[
            "enum, url, identifier",
            "url()",
            "format()",
            "local()",
        ]
        | str
        | None
    )
    stop_color: Literal["color",] | str | None
    stop_opacity: Literal["number(0-1)",] | str | None
    stroke: (
        Literal[
            "color, enum, url",
            "child",
            "child()",
            "context-fill",
            "context-stroke",
            "url()",
            "none",
        ]
        | str
        | None
    )
    stroke_dasharray: Literal["length, percentage, number, enum",] | str | None
    stroke_dashoffset: Literal["percentage, length",] | str | None
    stroke_linecap: (
        Literal[
            "enum",
            "butt",
            "round",
            "square",
        ]
        | str
        | None
    )
    stroke_linejoin: (
        Literal[
            "enum",
            "arcs",
            "bevel",
            "miter",
            "miter-clip",
            "round",
        ]
        | str
        | None
    )
    stroke_miterlimit: Literal["number",] | str | None
    stroke_opacity: Literal["number(0-1)",] | str | None
    stroke_width: Literal["percentage, length",] | str | None
    suffix: Literal["image, string, identifier",] | str | None
    symbols: Literal["image, string, identifier",] | str | None
    system: (
        Literal[
            "enum, integer",
            "additive",
            "alphabetic",
            "cyclic",
            "extends",
            "fixed",
            "numeric",
            "symbolic",
        ]
        | str
        | None
    )
    tab_size: Literal["integer, length",] | str | None
    table_layout: (
        Literal[
            "enum",
            "auto",
            "fixed",
        ]
        | str
        | None
    )
    text_align: Literal["string",] | str | None
    text_align_last: (
        Literal[
            "enum",
            "auto",
            "center",
            "end",
            "justify",
            "left",
            "right",
            "start",
        ]
        | str
        | None
    )
    text_anchor: (
        Literal[
            "enum",
            "end",
            "middle",
            "start",
        ]
        | str
        | None
    )
    text_combine_upright: (
        Literal[
            "enum, integer",
            "all",
            "digits",
            "none",
        ]
        | str
        | None
    )
    text_decoration: (
        Literal[
            "enum, color",
            "dashed",
            "dotted",
            "double",
            "line-through",
            "none",
            "overline",
            "solid",
            "underline",
            "wavy",
        ]
        | str
        | None
    )
    text_decoration_color: Literal["color",] | str | None
    text_decoration_line: (
        Literal[
            "enum",
            "line-through",
            "none",
            "overline",
            "underline",
        ]
        | str
        | None
    )
    text_decoration_skip: (
        Literal[
            "enum",
            "box-decoration",
            "ink",
            "none",
            "objects",
            "spaces",
        ]
        | str
        | None
    )
    text_decoration_style: (
        Literal[
            "enum",
            "dashed",
            "dotted",
            "double",
            "none",
            "solid",
            "wavy",
        ]
        | str
        | None
    )
    text_emphasis: Literal["color, string",] | str | None
    text_emphasis_color: Literal["color",] | str | None
    text_emphasis_position: (
        Literal[
            "enum",
            "over",
            "under",
            "left",
            "right",
        ]
        | str
        | None
    )
    text_emphasis_style: Literal["string",] | str | None
    text_indent: Literal["percentage, length",] | str | None
    text_justify: (
        Literal[
            "enum",
            "auto",
            "distribute",
            "distribute-all-lines",
            "inter-character",
            "inter-cluster",
            "inter-ideograph",
            "inter-word",
            "kashida",
            "newspaper",
            "none",
        ]
        | str
        | None
    )
    text_orientation: (
        Literal[
            "enum",
            "mixed",
            "sideways",
            "sideways-left",
            "sideways-right",
            "upright",
            "use-glyph-orientation",
        ]
        | str
        | None
    )
    text_overflow: (
        Literal[
            "enum, string",
            "clip",
            "ellipsis",
        ]
        | str
        | None
    )
    text_rendering: (
        Literal[
            "enum",
            "auto",
            "geometricPrecision",
            "optimizeLegibility",
            "optimizeSpeed",
        ]
        | str
        | None
    )
    text_shadow: Literal["length, color",] | str | None
    text_size_adjust: (
        Literal[
            "enum, percentage",
            "auto",
            "none",
        ]
        | str
        | None
    )
    text_space_collapse: (
        Literal[
            "enum",
            "collapse",
            "discard",
            "preserve",
            "preserve-auto",
            "preserve-trim",
            "preserve-breaks",
            "preserve-spaces",
        ]
        | str
        | None
    )
    text_space_trim: (
        Literal[
            "enum",
            "none",
            "trim-inner",
            "discard-before",
            "discard-after",
        ]
        | str
        | None
    )
    text_spacing: (
        Literal[
            "enum",
            "normal",
            "none",
            "trim-start",
            "space-start",
            "trim-end",
            "space-end",
            "allow-end",
            "trim-adjacent",
            "space-adjacent",
            "no-compress",
            "ideograph-alpha",
            "ideograph-numeric",
            "punctuation",
        ]
        | str
        | None
    )
    text_transform: (
        Literal[
            "enum",
            "capitalize",
            "full-width",
            "lowercase",
            "none",
            "uppercase",
        ]
        | str
        | None
    )
    text_underline_position: (
        Literal[
            "enum",
            "above",
            "auto",
            "below",
            "left",
            "right",
            "under",
        ]
        | str
        | None
    )
    text_wrap: (
        Literal[
            "enum",
            "balance",
            "normal",
            "nowrap",
        ]
        | str
        | None
    )
    top: Literal["length, percentage",] | str | None
    touch_action: (
        Literal[
            "enum",
            "auto",
            "cross-slide-x",
            "cross-slide-y",
            "double-tap-zoom",
            "manipulation",
            "none",
            "pan-x",
            "pan-y",
            "pinch-zoom",
        ]
        | str
        | None
    )
    transform: (
        Literal[
            "enum",
            "matrix()",
            "matrix3d()",
            "none",
            "perspective()",
            "rotate()",
            "rotate3d()",
            "rotateX('angle')",
            "rotateY('angle')",
            "rotateZ('angle')",
            "scale()",
            "scale3d()",
            "scaleX()",
            "scaleY()",
            "scaleZ()",
            "skew()",
            "skewX()",
            "skewY()",
            "translate()",
            "translate3d()",
            "translateX()",
            "translateY()",
            "translateZ()",
        ]
        | str
        | None
    )
    transform_box: (
        Literal[
            "enum",
            "border-box",
            "fill-box",
            "view-box",
        ]
        | str
        | None
    )
    transform_origin: Literal["position, length, percentage",] | str | None
    transform_style: (
        Literal[
            "enum",
            "flat",
            "preserve-3d",
        ]
        | str
        | None
    )
    transition: (
        Literal[
            "time, property, timing-function, enum",
            "all",
            "none",
        ]
        | str
        | None
    )
    transition_delay: Literal["time",] | str | None
    transition_duration: Literal["time",] | str | None
    transition_property: Literal["property",] | str | None
    transition_timing_function: Literal["timing-function",] | str | None
    unicode_bidi: (
        Literal[
            "enum",
            "bidi-override",
            "embed",
            "isolate",
            "isolate-override",
            "normal",
            "plaintext",
        ]
        | str
        | None
    )
    unicode_range: Literal["unicode-range",] | str | None
    user_select: (
        Literal[
            "enum",
            "all",
            "auto",
            "contain",
            "none",
            "text",
        ]
        | str
        | None
    )
    user_zoom: (
        Literal[
            "enum",
            "fixed",
            "zoom",
        ]
        | str
        | None
    )
    vector_effect: (
        Literal[
            "enum",
            "fixed-position",
            "none",
            "non-rotation",
            "non-scaling-size",
            "non-scaling-stroke",
            "screen",
            "viewport",
        ]
        | str
        | None
    )
    vertical_align: Literal["percentage, length",] | str | None
    visibility: (
        Literal[
            "enum",
            "collapse",
            "hidden",
            "visible",
        ]
        | str
        | None
    )
    voice_balance: Literal["number(-100-100)",] | str | None
    voice_duration: Literal["time",] | str | None
    voice_family: Literal["number, string, identifier",] | str | None
    voice_pitch: Literal["percentage, number, frequency, semitones",] | str | None
    voice_range: Literal["percentage, number, frequency, semitones",] | str | None
    voice_rate: Literal["percentage",] | str | None
    voice_stress: (
        Literal[
            "enum",
            "moderate",
            "none",
            "normal",
            "reduced",
            "strong",
        ]
        | str
        | None
    )
    voice_volume: (
        Literal[
            "volume, enum",
            "loud",
            "medium",
            "silent",
            "soft",
            "x-loud",
            "x-soft",
        ]
        | str
        | None
    )
    widows: Literal["integer",] | str | None
    width: Literal["length, percentage",] | str | None
    will_change: (
        Literal[
            "enum, identifier",
            "auto",
            "contents",
            "scroll-position",
        ]
        | str
        | None
    )
    word_break: (
        Literal[
            "enum",
            "break-all",
            "keep-all",
            "normal",
        ]
        | str
        | None
    )
    word_spacing: Literal["length, percentage",] | str | None
    word_wrap: (
        Literal[
            "enum",
            "break-word",
            "normal",
        ]
        | str
        | None
    )
    wrap_after: (
        Literal[
            "enum",
            "auto",
            "avoid",
            "avoid-line",
            "avoid-flex",
            "line",
            "flex",
        ]
        | str
        | None
    )
    wrap_before: (
        Literal[
            "enum",
            "auto",
            "avoid",
            "avoid-line",
            "avoid-flex",
            "line",
            "flex",
        ]
        | str
        | None
    )
    wrap_flow: (
        Literal[
            "enum",
            "auto",
            "both",
            "clear",
            "end",
            "maximum",
            "minimum",
            "start",
        ]
        | str
        | None
    )
    wrap_inside: (
        Literal[
            "enum",
            "auto",
            "avoid",
        ]
        | str
        | None
    )
    wrap_through: (
        Literal[
            "enum",
            "none",
            "wrap",
        ]
        | str
        | None
    )
    writing_mode: (
        Literal[
            "enum",
            "horizontal-tb",
            "sideways-lr",
            "sideways-rl",
            "vertical-lr",
            "vertical-rl",
        ]
        | str
        | None
    )
    x: Literal["length, percentage",] | str | None
    y: Literal["length, percentage",] | str | None
    z_index: Literal["integer",] | str | None
    zoom: Literal["enum, integer, number, percentage",] | str | None


class CSSPropertyTypes:
    _moz_animation = (
        Literal[
            "time, enum, timing-function, identifier, number",
            "alternate",
            "alternate-reverse",
            "backwards",
            "both",
            "forwards",
            "infinite",
            "none",
            "normal",
            "reverse",
        ]
        | str
        | None
    )
    _moz_animation_delay = Literal["time",] | str | None
    _moz_animation_direction = (
        Literal[
            "enum",
            "alternate",
            "alternate-reverse",
            "normal",
            "reverse",
        ]
        | str
        | None
    )
    _moz_animation_duration = Literal["time",] | str | None
    _moz_animation_iteration_count = Literal["number, enum",] | str | None
    _moz_animation_name = Literal["identifier, enum",] | str | None
    _moz_animation_play_state = (
        Literal[
            "enum",
            "paused",
            "running",
        ]
        | str
        | None
    )
    _moz_animation_timing_function = Literal["timing-function",] | str | None
    _moz_appearance = (
        Literal[
            "enum",
            "button",
            "button-arrow-down",
            "button-arrow-next",
            "button-arrow-previous",
            "button-arrow-up",
            "button-bevel",
            "checkbox",
            "checkbox-container",
            "checkbox-label",
            "dialog",
            "groupbox",
            "listbox",
            "menuarrow",
            "menuimage",
            "menuitem",
            "menuitemtext",
            "menulist",
            "menulist-button",
            "menulist-text",
            "menulist-textfield",
            "menupopup",
            "menuradio",
            "menuseparator",
            "-moz-mac-unified-toolbar",
            "-moz-win-borderless-glass",
            "-moz-win-browsertabbar-toolbox",
            "-moz-win-communications-toolbox",
            "-moz-win-glass",
            "-moz-win-media-toolbox",
            "none",
            "progressbar",
            "progresschunk",
            "radio",
            "radio-container",
            "radio-label",
            "radiomenuitem",
            "resizer",
            "resizerpanel",
            "scrollbarbutton-down",
            "scrollbarbutton-left",
            "scrollbarbutton-right",
            "scrollbarbutton-up",
            "scrollbar-small",
            "scrollbartrack-horizontal",
            "scrollbartrack-vertical",
            "separator",
            "spinner",
            "spinner-downbutton",
            "spinner-textfield",
            "spinner-upbutton",
            "statusbar",
            "statusbarpanel",
            "tab",
            "tabpanels",
            "tab-scroll-arrow-back",
            "tab-scroll-arrow-forward",
            "textfield",
            "textfield-multiline",
            "toolbar",
            "toolbox",
            "tooltip",
            "treeheadercell",
            "treeheadersortarrow",
            "treeitem",
            "treetwistyopen",
            "treeview",
            "treewisty",
            "window",
        ]
        | str
        | None
    )
    _moz_backface_visibility = (
        Literal[
            "enum",
            "hidden",
            "visible",
        ]
        | str
        | None
    )
    _moz_background_clip = Literal["box, enum",] | str | None
    _moz_background_inline_policy = (
        Literal[
            "enum",
            "bounding-box",
            "continuous",
            "each-box",
        ]
        | str
        | None
    )
    _moz_background_origin = Literal["box",] | str | None
    _moz_border_bottom_colors = Literal["color",] | str | None
    _moz_border_image = (
        Literal[
            "length, percentage, number, url, enum",
            "auto",
            "fill",
            "none",
            "repeat",
            "round",
            "space",
            "stretch",
            "url()",
        ]
        | str
        | None
    )
    _moz_border_left_colors = Literal["color",] | str | None
    _moz_border_right_colors = Literal["color",] | str | None
    _moz_border_top_colors = Literal["color",] | str | None
    _moz_box_align = (
        Literal[
            "enum",
            "baseline",
            "center",
            "end",
            "start",
            "stretch",
        ]
        | str
        | None
    )
    _moz_box_direction = (
        Literal[
            "enum",
            "normal",
            "reverse",
        ]
        | str
        | None
    )
    _moz_box_flex = Literal["number",] | str | None
    _moz_box_flexgroup = Literal["integer",] | str | None
    _moz_box_ordinal_group = Literal["integer",] | str | None
    _moz_box_orient = (
        Literal[
            "enum",
            "block-axis",
            "horizontal",
            "inline-axis",
            "vertical",
        ]
        | str
        | None
    )
    _moz_box_pack = (
        Literal[
            "enum",
            "center",
            "end",
            "justify",
            "start",
        ]
        | str
        | None
    )
    _moz_box_sizing = (
        Literal[
            "enum",
            "border-box",
            "content-box",
            "padding-box",
        ]
        | str
        | None
    )
    _moz_column_count = Literal["integer",] | str | None
    _moz_column_gap = Literal["length",] | str | None
    _moz_column_rule = Literal["length, line-width, line-style, color",] | str | None
    _moz_column_rule_color = Literal["color",] | str | None
    _moz_column_rule_style = Literal["line-style",] | str | None
    _moz_column_rule_width = Literal["length, line-width",] | str | None
    _moz_column_width = Literal["length",] | str | None
    _moz_columns = Literal["length, integer",] | str | None
    _moz_font_feature_settings = Literal["string, integer",] | str | None
    _moz_hyphens = (
        Literal[
            "enum",
            "auto",
            "manual",
            "none",
        ]
        | str
        | None
    )
    _moz_perspective = Literal["length",] | str | None
    _moz_perspective_origin = Literal["position, percentage, length",] | str | None
    _moz_text_align_last = (
        Literal[
            "enum",
            "auto",
            "center",
            "end",
            "justify",
            "left",
            "right",
            "start",
        ]
        | str
        | None
    )
    _moz_text_decoration_color = Literal["color",] | str | None
    _moz_text_decoration_line = (
        Literal[
            "enum",
            "line-through",
            "none",
            "overline",
            "underline",
        ]
        | str
        | None
    )
    _moz_text_decoration_style = (
        Literal[
            "enum",
            "dashed",
            "dotted",
            "double",
            "none",
            "solid",
            "wavy",
        ]
        | str
        | None
    )
    _moz_text_size_adjust = (
        Literal[
            "enum, percentage",
            "auto",
            "none",
        ]
        | str
        | None
    )
    _moz_transform = (
        Literal[
            "enum",
            "matrix()",
            "matrix3d()",
            "none",
            "perspective",
            "rotate()",
            "rotate3d()",
            "rotateX('angle')",
            "rotateY('angle')",
            "rotateZ('angle')",
            "scale()",
            "scale3d()",
            "scaleX()",
            "scaleY()",
            "scaleZ()",
            "skew()",
            "skewX()",
            "skewY()",
            "translate()",
            "translate3d()",
            "translateX()",
            "translateY()",
            "translateZ()",
        ]
        | str
        | None
    )
    _moz_transform_origin = Literal["position, length, percentage",] | str | None
    _moz_transition = (
        Literal[
            "time, property, timing-function, enum",
            "all",
            "none",
        ]
        | str
        | None
    )
    _moz_transition_delay = Literal["time",] | str | None
    _moz_transition_duration = Literal["time",] | str | None
    _moz_transition_property = Literal["property",] | str | None
    _moz_transition_timing_function = Literal["timing-function",] | str | None
    _moz_user_focus = str | None
    _moz_user_select = (
        Literal[
            "enum",
            "all",
            "element",
            "elements",
            "-moz-all",
            "-moz-none",
            "none",
            "text",
            "toggle",
        ]
        | str
        | None
    )
    _ms_accelerator = (
        Literal[
            "enum",
            "false",
            "true",
        ]
        | str
        | None
    )
    _ms_behavior = Literal["url",] | str | None
    _ms_block_progression = (
        Literal[
            "enum",
            "bt",
            "lr",
            "rl",
            "tb",
        ]
        | str
        | None
    )
    _ms_content_zoom_chaining = str | None
    _ms_content_zoom_limit = Literal["percentage",] | str | None
    _ms_content_zoom_limit_max = Literal["percentage",] | str | None
    _ms_content_zoom_limit_min = Literal["percentage",] | str | None
    _ms_content_zoom_snap = str | None
    _ms_content_zoom_snap_points = str | None
    _ms_content_zoom_snap_type = (
        Literal[
            "enum",
            "mandatory",
            "none",
            "proximity",
        ]
        | str
        | None
    )
    _ms_content_zooming = (
        Literal[
            "enum",
            "none",
            "zoom",
        ]
        | str
        | None
    )
    _ms_filter = Literal["string",] | str | None
    _ms_flex = Literal["length, number, percentage",] | str | None
    _ms_flex_align = (
        Literal[
            "enum",
            "baseline",
            "center",
            "end",
            "start",
            "stretch",
        ]
        | str
        | None
    )
    _ms_flex_direction = (
        Literal[
            "enum",
            "column",
            "column-reverse",
            "row",
            "row-reverse",
        ]
        | str
        | None
    )
    _ms_flex_flow = (
        Literal[
            "enum",
            "column",
            "column-reverse",
            "nowrap",
            "row",
            "wrap",
            "wrap-reverse",
        ]
        | str
        | None
    )
    _ms_flex_item_align = (
        Literal[
            "enum",
            "auto",
            "baseline",
            "center",
            "end",
            "start",
            "stretch",
        ]
        | str
        | None
    )
    _ms_flex_line_pack = (
        Literal[
            "enum",
            "center",
            "distribute",
            "end",
            "justify",
            "start",
            "stretch",
        ]
        | str
        | None
    )
    _ms_flex_order = Literal["integer",] | str | None
    _ms_flex_pack = (
        Literal[
            "enum",
            "center",
            "distribute",
            "end",
            "justify",
            "start",
        ]
        | str
        | None
    )
    _ms_flex_wrap = (
        Literal[
            "enum",
            "nowrap",
            "wrap",
            "wrap-reverse",
        ]
        | str
        | None
    )
    _ms_flow_from = Literal["identifier",] | str | None
    _ms_flow_into = Literal["identifier",] | str | None
    _ms_grid_column = (
        Literal[
            "integer, string, enum",
            "auto",
            "end",
            "start",
        ]
        | str
        | None
    )
    _ms_grid_column_align = (
        Literal[
            "enum",
            "center",
            "end",
            "start",
            "stretch",
        ]
        | str
        | None
    )
    _ms_grid_column_span = Literal["integer",] | str | None
    _ms_grid_columns = str | None
    _ms_grid_layer = Literal["integer",] | str | None
    _ms_grid_row = (
        Literal[
            "integer, string, enum",
            "auto",
            "end",
            "start",
        ]
        | str
        | None
    )
    _ms_grid_row_align = (
        Literal[
            "enum",
            "center",
            "end",
            "start",
            "stretch",
        ]
        | str
        | None
    )
    _ms_grid_row_span = Literal["integer",] | str | None
    _ms_grid_rows = str | None
    _ms_high_contrast_adjust = (
        Literal[
            "enum",
            "auto",
            "none",
        ]
        | str
        | None
    )
    _ms_hyphenate_limit_chars = Literal["integer",] | str | None
    _ms_hyphenate_limit_lines = Literal["integer",] | str | None
    _ms_hyphenate_limit_zone = Literal["percentage, length",] | str | None
    _ms_hyphens = (
        Literal[
            "enum",
            "auto",
            "manual",
            "none",
        ]
        | str
        | None
    )
    _ms_ime_mode = (
        Literal[
            "enum",
            "active",
            "auto",
            "disabled",
            "inactive",
            "normal",
        ]
        | str
        | None
    )
    _ms_interpolation_mode = (
        Literal[
            "enum",
            "bicubic",
            "nearest-neighbor",
        ]
        | str
        | None
    )
    _ms_layout_grid = str | None
    _ms_layout_grid_char = (
        Literal[
            "enum, length, percentage",
            "auto",
            "none",
        ]
        | str
        | None
    )
    _ms_layout_grid_line = Literal["length",] | str | None
    _ms_layout_grid_mode = (
        Literal[
            "enum",
            "both",
            "char",
            "line",
            "none",
        ]
        | str
        | None
    )
    _ms_layout_grid_type = (
        Literal[
            "enum",
            "fixed",
            "loose",
            "strict",
        ]
        | str
        | None
    )
    _ms_line_break = (
        Literal[
            "enum",
            "auto",
            "keep-all",
            "newspaper",
            "normal",
            "strict",
        ]
        | str
        | None
    )
    _ms_overflow_style = (
        Literal[
            "enum",
            "auto",
            "-ms-autohiding-scrollbar",
            "none",
            "scrollbar",
        ]
        | str
        | None
    )
    _ms_perspective = Literal["length",] | str | None
    _ms_perspective_origin = Literal["position, percentage, length",] | str | None
    _ms_perspective_origin_x = Literal["position, percentage, length",] | str | None
    _ms_perspective_origin_y = Literal["position, percentage, length",] | str | None
    _ms_progress_appearance = (
        Literal[
            "enum",
            "bar",
            "ring",
        ]
        | str
        | None
    )
    _ms_scroll_chaining = (
        Literal[
            "enum, length",
            "chained",
            "none",
        ]
        | str
        | None
    )
    _ms_scroll_limit = Literal["length",] | str | None
    _ms_scroll_limit_x_max = Literal["length",] | str | None
    _ms_scroll_limit_x_min = Literal["length",] | str | None
    _ms_scroll_limit_y_max = Literal["length",] | str | None
    _ms_scroll_limit_y_min = Literal["length",] | str | None
    _ms_scroll_rails = (
        Literal[
            "enum, length",
            "none",
            "railed",
        ]
        | str
        | None
    )
    _ms_scroll_snap_points_x = (
        Literal[
            "enum",
            "snapInterval(100%, 100%)",
            "snapList()",
        ]
        | str
        | None
    )
    _ms_scroll_snap_points_y = (
        Literal[
            "enum",
            "snapInterval(100%, 100%)",
            "snapList()",
        ]
        | str
        | None
    )
    _ms_scroll_snap_type = (
        Literal[
            "enum",
            "none",
            "mandatory",
            "proximity",
        ]
        | str
        | None
    )
    _ms_scroll_snap_x = (
        Literal[
            "enum",
            "mandatory",
            "none",
            "proximity",
            "snapInterval(100%, 100%)",
            "snapList()",
        ]
        | str
        | None
    )
    _ms_scroll_snap_y = (
        Literal[
            "enum",
            "mandatory",
            "none",
            "proximity",
            "snapInterval(100%, 100%)",
            "snapList()",
        ]
        | str
        | None
    )
    _ms_scroll_translation = (
        Literal[
            "enum",
            "none",
            "vertical-to-horizontal",
        ]
        | str
        | None
    )
    _ms_scrollbar_3dlight_color = Literal["color",] | str | None
    _ms_scrollbar_arrow_color = Literal["color",] | str | None
    _ms_scrollbar_base_color = Literal["color",] | str | None
    _ms_scrollbar_darkshadow_color = Literal["color",] | str | None
    _ms_scrollbar_face_color = Literal["color",] | str | None
    _ms_scrollbar_highlight_color = Literal["color",] | str | None
    _ms_scrollbar_shadow_color = Literal["color",] | str | None
    _ms_scrollbar_track_color = Literal["color",] | str | None
    _ms_text_align_last = (
        Literal[
            "enum",
            "auto",
            "center",
            "end",
            "justify",
            "left",
            "right",
            "start",
        ]
        | str
        | None
    )
    _ms_text_autospace = (
        Literal[
            "enum",
            "ideograph-alpha",
            "ideograph-numeric",
            "ideograph-parenthesis",
            "ideograph-space",
            "none",
            "punctuation",
        ]
        | str
        | None
    )
    _ms_text_combine_horizontal = (
        Literal[
            "enum, integer",
            "all",
            "digits",
            "none",
        ]
        | str
        | None
    )
    _ms_text_justify = (
        Literal[
            "enum",
            "auto",
            "distribute",
            "inter-cluster",
            "inter-ideograph",
            "inter-word",
            "kashida",
            "none",
            "trim",
        ]
        | str
        | None
    )
    _ms_text_kashida_space = Literal["percentage",] | str | None
    _ms_text_overflow = (
        Literal[
            "enum",
            "clip",
            "ellipsis",
        ]
        | str
        | None
    )
    _ms_text_size_adjust = (
        Literal[
            "enum, percentage",
            "auto",
            "none",
        ]
        | str
        | None
    )
    _ms_text_underline_position = (
        Literal[
            "enum",
            "alphabetic",
            "auto",
            "over",
            "under",
        ]
        | str
        | None
    )
    _ms_touch_action = (
        Literal[
            "enum",
            "auto",
            "double-tap-zoom",
            "manipulation",
            "none",
            "pan-x",
            "pan-y",
            "pinch-zoom",
        ]
        | str
        | None
    )
    _ms_touch_select = (
        Literal[
            "enum",
            "grippers",
            "none",
        ]
        | str
        | None
    )
    _ms_transform = (
        Literal[
            "enum",
            "matrix()",
            "matrix3d()",
            "none",
            "rotate()",
            "rotate3d()",
            "rotateX('angle')",
            "rotateY('angle')",
            "rotateZ('angle')",
            "scale()",
            "scale3d()",
            "scaleX()",
            "scaleY()",
            "scaleZ()",
            "skew()",
            "skewX()",
            "skewY()",
            "translate()",
            "translate3d()",
            "translateX()",
            "translateY()",
            "translateZ()",
        ]
        | str
        | None
    )
    _ms_transform_origin = Literal["position, length, percentage",] | str | None
    _ms_transform_origin_x = Literal["length, percentage",] | str | None
    _ms_transform_origin_y = Literal["length, percentage",] | str | None
    _ms_transform_origin_z = Literal["length, percentage",] | str | None
    _ms_user_select = (
        Literal[
            "enum",
            "element",
            "none",
            "text",
        ]
        | str
        | None
    )
    _ms_word_break = (
        Literal[
            "enum",
            "break-all",
            "keep-all",
            "normal",
        ]
        | str
        | None
    )
    _ms_word_wrap = (
        Literal[
            "enum",
            "break-word",
            "hyphenate",
            "normal",
        ]
        | str
        | None
    )
    _ms_wrap_flow = (
        Literal[
            "enum",
            "auto",
            "both",
            "clear",
            "end",
            "maximum",
            "minimum",
            "start",
        ]
        | str
        | None
    )
    _ms_wrap_margin = Literal["length, percentage",] | str | None
    _ms_wrap_through = (
        Literal[
            "enum",
            "none",
            "wrap",
        ]
        | str
        | None
    )
    _ms_writing_mode = (
        Literal[
            "enum",
            "bt-lr",
            "bt-rl",
            "lr-bt",
            "lr-tb",
            "rl-bt",
            "rl-tb",
            "tb-lr",
            "tb-rl",
        ]
        | str
        | None
    )
    _ms_zoom = Literal["enum, integer, number, percentage",] | str | None
    _ms_zoom_animation = (
        Literal[
            "enum",
            "default",
            "none",
        ]
        | str
        | None
    )
    _o_animation = (
        Literal[
            "time, enum, timing-function, identifier, number",
            "alternate",
            "alternate-reverse",
            "backwards",
            "both",
            "forwards",
            "infinite",
            "none",
            "normal",
            "reverse",
        ]
        | str
        | None
    )
    _o_animation_delay = Literal["time",] | str | None
    _o_animation_direction = (
        Literal[
            "enum",
            "alternate",
            "alternate-reverse",
            "normal",
            "reverse",
        ]
        | str
        | None
    )
    _o_animation_duration = Literal["time",] | str | None
    _o_animation_fill_mode = (
        Literal[
            "enum",
            "backwards",
            "both",
            "forwards",
            "none",
        ]
        | str
        | None
    )
    _o_animation_iteration_count = Literal["number, enum",] | str | None
    _o_animation_name = Literal["identifier, enum",] | str | None
    _o_animation_play_state = (
        Literal[
            "enum",
            "paused",
            "running",
        ]
        | str
        | None
    )
    _o_animation_timing_function = Literal["timing-function",] | str | None
    _o_border_image = (
        Literal[
            "length, percentage, number, image, enum",
            "auto",
            "fill",
            "none",
            "repeat",
            "round",
            "space",
            "stretch",
        ]
        | str
        | None
    )
    _o_object_fit = (
        Literal[
            "enum",
            "contain",
            "cover",
            "fill",
            "none",
            "scale-down",
        ]
        | str
        | None
    )
    _o_object_position = Literal["position, length, percentage",] | str | None
    _o_tab_size = Literal["integer, length",] | str | None
    _o_table_baseline = Literal["integer",] | str | None
    _o_text_overflow = (
        Literal[
            "enum",
            "clip",
            "ellipsis",
        ]
        | str
        | None
    )
    _o_transform = (
        Literal[
            "enum",
            "matrix()",
            "matrix3d()",
            "none",
            "rotate()",
            "rotate3d()",
            "rotateX('angle')",
            "rotateY('angle')",
            "rotateZ('angle')",
            "scale()",
            "scale3d()",
            "scaleX()",
            "scaleY()",
            "scaleZ()",
            "skew()",
            "skewX()",
            "skewY()",
            "translate()",
            "translate3d()",
            "translateX()",
            "translateY()",
            "translateZ()",
        ]
        | str
        | None
    )
    _o_transform_origin = Literal["positon, length, percentage",] | str | None
    _o_transition = (
        Literal[
            "time, property, timing-function, enum",
            "all",
            "none",
        ]
        | str
        | None
    )
    _o_transition_delay = Literal["time",] | str | None
    _o_transition_duration = Literal["time",] | str | None
    _o_transition_property = Literal["property",] | str | None
    _o_transition_timing_function = Literal["timing-function",] | str | None
    _webkit_animation = (
        Literal[
            "time, enum, timing-function, identifier, number",
            "alternate",
            "alternate-reverse",
            "backwards",
            "both",
            "forwards",
            "infinite",
            "none",
            "normal",
            "reverse",
        ]
        | str
        | None
    )
    _webkit_animation_delay = Literal["time",] | str | None
    _webkit_animation_direction = (
        Literal[
            "enum",
            "alternate",
            "alternate-reverse",
            "normal",
            "reverse",
        ]
        | str
        | None
    )
    _webkit_animation_duration = Literal["time",] | str | None
    _webkit_animation_fill_mode = (
        Literal[
            "enum",
            "backwards",
            "both",
            "forwards",
            "none",
        ]
        | str
        | None
    )
    _webkit_animation_iteration_count = Literal["number, enum",] | str | None
    _webkit_animation_name = Literal["identifier, enum",] | str | None
    _webkit_animation_play_state = (
        Literal[
            "enum",
            "paused",
            "running",
        ]
        | str
        | None
    )
    _webkit_animation_timing_function = Literal["timing-function",] | str | None
    _webkit_appearance = (
        Literal[
            "enum",
            "button",
            "button-bevel",
            "caps-lock-indicator",
            "caret",
            "checkbox",
            "default-button",
            "listbox",
            "listitem",
            "media-fullscreen-button",
            "media-mute-button",
            "media-play-button",
            "media-seek-back-button",
            "media-seek-forward-button",
            "media-slider",
            "media-sliderthumb",
            "menulist",
            "menulist-button",
            "menulist-text",
            "menulist-textfield",
            "none",
            "push-button",
            "radio",
            "scrollbarbutton-down",
            "scrollbarbutton-left",
            "scrollbarbutton-right",
            "scrollbarbutton-up",
            "scrollbargripper-horizontal",
            "scrollbargripper-vertical",
            "scrollbarthumb-horizontal",
            "scrollbarthumb-vertical",
            "scrollbartrack-horizontal",
            "scrollbartrack-vertical",
            "searchfield",
            "searchfield-cancel-button",
            "searchfield-decoration",
            "searchfield-results-button",
            "searchfield-results-decoration",
            "slider-horizontal",
            "sliderthumb-horizontal",
            "sliderthumb-vertical",
            "slider-vertical",
            "square-button",
            "textarea",
            "textfield",
        ]
        | str
        | None
    )
    _webkit_backdrop_filter = (
        Literal[
            "enum, url",
            "none",
            "blur()",
            "brightness()",
            "contrast()",
            "drop-shadow()",
            "grayscale()",
            "hue-rotate()",
            "invert()",
            "opacity()",
            "saturate()",
            "sepia()",
            "url()",
        ]
        | str
        | None
    )
    _webkit_backface_visibility = (
        Literal[
            "enum",
            "hidden",
            "visible",
        ]
        | str
        | None
    )
    _webkit_background_clip = Literal["box",] | str | None
    _webkit_background_composite = (
        Literal[
            "enum",
            "border",
            "padding",
        ]
        | str
        | None
    )
    _webkit_background_origin = Literal["box",] | str | None
    _webkit_border_image = (
        Literal[
            "length, percentage, number, url, enum",
            "auto",
            "fill",
            "none",
            "repeat",
            "round",
            "space",
            "stretch",
            "url()",
        ]
        | str
        | None
    )
    _webkit_box_align = (
        Literal[
            "enum",
            "baseline",
            "center",
            "end",
            "start",
            "stretch",
        ]
        | str
        | None
    )
    _webkit_box_direction = (
        Literal[
            "enum",
            "normal",
            "reverse",
        ]
        | str
        | None
    )
    _webkit_box_flex = Literal["number",] | str | None
    _webkit_box_flex_group = Literal["integer",] | str | None
    _webkit_box_ordinal_group = Literal["integer",] | str | None
    _webkit_box_orient = (
        Literal[
            "enum",
            "block-axis",
            "horizontal",
            "inline-axis",
            "vertical",
        ]
        | str
        | None
    )
    _webkit_box_pack = (
        Literal[
            "enum",
            "center",
            "end",
            "justify",
            "start",
        ]
        | str
        | None
    )
    _webkit_box_reflect = str | None
    _webkit_box_sizing = (
        Literal[
            "enum",
            "border-box",
            "content-box",
        ]
        | str
        | None
    )
    _webkit_break_after = (
        Literal[
            "enum",
            "always",
            "auto",
            "avoid",
            "avoid-column",
            "avoid-page",
            "avoid-region",
            "column",
            "left",
            "page",
            "region",
            "right",
        ]
        | str
        | None
    )
    _webkit_break_before = (
        Literal[
            "enum",
            "always",
            "auto",
            "avoid",
            "avoid-column",
            "avoid-page",
            "avoid-region",
            "column",
            "left",
            "page",
            "region",
            "right",
        ]
        | str
        | None
    )
    _webkit_break_inside = (
        Literal[
            "enum",
            "auto",
            "avoid",
            "avoid-column",
            "avoid-page",
            "avoid-region",
        ]
        | str
        | None
    )
    _webkit_column_break_after = (
        Literal[
            "enum",
            "always",
            "auto",
            "avoid",
            "avoid-column",
            "avoid-page",
            "avoid-region",
            "column",
            "left",
            "page",
            "region",
            "right",
        ]
        | str
        | None
    )
    _webkit_column_break_before = (
        Literal[
            "enum",
            "always",
            "auto",
            "avoid",
            "avoid-column",
            "avoid-page",
            "avoid-region",
            "column",
            "left",
            "page",
            "region",
            "right",
        ]
        | str
        | None
    )
    _webkit_column_break_inside = (
        Literal[
            "enum",
            "auto",
            "avoid",
            "avoid-column",
            "avoid-page",
            "avoid-region",
        ]
        | str
        | None
    )
    _webkit_column_count = Literal["integer",] | str | None
    _webkit_column_gap = Literal["length",] | str | None
    _webkit_column_rule = Literal["length, line-width, line-style, color",] | str | None
    _webkit_column_rule_color = Literal["color",] | str | None
    _webkit_column_rule_style = Literal["line-style",] | str | None
    _webkit_column_rule_width = Literal["length, line-width",] | str | None
    _webkit_column_span = (
        Literal[
            "enum",
            "all",
            "none",
        ]
        | str
        | None
    )
    _webkit_column_width = Literal["length",] | str | None
    _webkit_columns = Literal["length, integer",] | str | None
    _webkit_filter = (
        Literal[
            "enum, url",
            "none",
            "blur()",
            "brightness()",
            "contrast()",
            "drop-shadow()",
            "grayscale()",
            "hue-rotate()",
            "invert()",
            "opacity()",
            "saturate()",
            "sepia()",
            "url()",
        ]
        | str
        | None
    )
    _webkit_flow_from = Literal["identifier",] | str | None
    _webkit_flow_into = Literal["identifier",] | str | None
    _webkit_font_feature_settings = Literal["string, integer",] | str | None
    _webkit_hyphens = (
        Literal[
            "enum",
            "auto",
            "manual",
            "none",
        ]
        | str
        | None
    )
    _webkit_line_break = str | None
    _webkit_margin_bottom_collapse = (
        Literal[
            "enum",
            "collapse",
            "discard",
            "separate",
        ]
        | str
        | None
    )
    _webkit_margin_collapse = (
        Literal[
            "enum",
            "collapse",
            "discard",
            "separate",
        ]
        | str
        | None
    )
    _webkit_margin_start = Literal["percentage, length",] | str | None
    _webkit_margin_top_collapse = (
        Literal[
            "enum",
            "collapse",
            "discard",
            "separate",
        ]
        | str
        | None
    )
    _webkit_mask_clip = Literal["box",] | str | None
    _webkit_mask_image = (
        Literal[
            "url, image, enum",
            "none",
            "url()",
        ]
        | str
        | None
    )
    _webkit_mask_origin = Literal["box",] | str | None
    _webkit_mask_repeat = Literal["repeat",] | str | None
    _webkit_mask_size = (
        Literal[
            "length, percentage, enum",
            "auto",
            "contain",
            "cover",
        ]
        | str
        | None
    )
    _webkit_nbsp_mode = str | None
    _webkit_overflow_scrolling = str | None
    _webkit_padding_start = Literal["percentage, length",] | str | None
    _webkit_perspective = Literal["length",] | str | None
    _webkit_perspective_origin = Literal["position, percentage, length",] | str | None
    _webkit_region_fragment = (
        Literal[
            "enum",
            "auto",
            "break",
        ]
        | str
        | None
    )
    _webkit_tap_highlight_color = Literal["color",] | str | None
    _webkit_text_fill_color = Literal["color",] | str | None
    _webkit_text_size_adjust = Literal["percentage",] | str | None
    _webkit_text_stroke = Literal["length, line-width, color, percentage",] | str | None
    _webkit_text_stroke_color = Literal["color",] | str | None
    _webkit_text_stroke_width = Literal["length, line-width, percentage",] | str | None
    _webkit_touch_callout = Literal["enum",] | str | None
    _webkit_transform = (
        Literal[
            "enum",
            "matrix()",
            "matrix3d()",
            "none",
            "perspective()",
            "rotate()",
            "rotate3d()",
            "rotateX('angle')",
            "rotateY('angle')",
            "rotateZ('angle')",
            "scale()",
            "scale3d()",
            "scaleX()",
            "scaleY()",
            "scaleZ()",
            "skew()",
            "skewX()",
            "skewY()",
            "translate()",
            "translate3d()",
            "translateX()",
            "translateY()",
            "translateZ()",
        ]
        | str
        | None
    )
    _webkit_transform_origin = Literal["position, length, percentage",] | str | None
    _webkit_transform_origin_x = Literal["length, percentage",] | str | None
    _webkit_transform_origin_y = Literal["length, percentage",] | str | None
    _webkit_transform_origin_z = Literal["length, percentage",] | str | None
    _webkit_transform_style = (
        Literal[
            "enum",
            "flat",
            "preserve-3d",
        ]
        | str
        | None
    )
    _webkit_transition = (
        Literal[
            "time, property, timing-function, enum",
            "all",
            "none",
        ]
        | str
        | None
    )
    _webkit_transition_delay = Literal["time",] | str | None
    _webkit_transition_duration = Literal["time",] | str | None
    _webkit_transition_property = Literal["property",] | str | None
    _webkit_transition_timing_function = Literal["timing-function",] | str | None
    _webkit_user_drag = (
        Literal[
            "enum",
            "auto",
            "element",
            "none",
        ]
        | str
        | None
    )
    _webkit_user_modify = (
        Literal[
            "enum",
            "read-only",
            "read-write",
            "read-write-plaintext-only",
        ]
        | str
        | None
    )
    _webkit_user_select = (
        Literal[
            "enum",
            "auto",
            "none",
            "text",
        ]
        | str
        | None
    )
    additive_symbols = Literal["integer, string, image, identifier",] | str | None
    align_content = (
        Literal[
            "enum",
            "center",
            "flex-end",
            "flex-start",
            "space-around",
            "space-between",
            "stretch",
            "start",
            "end",
            "normal",
            "baseline",
            "first baseline",
            "last baseline",
            "space-around",
            "space-between",
            "space-evenly",
            "stretch",
            "safe",
            "unsafe",
        ]
        | str
        | None
    )
    align_items = (
        Literal[
            "enum",
            "baseline",
            "center",
            "flex-end",
            "flex-start",
            "stretch",
            "normal",
            "start",
            "end",
            "self-start",
            "self-end",
            "first baseline",
            "last baseline",
            "stretch",
            "safe",
            "unsafe",
        ]
        | str
        | None
    )
    align_self = (
        Literal[
            "enum",
            "auto",
            "normal",
            "self-end",
            "self-start",
            "baseline",
            "center",
            "flex-end",
            "flex-start",
            "stretch",
            "baseline",
            "first baseline",
            "last baseline",
            "safe",
            "unsafe",
        ]
        | str
        | None
    )
    alignment_baseline = (
        Literal[
            "enum",
            "alphabetic",
            "baseline",
            "bottom",
            "center",
            "central",
            "mathematical",
            "middle",
            "text-bottom",
            "text-top",
            "top",
        ]
        | str
        | None
    )
    all = Literal["enum",] | str | None
    alt = Literal["string, enum",] | str | None
    animation = (
        Literal[
            "time, timing-function, enum, identifier, number",
            "alternate",
            "alternate-reverse",
            "backwards",
            "both",
            "forwards",
            "infinite",
            "none",
            "normal",
            "reverse",
        ]
        | str
        | None
    )
    animation_composition = (
        Literal[
            "enum",
            "accumulate",
            "add",
            "replace",
        ]
        | str
        | None
    )
    animation_delay = Literal["time",] | str | None
    animation_direction = (
        Literal[
            "enum",
            "alternate",
            "alternate-reverse",
            "normal",
            "reverse",
        ]
        | str
        | None
    )
    animation_duration = Literal["time",] | str | None
    animation_fill_mode = (
        Literal[
            "enum",
            "backwards",
            "both",
            "forwards",
            "none",
        ]
        | str
        | None
    )
    animation_iteration_count = Literal["number, enum",] | str | None
    animation_name = Literal["identifier, enum",] | str | None
    animation_play_state = (
        Literal[
            "enum",
            "paused",
            "running",
        ]
        | str
        | None
    )
    animation_timing_function = Literal["timing-function",] | str | None
    backdrop_filter = (
        Literal[
            "enum, url",
            "none",
            "blur()",
            "brightness()",
            "contrast()",
            "drop-shadow()",
            "grayscale()",
            "hue-rotate()",
            "invert()",
            "opacity()",
            "saturate()",
            "sepia()",
            "url()",
        ]
        | str
        | None
    )
    backface_visibility = (
        Literal[
            "enum",
            "hidden",
            "visible",
        ]
        | str
        | None
    )
    background = (
        Literal[
            "enum, image, color, position, length, repeat, percentage, box",
            "fixed",
            "local",
            "none",
            "scroll",
        ]
        | str
        | None
    )
    background_attachment = (
        Literal[
            "enum",
            "fixed",
            "local",
            "scroll",
        ]
        | str
        | None
    )
    background_blend_mode = (
        Literal[
            "enum",
            "normal",
            "multiply",
            "screen",
            "overlay",
            "darken",
            "lighten",
            "color-dodge",
            "color-burn",
            "hard-light",
            "soft-light",
            "difference",
            "exclusion",
            "hue",
            "saturation",
            "color",
            "luminosity",
        ]
        | str
        | None
    )
    background_clip = Literal["box",] | str | None
    background_color = Literal["color",] | str | None
    background_image = Literal["image, enum",] | str | None
    background_image_transform = (
        Literal[
            "enum",
            "logical",
            "physical",
            "rotate",
        ]
        | str
        | None
    )
    background_origin = Literal["box",] | str | None
    background_position = Literal["position, length, percentage",] | str | None
    background_position_x = Literal["length, percentage",] | str | None
    background_position_y = Literal["length, percentage",] | str | None
    background_repeat = Literal["repeat",] | str | None
    background_size = Literal["length, percentage",] | str | None
    baseline_shift = (
        Literal[
            "length, percentage, enum",
            "sub",
            "super",
        ]
        | str
        | None
    )
    behavior = Literal["url",] | str | None
    block_size = Literal["length, percentage",] | str | None
    border = Literal["length, line-width, line-style, color",] | str | None
    border_block_end = Literal["length, line-width, line-style, color",] | str | None
    border_block_end_color = Literal["color",] | str | None
    border_block_end_style = Literal["line-style",] | str | None
    border_block_end_width = Literal["length, line-width",] | str | None
    border_block_start = Literal["length, line-width, line-style, color",] | str | None
    border_block_start_color = Literal["color",] | str | None
    border_block_start_style = Literal["line-style",] | str | None
    border_block_start_width = Literal["length, line-width",] | str | None
    border_bottom = Literal["length, line-width, line-style, color",] | str | None
    border_bottom_color = Literal["color",] | str | None
    border_bottom_left_radius = Literal["length, percentage",] | str | None
    border_bottom_right_radius = Literal["length, percentage",] | str | None
    border_bottom_style = Literal["line-style",] | str | None
    border_bottom_width = Literal["length, line-width",] | str | None
    border_collapse = (
        Literal[
            "enum",
            "collapse",
            "separate",
        ]
        | str
        | None
    )
    border_color = Literal["color",] | str | None
    border_image = (
        Literal[
            "length, percentage, number, url, enum",
            "auto",
            "fill",
            "none",
            "repeat",
            "round",
            "space",
            "stretch",
            "url()",
        ]
        | str
        | None
    )
    border_image_outset = Literal["length, number",] | str | None
    border_image_repeat = (
        Literal[
            "enum",
            "repeat",
            "round",
            "space",
            "stretch",
        ]
        | str
        | None
    )
    border_image_slice = Literal["number, percentage",] | str | None
    border_image_source = Literal["image",] | str | None
    border_image_transform = (
        Literal[
            "enum",
            "logical",
            "physical",
            "rotate",
        ]
        | str
        | None
    )
    border_image_width = Literal["length, percentage, number",] | str | None
    border_inline_end = Literal["length, line-width, line-style, color",] | str | None
    border_inline_end_color = Literal["color",] | str | None
    border_inline_end_style = Literal["line-style",] | str | None
    border_inline_end_width = Literal["length, line-width",] | str | None
    border_inline_start = Literal["length, line-width, line-style, color",] | str | None
    border_inline_start_color = Literal["color",] | str | None
    border_inline_start_style = Literal["line-style",] | str | None
    border_inline_start_width = Literal["length, line-width",] | str | None
    border_left = Literal["length, line-width, line-style, color",] | str | None
    border_left_color = Literal["color",] | str | None
    border_left_style = Literal["line-style",] | str | None
    border_left_width = Literal["length, line-width",] | str | None
    border_radius = Literal["length, percentage",] | str | None
    border_right = Literal["length, line-width, line-style, color",] | str | None
    border_right_color = Literal["color",] | str | None
    border_right_style = Literal["line-style",] | str | None
    border_right_width = Literal["length, line-width",] | str | None
    border_spacing = Literal["length",] | str | None
    border_style = Literal["line-style",] | str | None
    border_top = Literal["length, line-width, line-style, color",] | str | None
    border_top_color = Literal["color",] | str | None
    border_top_left_radius = Literal["length, percentage",] | str | None
    border_top_right_radius = Literal["length, percentage",] | str | None
    border_top_style = Literal["line-style",] | str | None
    border_top_width = Literal["length, line-width",] | str | None
    border_width = Literal["length, line-width",] | str | None
    bottom = Literal["length, percentage",] | str | None
    box_decoration_break = (
        Literal[
            "enum",
            "clone",
            "slice",
        ]
        | str
        | None
    )
    box_shadow = (
        Literal[
            "length, color, enum",
            "inset",
            "none",
        ]
        | str
        | None
    )
    box_sizing = (
        Literal[
            "enum",
            "border-box",
            "content-box",
        ]
        | str
        | None
    )
    box_snap = (
        Literal[
            "enum",
            "none",
            "block-start",
            "block-end",
            "center",
            "baseline",
            "last-baseline",
        ]
        | str
        | None
    )
    box_suppress = (
        Literal[
            "enum",
            "show",
            "discard",
            "hide",
        ]
        | str
        | None
    )
    break_after = (
        Literal[
            "enum",
            "always",
            "auto",
            "avoid",
            "avoid-column",
            "avoid-page",
            "avoid-region",
            "column",
            "left",
            "page",
            "region",
            "right",
            "recto",
            "verso",
        ]
        | str
        | None
    )
    break_before = (
        Literal[
            "enum",
            "always",
            "auto",
            "avoid",
            "avoid-column",
            "avoid-page",
            "avoid-region",
            "column",
            "left",
            "page",
            "region",
            "right",
            "recto",
            "verso",
        ]
        | str
        | None
    )
    break_inside = (
        Literal[
            "enum",
            "auto",
            "avoid",
            "avoid-column",
            "avoid-page",
            "avoid-region",
        ]
        | str
        | None
    )
    caption_side = (
        Literal[
            "enum",
            "block-end",
            "block-start",
            "bottom",
            "inline-end",
            "inline-start",
            "top",
        ]
        | str
        | None
    )
    caret_color = Literal["color, enum",] | str | None
    clear = (
        Literal[
            "enum",
            "both",
            "inline-end",
            "inline-start",
            "left",
            "none",
            "right",
        ]
        | str
        | None
    )
    clip = (
        Literal[
            "enum",
            "auto",
            "rect()",
        ]
        | str
        | None
    )
    clip_path = (
        Literal[
            "url, shape, geometry-box, enum",
            "none",
            "url()",
        ]
        | str
        | None
    )
    clip_rule = (
        Literal[
            "enum",
            "evenodd",
            "nonzero",
        ]
        | str
        | None
    )
    color = Literal["color",] | str | None
    color_adjust = (
        Literal[
            "enum",
            "economy",
            "exact",
        ]
        | str
        | None
    )
    color_interpolation = (
        Literal[
            "enum",
            "auto",
            "linearRGB",
            "sRGB",
        ]
        | str
        | None
    )
    color_interpolation_filters = (
        Literal[
            "enum",
            "auto",
            "linearRGB",
            "sRGB",
        ]
        | str
        | None
    )
    color_rendering = (
        Literal[
            "enum",
            "auto",
            "optimizeQuality",
            "optimizeSpeed",
        ]
        | str
        | None
    )
    column_count = Literal["integer, enum",] | str | None
    column_fill = (
        Literal[
            "enum",
            "auto",
            "balance",
        ]
        | str
        | None
    )
    column_gap = Literal["length, enum",] | str | None
    column_rule = Literal["length, line-width, line-style, color",] | str | None
    column_rule_color = Literal["color",] | str | None
    column_rule_style = Literal["line-style",] | str | None
    column_rule_width = Literal["length, line-width",] | str | None
    column_span = (
        Literal[
            "enum",
            "all",
            "none",
        ]
        | str
        | None
    )
    column_width = (
        Literal[
            "length, enum",
            "auto",
            "fill",
            "fit-content",
            "max-content",
            "min-content",
        ]
        | str
        | None
    )
    columns = Literal["length, integer, enum",] | str | None
    contain = (
        Literal[
            "enum",
            "none",
            "strict",
            "content",
            "size",
            "layout",
            "style",
            "paint",
        ]
        | str
        | None
    )
    content = Literal["string, url",] | str | None
    counter_increment = Literal["identifier, integer",] | str | None
    counter_reset = Literal["identifier, integer",] | str | None
    crop = (
        Literal[
            "enum",
            "auto",
            "insert-rect(top, right, bottom, left)",
            "rect(top, right, bottom, left)",
        ]
        | str
        | None
    )
    cue = (
        Literal[
            "url, volume, enum",
            "none",
            "url()",
        ]
        | str
        | None
    )
    cue_after = (
        Literal[
            "url, volume, enum",
            "none",
            "url()",
        ]
        | str
        | None
    )
    cue_before = (
        Literal[
            "url, volume, enum",
            "none",
            "url()",
        ]
        | str
        | None
    )
    cursor = (
        Literal[
            "url, number, enum",
            "alias",
            "all-scroll",
            "auto",
            "cell",
            "col-resize",
            "context-menu",
            "copy",
            "crosshair",
            "default",
            "e-resize",
            "ew-resize",
            "grab",
            "grabbing",
            "help",
            "move",
            "-moz-grab",
            "-moz-grabbing",
            "-moz-zoom-in",
            "-moz-zoom-out",
            "ne-resize",
            "nesw-resize",
            "no-drop",
            "none",
            "not-allowed",
            "n-resize",
            "ns-resize",
            "nw-resize",
            "nwse-resize",
            "pointer",
            "progress",
            "row-resize",
            "se-resize",
            "s-resize",
            "sw-resize",
            "text",
            "vertical-text",
            "wait",
            "-webkit-grab",
            "-webkit-grabbing",
            "-webkit-zoom-in",
            "-webkit-zoom-out",
            "w-resize",
            "zoom-in",
            "zoom-out",
        ]
        | str
        | None
    )
    cx = Literal["length, percentage",] | str | None
    cy = Literal["length, percentage",] | str | None
    direction = (
        Literal[
            "enum",
            "ltr",
            "rtl",
        ]
        | str
        | None
    )
    display = (
        Literal[
            "enum",
            "block",
            "contents",
            "flex",
            "flexbox",
            "flow",
            "flow-root",
            "grid",
            "inline",
            "inline-block",
            "inline-flex",
            "inline-flexbox",
            "inline-grid",
            "inline-table",
            "list-item",
            "-moz-box",
            "-moz-deck",
            "-moz-grid",
            "-moz-grid-group",
            "-moz-grid-line",
            "-moz-groupbox",
            "-moz-inline-box",
            "-moz-inline-grid",
            "-moz-inline-stack",
            "-moz-marker",
            "-moz-popup",
            "-moz-stack",
            "-ms-flexbox",
            "-ms-grid",
            "-ms-inline-flexbox",
            "-ms-inline-grid",
            "none",
            "ruby",
            "ruby-base",
            "ruby-base-container",
            "ruby-base-group",
            "ruby-text",
            "ruby-text-container",
            "ruby-text-group",
            "run-in",
            "table",
            "table-caption",
            "table-cell",
            "table-column",
            "table-column-group",
            "table-footer-group",
            "table-header-group",
            "table-row",
            "table-row-group",
            "-webkit-box",
            "-webkit-flex",
            "-webkit-inline-box",
            "-webkit-inline-flex",
        ]
        | str
        | None
    )
    dominant_baseline = (
        Literal[
            "enum",
            "auto",
            "text-bottom",
            "alphabetic",
            "central",
            "mathematical",
            "hanging",
            "text-top",
        ]
        | str
        | None
    )
    empty_cells = (
        Literal[
            "enum",
            "hide",
            "-moz-show-background",
            "show",
        ]
        | str
        | None
    )
    enable_background = (
        Literal[
            "integer, length, percentage, enum",
            "accumulate",
            "new",
        ]
        | str
        | None
    )
    fallback = Literal["identifier",] | str | None
    fill = (
        Literal[
            "color, enum, url",
            "child",
            "child()",
            "context-fill",
            "context-stroke",
            "url()",
            "none",
        ]
        | str
        | None
    )
    fill_opacity = Literal["number(0-1)",] | str | None
    fill_rule = (
        Literal[
            "enum",
            "evenodd",
            "nonzero",
        ]
        | str
        | None
    )
    filter = (
        Literal[
            "enum, url",
            "none",
            "blur()",
            "brightness()",
            "contrast()",
            "drop-shadow()",
            "grayscale()",
            "hue-rotate()",
            "invert()",
            "opacity()",
            "saturate()",
            "sepia()",
            "url()",
        ]
        | str
        | None
    )
    flex = Literal["length, number, percentage",] | str | None
    flex_basis = Literal["length, number, percentage",] | str | None
    flex_direction = (
        Literal[
            "enum",
            "column",
            "column-reverse",
            "row",
            "row-reverse",
        ]
        | str
        | None
    )
    flex_flow = (
        Literal[
            "enum",
            "column",
            "column-reverse",
            "nowrap",
            "row",
            "row-reverse",
            "wrap",
            "wrap-reverse",
        ]
        | str
        | None
    )
    flex_grow = Literal["number",] | str | None
    flex_shrink = Literal["number",] | str | None
    flex_wrap = (
        Literal[
            "enum",
            "nowrap",
            "wrap",
            "wrap-reverse",
        ]
        | str
        | None
    )
    float = (
        Literal[
            "enum",
            "inline-end",
            "inline-start",
            "left",
            "none",
            "right",
        ]
        | str
        | None
    )
    flood_color = Literal["color",] | str | None
    flood_opacity = Literal["number(0-1), percentage",] | str | None
    flow_from = Literal["identifier",] | str | None
    flow_into = Literal["identifier",] | str | None
    font = Literal["font",] | str | None
    font_family = Literal["font",] | str | None
    font_feature_settings = Literal["string, integer",] | str | None
    font_kerning = (
        Literal[
            "enum",
            "auto",
            "none",
            "normal",
        ]
        | str
        | None
    )
    font_language_override = Literal["string",] | str | None
    font_size = Literal["length, percentage",] | str | None
    font_size_adjust = Literal["number",] | str | None
    font_stretch = (
        Literal[
            "enum",
            "condensed",
            "expanded",
            "extra-condensed",
            "extra-expanded",
            "narrower",
            "normal",
            "semi-condensed",
            "semi-expanded",
            "ultra-condensed",
            "ultra-expanded",
            "wider",
        ]
        | str
        | None
    )
    font_style = (
        Literal[
            "enum",
            "italic",
            "normal",
            "oblique",
        ]
        | str
        | None
    )
    font_synthesis = (
        Literal[
            "enum",
            "none",
            "style",
            "weight",
        ]
        | str
        | None
    )
    font_variant = (
        Literal[
            "enum",
            "normal",
            "small-caps",
        ]
        | str
        | None
    )
    font_variant_alternates = (
        Literal[
            "enum",
            "annotation()",
            "character-variant()",
            "historical-forms",
            "normal",
            "ornaments()",
            "styleset()",
            "stylistic()",
            "swash()",
        ]
        | str
        | None
    )
    font_variant_caps = (
        Literal[
            "enum",
            "all-petite-caps",
            "all-small-caps",
            "normal",
            "petite-caps",
            "small-caps",
            "titling-caps",
            "unicase",
        ]
        | str
        | None
    )
    font_variant_east_asian = (
        Literal[
            "enum",
            "full-width",
            "jis04",
            "jis78",
            "jis83",
            "jis90",
            "normal",
            "proportional-width",
            "ruby",
            "simplified",
            "traditional",
        ]
        | str
        | None
    )
    font_variant_ligatures = (
        Literal[
            "enum",
            "additional-ligatures",
            "common-ligatures",
            "contextual",
            "discretionary-ligatures",
            "historical-ligatures",
            "no-additional-ligatures",
            "no-common-ligatures",
            "no-contextual",
            "no-discretionary-ligatures",
            "no-historical-ligatures",
            "none",
            "normal",
        ]
        | str
        | None
    )
    font_variant_numeric = (
        Literal[
            "enum",
            "diagonal-fractions",
            "lining-nums",
            "normal",
            "oldstyle-nums",
            "ordinal",
            "proportional-nums",
            "slashed-zero",
            "stacked-fractions",
            "tabular-nums",
        ]
        | str
        | None
    )
    font_variant_position = (
        Literal[
            "enum",
            "normal",
            "sub",
            "super",
        ]
        | str
        | None
    )
    font_weight = (
        Literal[
            "enum",
            "100",
            "200",
            "300",
            "400",
            "500",
            "600",
            "700",
            "800",
            "900",
            "bold",
            "bolder",
            "lighter",
            "normal",
        ]
        | str
        | None
    )
    glyph_orientation_horizontal = Literal["angle, number",] | str | None
    glyph_orientation_vertical = Literal["angle, number, enum",] | str | None
    grid = Literal["identifier, length, percentage, string, enum",] | str | None
    grid_area = Literal["identifier, integer",] | str | None
    grid_auto_columns = Literal["length, percentage",] | str | None
    grid_auto_flow = (
        Literal[
            "enum",
            "row",
            "column",
            "dense",
        ]
        | str
        | None
    )
    grid_auto_rows = Literal["length, percentage",] | str | None
    grid_column = (
        Literal[
            "identifier, integer, enum",
            "auto",
            "span",
        ]
        | str
        | None
    )
    grid_column_end = (
        Literal[
            "identifier, integer, enum",
            "auto",
            "span",
        ]
        | str
        | None
    )
    grid_column_gap = Literal["length",] | str | None
    grid_column_start = (
        Literal[
            "identifier, integer, enum",
            "auto",
            "span",
        ]
        | str
        | None
    )
    grid_gap = Literal["length",] | str | None
    grid_row = (
        Literal[
            "identifier, integer, enum",
            "auto",
            "span",
        ]
        | str
        | None
    )
    grid_row_end = (
        Literal[
            "identifier, integer, enum",
            "auto",
            "span",
        ]
        | str
        | None
    )
    grid_row_gap = Literal["length",] | str | None
    grid_row_start = (
        Literal[
            "identifier, integer, enum",
            "auto",
            "span",
        ]
        | str
        | None
    )
    grid_template = (
        Literal[
            "identifier, length, percentage, string, enum",
            "none",
            "min-content",
            "max-content",
            "auto",
            "subgrid",
            "minmax()",
            "repeat()",
        ]
        | str
        | None
    )
    grid_template_areas = Literal["string",] | str | None
    grid_template_columns = (
        Literal[
            "identifier, length, percentage, enum",
            "none",
            "min-content",
            "max-content",
            "auto",
            "subgrid",
            "minmax()",
            "repeat()",
        ]
        | str
        | None
    )
    grid_template_rows = (
        Literal[
            "identifier, length, percentage, string, enum",
            "none",
            "min-content",
            "max-content",
            "auto",
            "subgrid",
            "minmax()",
            "repeat()",
        ]
        | str
        | None
    )
    hanging_punctuation = (
        Literal[
            "enum",
            "allow-end",
            "first",
            "force-end",
            "last",
            "none",
        ]
        | str
        | None
    )
    height = Literal["length, percentage",] | str | None
    hyphenate_character = Literal["string, enum",] | str | None
    hyphenate_limit_chars = Literal["integer, enum",] | str | None
    hyphenate_limit_last = (
        Literal[
            "enum",
            "none",
            "always",
            "column",
            "page",
            "spread",
        ]
        | str
        | None
    )
    hyphenate_limit_lines = Literal["integer",] | str | None
    hyphenate_limit_zone = Literal["percentage, length",] | str | None
    hyphens = (
        Literal[
            "enum",
            "auto",
            "manual",
            "none",
        ]
        | str
        | None
    )
    image_orientation = Literal["angle",] | str | None
    image_rendering = (
        Literal[
            "enum",
            "auto",
            "crisp-edges",
            "-moz-crisp-edges",
            "optimizeQuality",
            "optimizeSpeed",
            "pixelated",
        ]
        | str
        | None
    )
    image_resolution = Literal["resolution",] | str | None
    ime_mode = (
        Literal[
            "enum",
            "active",
            "auto",
            "disabled",
            "inactive",
            "normal",
        ]
        | str
        | None
    )
    initial_letter = Literal["number, integer, enum",] | str | None
    initial_letter_align = (
        Literal[
            "enum",
            "alphabetic",
            "ideographic",
            "hebrew",
            "hanging",
            "border-box",
        ]
        | str
        | None
    )
    initial_letter_wrap = (
        Literal[
            "length, percentage, enum",
            "none",
            "first",
            "all",
            "grid",
        ]
        | str
        | None
    )
    inline_size = Literal["length, percentage",] | str | None
    isolation = (
        Literal[
            "enum",
            "auto",
            "isolate",
        ]
        | str
        | None
    )
    justify_content = (
        Literal[
            "enum",
            "center",
            "start",
            "end",
            "left",
            "right",
            "safe",
            "unsafe",
            "stretch",
            "space-evenly",
            "flex-end",
            "flex-start",
            "space-around",
            "space-between",
            "baseline",
            "first baseline",
            "last baseline",
        ]
        | str
        | None
    )
    justify_items = (
        Literal[
            "enum",
            "auto",
            "normal",
            "end",
            "start",
            "flex-end",
            "flex-start",
            "self-end",
            "self-start",
            "center",
            "left",
            "right",
            "baseline",
            "first baseline",
            "last baseline",
            "stretch",
            "safe",
            "unsafe",
            "legacy",
        ]
        | str
        | None
    )
    justify_self = (
        Literal[
            "enum",
            "auto",
            "normal",
            "end",
            "start",
            "flex-end",
            "flex-start",
            "self-end",
            "self-start",
            "center",
            "left",
            "right",
            "baseline",
            "first baseline",
            "last baseline",
            "stretch",
            "save",
            "unsave",
        ]
        | str
        | None
    )
    kerning = Literal["length, enum",] | str | None
    left = Literal["length, percentage",] | str | None
    letter_spacing = Literal["length",] | str | None
    lighting_color = Literal["color",] | str | None
    line_break = (
        Literal[
            "enum",
            "auto",
            "loose",
            "normal",
            "strict",
            "anywhere",
        ]
        | str
        | None
    )
    line_grid = (
        Literal[
            "enum",
            "match-parent",
            "create",
        ]
        | str
        | None
    )
    line_height = Literal["number, length, percentage",] | str | None
    line_snap = (
        Literal[
            "enum",
            "none",
            "baseline",
            "contain",
        ]
        | str
        | None
    )
    list_style = (
        Literal[
            "image, enum, url",
            "armenian",
            "circle",
            "decimal",
            "decimal-leading-zero",
            "disc",
            "georgian",
            "hanging",
            "inside",
            "lower-alpha",
            "lower-greek",
            "lower-latin",
            "lower-roman",
            "none",
            "outside",
            "square",
            "symbols()",
            "upper-alpha",
            "upper-latin",
            "upper-roman",
            "url()",
        ]
        | str
        | None
    )
    list_style_image = Literal["image",] | str | None
    list_style_position = (
        Literal[
            "enum",
            "inside",
            "outside",
        ]
        | str
        | None
    )
    list_style_type = (
        Literal[
            "enum, string",
            "arabic-indic",
            "armenian",
            "bengali",
            "cambodian",
            "circle",
            "cjk-decimal",
            "cjk-earthly-branch",
            "cjk-heavenly-stem",
            "decimal",
            "decimal-leading-zero",
            "devanagari",
            "disc",
            "disclosure-closed",
            "disclosure-open",
            "georgian",
            "gujarati",
            "gurmukhi",
            "hebrew",
            "hiragana",
            "hiragana-iroha",
            "kannada",
            "katakana",
            "katakana-iroha",
            "khmer",
            "lao",
            "lower-alpha",
            "lower-armenian",
            "lower-greek",
            "lower-latin",
            "lower-roman",
            "malayalam",
            "mongolian",
            "myanmar",
            "none",
            "oriya",
            "persian",
            "square",
            "tamil",
            "telugu",
            "thai",
            "tibetan",
            "symbols()",
            "upper-alpha",
            "upper-armenian",
            "upper-latin",
            "upper-roman",
        ]
        | str
        | None
    )
    margin = Literal["length, percentage",] | str | None
    margin_block_end = Literal["length, percentage",] | str | None
    margin_block_start = Literal["length, percentage",] | str | None
    margin_bottom = Literal["length, percentage",] | str | None
    margin_inline_end = Literal["length, percentage",] | str | None
    margin_inline_start = Literal["length, percentage",] | str | None
    margin_left = Literal["length, percentage",] | str | None
    margin_right = Literal["length, percentage",] | str | None
    margin_top = Literal["length, percentage",] | str | None
    marker = Literal["url",] | str | None
    marker_end = Literal["url",] | str | None
    marker_mid = Literal["url",] | str | None
    marker_side = (
        Literal[
            "enum",
            "list-item",
            "list-container",
        ]
        | str
        | None
    )
    marker_start = Literal["url",] | str | None
    mask = (
        Literal[
            "url, image, length, percentage, position, repeat, geometry-box, enum",
            "none",
            "url()",
            "alpha",
            "auto",
            "luminance",
            "contain",
            "cover",
            "no-clip",
            "add",
            "exclude",
            "intersect",
            "subtract",
        ]
        | str
        | None
    )
    mask_border = (
        Literal[
            "image, length, number, percentage, enum",
            "none",
            "fill",
            "auto",
            "repeat",
            "round",
            "space",
            "stretch",
            "alpha",
            "luminance",
        ]
        | str
        | None
    )
    mask_border_mode = (
        Literal[
            "enum",
            "alpha",
            "luminance",
        ]
        | str
        | None
    )
    mask_border_outset = Literal["length, number",] | str | None
    mask_border_repeat = (
        Literal[
            "enum",
            "repeat",
            "round",
            "space",
            "stretch",
        ]
        | str
        | None
    )
    mask_border_slice = Literal["number, percentage, enum",] | str | None
    mask_border_source = Literal["image, enum",] | str | None
    mask_border_width = Literal["length, percentage, enum",] | str | None
    mask_clip = Literal["geometry-box, enum",] | str | None
    mask_composite = (
        Literal[
            "enum",
            "add",
            "exclude",
            "intersect",
            "subtract",
        ]
        | str
        | None
    )
    mask_image = (
        Literal[
            "url, image, enum",
            "none",
            "url()",
        ]
        | str
        | None
    )
    mask_mode = (
        Literal[
            "url, image, enum",
            "alpha",
            "auto",
            "luminance",
        ]
        | str
        | None
    )
    mask_origin = Literal["geometry-box, enum",] | str | None
    mask_position = Literal["position, length, percentage",] | str | None
    mask_repeat = Literal["repeat",] | str | None
    mask_size = (
        Literal[
            "length, percentage, enum",
            "auto",
            "contain",
            "cover",
        ]
        | str
        | None
    )
    mask_type = (
        Literal[
            "enum",
            "alpha",
            "luminance",
        ]
        | str
        | None
    )
    max_block_size = Literal["length, percentage",] | str | None
    max_height = Literal["length, percentage",] | str | None
    max_inline_size = Literal["length, percentage",] | str | None
    max_lines = Literal["integer, enum",] | str | None
    max_width = Literal["length, percentage",] | str | None
    max_zoom = Literal["number, percentage, enum",] | str | None
    min_block_size = Literal["length, percentage",] | str | None
    min_height = Literal["length, percentage",] | str | None
    min_inline_size = Literal["length, percentage",] | str | None
    min_width = Literal["length, percentage",] | str | None
    min_zoom = Literal["number, percentage, enum",] | str | None
    mix_blend_mode = (
        Literal[
            "enum",
            "normal",
            "multiply",
            "screen",
            "overlay",
            "darken",
            "lighten",
            "color-dodge",
            "color-burn",
            "hard-light",
            "soft-light",
            "difference",
            "exclusion",
            "hue",
            "saturation",
            "color",
            "luminosity",
        ]
        | str
        | None
    )
    motion = (
        Literal[
            "url, length, percentage, angle, shape, geometry-box, enum",
            "none",
            "path()",
            "url()",
            "auto",
            "reverse",
        ]
        | str
        | None
    )
    motion_offset = Literal["length, percentage",] | str | None
    motion_path = (
        Literal[
            "url, shape, geometry-box, enum",
            "none",
            "path()",
            "url()",
        ]
        | str
        | None
    )
    motion_rotation = Literal["angle",] | str | None
    move_to = Literal["identifier",] | str | None
    nav_down = (
        Literal[
            "enum, identifier, string",
            "auto",
            "current",
            "root",
        ]
        | str
        | None
    )
    nav_index = Literal["number",] | str | None
    nav_left = (
        Literal[
            "enum, identifier, string",
            "auto",
            "current",
            "root",
        ]
        | str
        | None
    )
    nav_right = (
        Literal[
            "enum, identifier, string",
            "auto",
            "current",
            "root",
        ]
        | str
        | None
    )
    nav_up = (
        Literal[
            "enum, identifier, string",
            "auto",
            "current",
            "root",
        ]
        | str
        | None
    )
    negative = Literal["image, identifier, string",] | str | None
    object_fit = (
        Literal[
            "enum",
            "contain",
            "cover",
            "fill",
            "none",
            "scale-down",
        ]
        | str
        | None
    )
    object_position = Literal["position, length, percentage",] | str | None
    offset_block_end = Literal["length, percentage",] | str | None
    offset_block_start = Literal["length, percentage",] | str | None
    offset_inline_end = Literal["length, percentage",] | str | None
    offset_inline_start = Literal["length, percentage",] | str | None
    opacity = Literal["number(0-1)",] | str | None
    order = Literal["integer",] | str | None
    orientation = (
        Literal[
            "enum",
            "auto",
            "landscape",
            "portrait",
        ]
        | str
        | None
    )
    orphans = Literal["integer",] | str | None
    outline = (
        Literal[
            "length, line-width, line-style, color, enum",
            "auto",
            "invert",
        ]
        | str
        | None
    )
    outline_color = Literal["enum, color",] | str | None
    outline_offset = Literal["length",] | str | None
    outline_style = Literal["line-style, enum",] | str | None
    outline_width = Literal["length, line-width",] | str | None
    overflow = (
        Literal[
            "enum",
            "auto",
            "clip",
            "hidden",
            "-moz-hidden-unscrollable",
            "scroll",
            "visible",
        ]
        | str
        | None
    )
    overflow_wrap = (
        Literal[
            "enum",
            "break-word",
            "normal",
            "anywhere",
        ]
        | str
        | None
    )
    overflow_x = (
        Literal[
            "enum",
            "auto",
            "clip",
            "hidden",
            "scroll",
            "visible",
        ]
        | str
        | None
    )
    overflow_y = (
        Literal[
            "enum",
            "auto",
            "clip",
            "hidden",
            "scroll",
            "visible",
        ]
        | str
        | None
    )
    pad = Literal["integer, image, string, identifier",] | str | None
    padding = Literal["length, percentage",] | str | None
    padding_block_end = Literal["length, percentage",] | str | None
    padding_block_start = Literal["length, percentage",] | str | None
    padding_bottom = Literal["length, percentage",] | str | None
    padding_inline_end = Literal["length, percentage",] | str | None
    padding_inline_start = Literal["length, percentage",] | str | None
    padding_left = Literal["length, percentage",] | str | None
    padding_right = Literal["length, percentage",] | str | None
    padding_top = Literal["length, percentage",] | str | None
    page = Literal["identifier",] | str | None
    page_break_after = (
        Literal[
            "enum",
            "always",
            "auto",
            "avoid",
            "left",
            "recto",
            "right",
            "verso",
        ]
        | str
        | None
    )
    page_break_before = (
        Literal[
            "enum",
            "always",
            "auto",
            "avoid",
            "left",
            "right",
        ]
        | str
        | None
    )
    page_break_inside = (
        Literal[
            "enum",
            "auto",
            "avoid",
        ]
        | str
        | None
    )
    page_policy = (
        Literal[
            "enum",
            "first",
            "last",
            "start",
        ]
        | str
        | None
    )
    paint_order = (
        Literal[
            "enum",
            "fill",
            "markers",
            "normal",
            "stroke",
        ]
        | str
        | None
    )
    pause = (
        Literal[
            "time, enum",
            "medium",
            "none",
            "strong",
            "weak",
            "x-strong",
            "x-weak",
        ]
        | str
        | None
    )
    pause_after = Literal["time",] | str | None
    pause_before = Literal["time",] | str | None
    perspective = Literal["length, enum",] | str | None
    perspective_origin = Literal["position, percentage, length",] | str | None
    pointer_events = (
        Literal[
            "enum",
            "all",
            "fill",
            "none",
            "painted",
            "stroke",
            "visible",
            "visibleFill",
            "visiblePainted",
            "visibleStroke",
        ]
        | str
        | None
    )
    position = (
        Literal[
            "enum",
            "absolute",
            "center",
            "fixed",
            "-ms-page",
            "page",
            "relative",
            "static",
            "sticky",
            "-webkit-sticky",
        ]
        | str
        | None
    )
    prefix = Literal["image, string, identifier",] | str | None
    quotes = Literal["string",] | str | None
    r = Literal["length, percentage",] | str | None
    range = (
        Literal[
            "integer, enum",
            "auto",
            "infinite",
        ]
        | str
        | None
    )
    region_fragment = (
        Literal[
            "enum",
            "auto",
            "break",
        ]
        | str
        | None
    )
    resize = (
        Literal[
            "enum",
            "both",
            "block",
            "horizontal",
            "inline",
            "none",
            "vertical",
        ]
        | str
        | None
    )
    rest = Literal["time",] | str | None
    rest_after = Literal["time",] | str | None
    rest_before = Literal["time",] | str | None
    right = Literal["length, percentage",] | str | None
    rotation = Literal["angle",] | str | None
    rotation_point = Literal["position, percentage, length",] | str | None
    ruby_align = (
        Literal[
            "enum",
            "auto",
            "center",
            "distribute-letter",
            "distribute-space",
            "left",
            "line-edge",
            "right",
            "start",
            "space-between",
            "space-around",
        ]
        | str
        | None
    )
    ruby_overhang = (
        Literal[
            "enum",
            "auto",
            "end",
            "none",
            "start",
        ]
        | str
        | None
    )
    ruby_position = (
        Literal[
            "enum",
            "after",
            "before",
            "inline",
            "right",
        ]
        | str
        | None
    )
    ruby_span = (
        Literal[
            "enum",
            "attr(x)",
            "none",
        ]
        | str
        | None
    )
    rx = Literal["length, percentage",] | str | None
    ry = Literal["length, percentage",] | str | None
    scroll_behavior = (
        Literal[
            "enum",
            "auto",
            "smooth",
        ]
        | str
        | None
    )
    scroll_snap_coordinate = (
        Literal[
            "position, length, percentage, enum",
            "none",
            "border-box",
            "margin-box",
        ]
        | str
        | None
    )
    scroll_snap_destination = Literal["position, length, percentage",] | str | None
    scroll_snap_points_x = (
        Literal[
            "enum",
            "none",
            "repeat()",
        ]
        | str
        | None
    )
    scroll_snap_points_y = (
        Literal[
            "enum",
            "none",
            "repeat()",
        ]
        | str
        | None
    )
    scroll_snap_type = (
        Literal[
            "enum",
            "none",
            "mandatory",
            "proximity",
        ]
        | str
        | None
    )
    scrollbar_3dlight_color = Literal["color",] | str | None
    scrollbar_arrow_color = Literal["color",] | str | None
    scrollbar_base_color = Literal["color",] | str | None
    scrollbar_darkshadow_color = Literal["color",] | str | None
    scrollbar_face_color = Literal["color",] | str | None
    scrollbar_highlight_color = Literal["color",] | str | None
    scrollbar_shadow_color = Literal["color",] | str | None
    scrollbar_track_color = Literal["color",] | str | None
    shape_image_threshold = Literal["number",] | str | None
    shape_inside = (
        Literal[
            "image, shape, box, enum",
            "auto",
            "display",
            "margin-box",
            "outside-shape",
            "url()",
        ]
        | str
        | None
    )
    shape_margin = Literal["url, length, percentage",] | str | None
    shape_outside = (
        Literal[
            "image, box, shape, enum",
            "margin-box",
            "none",
        ]
        | str
        | None
    )
    shape_padding = Literal["length",] | str | None
    shape_rendering = (
        Literal[
            "enum",
            "auto",
            "crispEdges",
            "geometricPrecision",
            "optimizeSpeed",
        ]
        | str
        | None
    )
    size = Literal["length",] | str | None
    speak = (
        Literal[
            "enum",
            "auto",
            "none",
            "normal",
        ]
        | str
        | None
    )
    speak_as = (
        Literal[
            "enum",
            "digits",
            "literal-punctuation",
            "no-punctuation",
            "normal",
            "spell-out",
        ]
        | str
        | None
    )
    src = (
        Literal[
            "enum, url, identifier",
            "url()",
            "format()",
            "local()",
        ]
        | str
        | None
    )
    stop_color = Literal["color",] | str | None
    stop_opacity = Literal["number(0-1)",] | str | None
    stroke = (
        Literal[
            "color, enum, url",
            "child",
            "child()",
            "context-fill",
            "context-stroke",
            "url()",
            "none",
        ]
        | str
        | None
    )
    stroke_dasharray = Literal["length, percentage, number, enum",] | str | None
    stroke_dashoffset = Literal["percentage, length",] | str | None
    stroke_linecap = (
        Literal[
            "enum",
            "butt",
            "round",
            "square",
        ]
        | str
        | None
    )
    stroke_linejoin = (
        Literal[
            "enum",
            "arcs",
            "bevel",
            "miter",
            "miter-clip",
            "round",
        ]
        | str
        | None
    )
    stroke_miterlimit = Literal["number",] | str | None
    stroke_opacity = Literal["number(0-1)",] | str | None
    stroke_width = Literal["percentage, length",] | str | None
    suffix = Literal["image, string, identifier",] | str | None
    symbols = Literal["image, string, identifier",] | str | None
    system = (
        Literal[
            "enum, integer",
            "additive",
            "alphabetic",
            "cyclic",
            "extends",
            "fixed",
            "numeric",
            "symbolic",
        ]
        | str
        | None
    )
    tab_size = Literal["integer, length",] | str | None
    table_layout = (
        Literal[
            "enum",
            "auto",
            "fixed",
        ]
        | str
        | None
    )
    text_align = Literal["string",] | str | None
    text_align_last = (
        Literal[
            "enum",
            "auto",
            "center",
            "end",
            "justify",
            "left",
            "right",
            "start",
        ]
        | str
        | None
    )
    text_anchor = (
        Literal[
            "enum",
            "end",
            "middle",
            "start",
        ]
        | str
        | None
    )
    text_combine_upright = (
        Literal[
            "enum, integer",
            "all",
            "digits",
            "none",
        ]
        | str
        | None
    )
    text_decoration = (
        Literal[
            "enum, color",
            "dashed",
            "dotted",
            "double",
            "line-through",
            "none",
            "overline",
            "solid",
            "underline",
            "wavy",
        ]
        | str
        | None
    )
    text_decoration_color = Literal["color",] | str | None
    text_decoration_line = (
        Literal[
            "enum",
            "line-through",
            "none",
            "overline",
            "underline",
        ]
        | str
        | None
    )
    text_decoration_skip = (
        Literal[
            "enum",
            "box-decoration",
            "ink",
            "none",
            "objects",
            "spaces",
        ]
        | str
        | None
    )
    text_decoration_style = (
        Literal[
            "enum",
            "dashed",
            "dotted",
            "double",
            "none",
            "solid",
            "wavy",
        ]
        | str
        | None
    )
    text_emphasis = Literal["color, string",] | str | None
    text_emphasis_color = Literal["color",] | str | None
    text_emphasis_position = (
        Literal[
            "enum",
            "over",
            "under",
            "left",
            "right",
        ]
        | str
        | None
    )
    text_emphasis_style = Literal["string",] | str | None
    text_indent = Literal["percentage, length",] | str | None
    text_justify = (
        Literal[
            "enum",
            "auto",
            "distribute",
            "distribute-all-lines",
            "inter-character",
            "inter-cluster",
            "inter-ideograph",
            "inter-word",
            "kashida",
            "newspaper",
            "none",
        ]
        | str
        | None
    )
    text_orientation = (
        Literal[
            "enum",
            "mixed",
            "sideways",
            "sideways-left",
            "sideways-right",
            "upright",
            "use-glyph-orientation",
        ]
        | str
        | None
    )
    text_overflow = (
        Literal[
            "enum, string",
            "clip",
            "ellipsis",
        ]
        | str
        | None
    )
    text_rendering = (
        Literal[
            "enum",
            "auto",
            "geometricPrecision",
            "optimizeLegibility",
            "optimizeSpeed",
        ]
        | str
        | None
    )
    text_shadow = Literal["length, color",] | str | None
    text_size_adjust = (
        Literal[
            "enum, percentage",
            "auto",
            "none",
        ]
        | str
        | None
    )
    text_space_collapse = (
        Literal[
            "enum",
            "collapse",
            "discard",
            "preserve",
            "preserve-auto",
            "preserve-trim",
            "preserve-breaks",
            "preserve-spaces",
        ]
        | str
        | None
    )
    text_space_trim = (
        Literal[
            "enum",
            "none",
            "trim-inner",
            "discard-before",
            "discard-after",
        ]
        | str
        | None
    )
    text_spacing = (
        Literal[
            "enum",
            "normal",
            "none",
            "trim-start",
            "space-start",
            "trim-end",
            "space-end",
            "allow-end",
            "trim-adjacent",
            "space-adjacent",
            "no-compress",
            "ideograph-alpha",
            "ideograph-numeric",
            "punctuation",
        ]
        | str
        | None
    )
    text_transform = (
        Literal[
            "enum",
            "capitalize",
            "full-width",
            "lowercase",
            "none",
            "uppercase",
        ]
        | str
        | None
    )
    text_underline_position = (
        Literal[
            "enum",
            "above",
            "auto",
            "below",
            "left",
            "right",
            "under",
        ]
        | str
        | None
    )
    text_wrap = (
        Literal[
            "enum",
            "balance",
            "normal",
            "nowrap",
        ]
        | str
        | None
    )
    top = Literal["length, percentage",] | str | None
    touch_action = (
        Literal[
            "enum",
            "auto",
            "cross-slide-x",
            "cross-slide-y",
            "double-tap-zoom",
            "manipulation",
            "none",
            "pan-x",
            "pan-y",
            "pinch-zoom",
        ]
        | str
        | None
    )
    transform = (
        Literal[
            "enum",
            "matrix()",
            "matrix3d()",
            "none",
            "perspective()",
            "rotate()",
            "rotate3d()",
            "rotateX('angle')",
            "rotateY('angle')",
            "rotateZ('angle')",
            "scale()",
            "scale3d()",
            "scaleX()",
            "scaleY()",
            "scaleZ()",
            "skew()",
            "skewX()",
            "skewY()",
            "translate()",
            "translate3d()",
            "translateX()",
            "translateY()",
            "translateZ()",
        ]
        | str
        | None
    )
    transform_box = (
        Literal[
            "enum",
            "border-box",
            "fill-box",
            "view-box",
        ]
        | str
        | None
    )
    transform_origin = Literal["position, length, percentage",] | str | None
    transform_style = (
        Literal[
            "enum",
            "flat",
            "preserve-3d",
        ]
        | str
        | None
    )
    transition = (
        Literal[
            "time, property, timing-function, enum",
            "all",
            "none",
        ]
        | str
        | None
    )
    transition_delay = Literal["time",] | str | None
    transition_duration = Literal["time",] | str | None
    transition_property = Literal["property",] | str | None
    transition_timing_function = Literal["timing-function",] | str | None
    unicode_bidi = (
        Literal[
            "enum",
            "bidi-override",
            "embed",
            "isolate",
            "isolate-override",
            "normal",
            "plaintext",
        ]
        | str
        | None
    )
    unicode_range = Literal["unicode-range",] | str | None
    user_select = (
        Literal[
            "enum",
            "all",
            "auto",
            "contain",
            "none",
            "text",
        ]
        | str
        | None
    )
    user_zoom = (
        Literal[
            "enum",
            "fixed",
            "zoom",
        ]
        | str
        | None
    )
    vector_effect = (
        Literal[
            "enum",
            "fixed-position",
            "none",
            "non-rotation",
            "non-scaling-size",
            "non-scaling-stroke",
            "screen",
            "viewport",
        ]
        | str
        | None
    )
    vertical_align = Literal["percentage, length",] | str | None
    visibility = (
        Literal[
            "enum",
            "collapse",
            "hidden",
            "visible",
        ]
        | str
        | None
    )
    voice_balance = Literal["number(-100-100)",] | str | None
    voice_duration = Literal["time",] | str | None
    voice_family = Literal["number, string, identifier",] | str | None
    voice_pitch = Literal["percentage, number, frequency, semitones",] | str | None
    voice_range = Literal["percentage, number, frequency, semitones",] | str | None
    voice_rate = Literal["percentage",] | str | None
    voice_stress = (
        Literal[
            "enum",
            "moderate",
            "none",
            "normal",
            "reduced",
            "strong",
        ]
        | str
        | None
    )
    voice_volume = (
        Literal[
            "volume, enum",
            "loud",
            "medium",
            "silent",
            "soft",
            "x-loud",
            "x-soft",
        ]
        | str
        | None
    )
    widows = Literal["integer",] | str | None
    width = Literal["length, percentage",] | str | None
    will_change = (
        Literal[
            "enum, identifier",
            "auto",
            "contents",
            "scroll-position",
        ]
        | str
        | None
    )
    word_break = (
        Literal[
            "enum",
            "break-all",
            "keep-all",
            "normal",
        ]
        | str
        | None
    )
    word_spacing = Literal["length, percentage",] | str | None
    word_wrap = (
        Literal[
            "enum",
            "break-word",
            "normal",
        ]
        | str
        | None
    )
    wrap_after = (
        Literal[
            "enum",
            "auto",
            "avoid",
            "avoid-line",
            "avoid-flex",
            "line",
            "flex",
        ]
        | str
        | None
    )
    wrap_before = (
        Literal[
            "enum",
            "auto",
            "avoid",
            "avoid-line",
            "avoid-flex",
            "line",
            "flex",
        ]
        | str
        | None
    )
    wrap_flow = (
        Literal[
            "enum",
            "auto",
            "both",
            "clear",
            "end",
            "maximum",
            "minimum",
            "start",
        ]
        | str
        | None
    )
    wrap_inside = (
        Literal[
            "enum",
            "auto",
            "avoid",
        ]
        | str
        | None
    )
    wrap_through = (
        Literal[
            "enum",
            "none",
            "wrap",
        ]
        | str
        | None
    )
    writing_mode = (
        Literal[
            "enum",
            "horizontal-tb",
            "sideways-lr",
            "sideways-rl",
            "vertical-lr",
            "vertical-rl",
        ]
        | str
        | None
    )
    x = Literal["length, percentage",] | str | None
    y = Literal["length, percentage",] | str | None
    z_index = Literal["integer",] | str | None
    zoom = Literal["enum, integer, number, percentage",] | str | None


# Base Class For Every Element
class Element:
    current_context: ContextVar["Element | None"] = ContextVar(
        "current_context", default=None
    )

    VOID_TAGS_SET = frozenset(get_args(HTMLVoidTag))

    def __init__(self, name: HTMLTag | str):
        self._name = name
        self._is_void = self._name in Element.VOID_TAGS_SET
        self._attrs_dict = {}
        self._style_dict = {}
        self._classes = []
        self._children = []
        self._context_cache = None

        current = Element.current_context.get()
        if (
            current is not None and current is not self
        ):  # Fixed: Infinite recursion: a.children.append(a)
            current._children.append(self)

    def attr(
        self, d: dict[str, str | bool] | None = None, **kwargs: Unpack[HTMLAttribute]
    ):
        "Values None or False are removed."
        d = dict(d or {})
        d = {k: v for k, v in d.items() if v is not None and v is not False}
        kwargs = {k: v for k, v in kwargs.items() if v is not None and v is not False}

        # you can't set style or class from attr to remove confusions
        if "style" in kwargs or "style" in d:
            raise KeyError("Please use .style() method instead.")
        if "class_" in kwargs or "class" in d:
            raise KeyError("Please use .classes() method instead.")

        to_be_preprocessed = {}
        for k, v in kwargs.items():
            if k in HTMLAttribute.__annotations__:
                to_be_preprocessed[k] = v
            else:
                if d.get(k) is None:
                    d[k] = v  # preference d > kwargs
                else:
                    warn(
                        f"html attr {k} in kwargs is wasted as it is already in `d`. Data lost."
                    )
        processed = {
            recover_thing_from_python_identifier(k): v
            for k, v in to_be_preprocessed.items()
        }
        processed.update(d)  # prefernce d > kwargs
        self._attrs_dict.update(processed)
        return self

    def class_(self, cls_str: str = "", *classes):
        classes = [*cls_str.split(), *classes]

        if len(classes) > 0:
            for c in classes:
                if c not in self._classes:
                    self._classes.append(c)
                else:
                    self._classes.remove(c)
                    self._classes.append(c)  # Respects insertion orders.
        return self

    def style(
        self, d: dict[str, str | None] | None = None, **kwargs: Unpack[CSSProperty]
    ):
        d = dict[str, str | None](d or {})

        # None --> none
        nd = {}
        nkwargs = {}

        for k, v in d.items():
            if v is None:
                v = "none"
            nd[k] = v

        for k, v in kwargs.items():
            if v is None:
                v = "none"
            nkwargs[k] = v

        to_be_processed = {}
        for k, v in kwargs.items():
            if k in CSSProperty.__annotations__:
                to_be_processed[k] = v
            else:
                if d.get(k) is None:
                    d[k] = v  # preference d > kwargs
                else:
                    warn(
                        f"css prop {k} in kwargs is wasted as it is already in `d`. Data lost."
                    )
        processed = {
            recover_thing_from_python_identifier(k): v
            for k, v in to_be_processed.items()
        }
        d.update(processed)  # preference d > kwargs
        self._style_dict.update(d)
        return self

    def text(self, data: str | None = None):
        if data is None:
            return self
        with self:
            Text(data)
        return self

    def __enter__(self):
        if self._is_void:
            raise Exception(
                f"`{self._name}` is a void tag hence can not have children. "
            )
        self._token = Element.current_context.set(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        Element.current_context.reset(self._token)

    def __str__(self):
        if not is_valid_attr_name(self._name):
            raise SyntaxError(f"{self._name} is not a valid html tag name")

        attr_str = ""
        for k, v in self._attrs_dict.items():
            if not is_valid_attr_name(k):
                raise SyntaxError(f"{k} is not a valid html attribute.")

            if isinstance(v, bool):
                if v is True:
                    attr_str += k + " "
            else:
                v = str(v)
                attr_str += k + "=" + f'"{html.escape(v, quote=True)}"' + " "

        if len(self._style_dict) > 0:
            style_val = " ".join([f"{k}:{v};" for k, v in self._style_dict.items()])
            attr_str += f' style="{html.escape(style_val, quote=True)}"'

        if len(self._classes) > 0:
            class_val = " ".join(self._classes)
            attr_str += f' class="{html.escape(class_val, quote=True)}"'

        if len(attr_str) > 0:
            attr_str = " " + attr_str

        if self._is_void:
            return f"<{self._name}{attr_str} />"

        return f"<{self._name}{attr_str}>{''.join([str(i) for i in self._children])}</{self._name}>"


class Text:
    def __init__(self, text: str) -> None:
        self.value = html.escape(text)
        current = Element.current_context.get()
        if current is not None:
            current._children.append(self)

    def __str__(self):
        return self.value


# Tag Dump
# ooklept/tag_dump.py


class tags:
    @staticmethod
    def html5(text: str | None = None, manifest: str | None = None) -> Element:
        return Element("html").attr(manifest=manifest).text(text)

    @staticmethod
    def head(text: str | None = None) -> Element:
        return Element("head").attr().text(text)

    @staticmethod
    def title(text: str | None = None) -> Element:
        return Element("title").attr().text(text)

    @staticmethod
    def base(
        href: str | None = None,
        target: Literal["_self", "_blank", "_parent", "_top"] | str | None = None,
    ) -> Element:
        return Element("base").attr(href=href, target=target)

    @staticmethod
    def link(
        href: str | None = None,
        crossorigin: Literal["anonymous", "use-credentials"] | str | None = None,
        rel: str | None = None,
        media: str | None = None,
        hreflang: str | None = None,
        type: str | None = None,
        sizes: str | None = None,
    ) -> Element:
        return Element("link").attr(
            href=href,
            crossorigin=crossorigin,
            rel=rel,
            media=media,
            hreflang=hreflang,
            type=type,
            sizes=sizes,
        )

    @staticmethod
    def meta(
        name: str | None = None,
        http_equiv: str | None = None,
        content: str | None = None,
        charset: str | None = None,
    ) -> Element:
        return Element("meta").attr(
            name=name, http_equiv=http_equiv, content=content, charset=charset
        )

    @staticmethod
    def style(
        text: str | None = None,
        media: str | None = None,
        nonce: str | None = None,
        type: str | None = None,
        scoped: Literal["true", "false"] | str | None = None,
    ) -> Element:
        return (
            Element("style")
            .attr(media=media, nonce=nonce, type=type, scoped=scoped)
            .text(text)
        )

    @staticmethod
    def body(
        text: str | None = None,
        onafterprint: str | None = None,
        onbeforeprint: str | None = None,
        onbeforeunload: str | None = None,
        onhashchange: str | None = None,
        onlanguagechange: str | None = None,
        onmessage: str | None = None,
        onoffline: str | None = None,
        ononline: str | None = None,
        onpagehide: str | None = None,
        onpageshow: str | None = None,
        onpopstate: str | None = None,
        onstorage: str | None = None,
        onunload: str | None = None,
    ) -> Element:
        return (
            Element("body")
            .attr(
                onafterprint=onafterprint,
                onbeforeprint=onbeforeprint,
                onbeforeunload=onbeforeunload,
                onhashchange=onhashchange,
                onlanguagechange=onlanguagechange,
                onmessage=onmessage,
                onoffline=onoffline,
                ononline=ononline,
                onpagehide=onpagehide,
                onpageshow=onpageshow,
                onpopstate=onpopstate,
                onstorage=onstorage,
                onunload=onunload,
            )
            .text(text)
        )

    @staticmethod
    def article(text: str | None = None) -> Element:
        return Element("article").attr().text(text)

    @staticmethod
    def section(text: str | None = None) -> Element:
        return Element("section").attr().text(text)

    @staticmethod
    def nav(text: str | None = None) -> Element:
        return Element("nav").attr().text(text)

    @staticmethod
    def aside(text: str | None = None) -> Element:
        return Element("aside").attr().text(text)

    @staticmethod
    def h1(text: str | None = None) -> Element:
        return Element("h1").attr().text(text)

    @staticmethod
    def h2(text: str | None = None) -> Element:
        return Element("h2").attr().text(text)

    @staticmethod
    def h3(text: str | None = None) -> Element:
        return Element("h3").attr().text(text)

    @staticmethod
    def h4(text: str | None = None) -> Element:
        return Element("h4").attr().text(text)

    @staticmethod
    def h5(text: str | None = None) -> Element:
        return Element("h5").attr().text(text)

    @staticmethod
    def h6(text: str | None = None) -> Element:
        return Element("h6").attr().text(text)

    @staticmethod
    def header(text: str | None = None) -> Element:
        return Element("header").attr().text(text)

    @staticmethod
    def footer(text: str | None = None) -> Element:
        return Element("footer").attr().text(text)

    @staticmethod
    def address(text: str | None = None) -> Element:
        return Element("address").attr().text(text)

    @staticmethod
    def p(text: str | None = None) -> Element:
        return Element("p").attr().text(text)

    @staticmethod
    def hr() -> Element:
        return Element("hr").attr()

    @staticmethod
    def pre(text: str | None = None) -> Element:
        return Element("pre").attr().text(text)

    @staticmethod
    def blockquote(text: str | None = None, cite: str | None = None) -> Element:
        return Element("blockquote").attr(cite=cite).text(text)

    @staticmethod
    def ol(
        text: str | None = None,
        reversed: Literal["true", "false"] | str | None = None,
        start: str | None = None,
        type: Literal["1", "a", "A", "i", "I"] | str | None = None,
    ) -> Element:
        return Element("ol").attr(reversed=reversed, start=start, type=type).text(text)

    @staticmethod
    def ul(text: str | None = None) -> Element:
        return Element("ul").attr().text(text)

    @staticmethod
    def li(text: str | None = None, value: str | None = None) -> Element:
        return Element("li").attr(value=value).text(text)

    @staticmethod
    def dl(text: str | None = None) -> Element:
        return Element("dl").attr().text(text)

    @staticmethod
    def dt(text: str | None = None) -> Element:
        return Element("dt").attr().text(text)

    @staticmethod
    def dd(text: str | None = None) -> Element:
        return Element("dd").attr().text(text)

    @staticmethod
    def figure(text: str | None = None) -> Element:
        return Element("figure").attr().text(text)

    @staticmethod
    def figcaption(text: str | None = None) -> Element:
        return Element("figcaption").attr().text(text)

    @staticmethod
    def main(text: str | None = None) -> Element:
        return Element("main").attr().text(text)

    @staticmethod
    def div(text: str | None = None) -> Element:
        return Element("div").attr().text(text)

    @staticmethod
    def a(
        text: str | None = None,
        href: str | None = None,
        target: Literal["_self", "_blank", "_parent", "_top"] | str | None = None,
        download: str | None = None,
        ping: str | None = None,
        rel: str | None = None,
        hreflang: str | None = None,
        type: str | None = None,
    ) -> Element:
        return (
            Element("a")
            .attr(
                href=href,
                target=target,
                download=download,
                ping=ping,
                rel=rel,
                hreflang=hreflang,
                type=type,
            )
            .text(text)
        )

    @staticmethod
    def em(text: str | None = None) -> Element:
        return Element("em").attr().text(text)

    @staticmethod
    def strong(text: str | None = None) -> Element:
        return Element("strong").attr().text(text)

    @staticmethod
    def small(text: str | None = None) -> Element:
        return Element("small").attr().text(text)

    @staticmethod
    def s(text: str | None = None) -> Element:
        return Element("s").attr().text(text)

    @staticmethod
    def cite(text: str | None = None) -> Element:
        return Element("cite").attr().text(text)

    @staticmethod
    def q(text: str | None = None, cite: str | None = None) -> Element:
        return Element("q").attr(cite=cite).text(text)

    @staticmethod
    def dfn(text: str | None = None) -> Element:
        return Element("dfn").attr().text(text)

    @staticmethod
    def abbr(text: str | None = None) -> Element:
        return Element("abbr").attr().text(text)

    @staticmethod
    def ruby(text: str | None = None) -> Element:
        return Element("ruby").attr().text(text)

    @staticmethod
    def rb(text: str | None = None) -> Element:
        return Element("rb").attr().text(text)

    @staticmethod
    def rt(text: str | None = None) -> Element:
        return Element("rt").attr().text(text)

    @staticmethod
    def rp(text: str | None = None) -> Element:
        return Element("rp").attr().text(text)

    @staticmethod
    def time(text: str | None = None, datetime: str | None = None) -> Element:
        return Element("time").attr(datetime=datetime).text(text)

    @staticmethod
    def code(text: str | None = None) -> Element:
        return Element("code").attr().text(text)

    @staticmethod
    def var(text: str | None = None) -> Element:
        return Element("var").attr().text(text)

    @staticmethod
    def samp(text: str | None = None) -> Element:
        return Element("samp").attr().text(text)

    @staticmethod
    def kbd(text: str | None = None) -> Element:
        return Element("kbd").attr().text(text)

    @staticmethod
    def sub(text: str | None = None) -> Element:
        return Element("sub").attr().text(text)

    @staticmethod
    def sup(text: str | None = None) -> Element:
        return Element("sup").attr().text(text)

    @staticmethod
    def i(text: str | None = None) -> Element:
        return Element("i").attr().text(text)

    @staticmethod
    def b(text: str | None = None) -> Element:
        return Element("b").attr().text(text)

    @staticmethod
    def u(text: str | None = None) -> Element:
        return Element("u").attr().text(text)

    @staticmethod
    def mark(text: str | None = None) -> Element:
        return Element("mark").attr().text(text)

    @staticmethod
    def bdi(text: str | None = None) -> Element:
        return Element("bdi").attr().text(text)

    @staticmethod
    def bdo(text: str | None = None) -> Element:
        return Element("bdo").attr().text(text)

    @staticmethod
    def span(text: str | None = None) -> Element:
        return Element("span").attr().text(text)

    @staticmethod
    def br() -> Element:
        return Element("br").attr()

    @staticmethod
    def wbr() -> Element:
        return Element("wbr").attr()

    @staticmethod
    def ins(text: str | None = None) -> Element:
        return Element("ins").attr().text(text)

    @staticmethod
    def del_(
        text: str | None = None, cite: str | None = None, datetime: str | None = None
    ) -> Element:
        return Element("del").attr(cite=cite, datetime=datetime).text(text)

    @staticmethod
    def picture(text: str | None = None) -> Element:
        return Element("picture").attr().text(text)

    @staticmethod
    def img(
        alt: str | None = None,
        src: str | None = None,
        srcset: str | None = None,
        crossorigin: Literal["anonymous", "use-credentials"] | str | None = None,
        usemap: str | None = None,
        ismap: Literal["true", "false"] | str | None = None,
        width: str | None = None,
        height: str | None = None,
        decoding: Literal["sync", "async", "auto"] | str | None = None,
        loading: Literal["eager", "lazy"] | str | None = None,
        fetchpriority: Literal["high", "low", "auto"] | str | None = None,
        referrerpolicy: Literal[
            "no-referrer",
            "no-referrer-when-downgrade",
            "origin",
            "origin-when-cross-origin",
            "same-origin",
            "strict-origin",
            "strict-origin-when-cross-origin",
            "unsafe-url",
        ]
        | str
        | None = None,
        sizes: str | None = None,
    ) -> Element:
        return Element("img").attr(
            alt=alt,
            src=src,
            srcset=srcset,
            crossorigin=crossorigin,
            usemap=usemap,
            ismap=ismap,
            width=width,
            height=height,
            decoding=decoding,
            loading=loading,
            fetchpriority=fetchpriority,
            referrerpolicy=referrerpolicy,
            sizes=sizes,
        )

    @staticmethod
    def iframe(
        text: str | None = None,
        src: str | None = None,
        srcdoc: str | None = None,
        name: str | None = None,
        sandbox: Literal[
            "allow-forms",
            "allow-modals",
            "allow-pointer-lock",
            "allow-popups",
            "allow-popups-to-escape-sandbox",
            "allow-same-origin",
            "allow-scripts",
            "allow-top-navigation",
        ]
        | str
        | None = None,
        seamless: Literal["true", "false"] | str | None = None,
        allowfullscreen: Literal["true", "false"] | str | None = None,
        width: str | None = None,
        height: str | None = None,
    ) -> Element:
        return (
            Element("iframe")
            .attr(
                src=src,
                srcdoc=srcdoc,
                name=name,
                sandbox=sandbox,
                seamless=seamless,
                allowfullscreen=allowfullscreen,
                width=width,
                height=height,
            )
            .text(text)
        )

    @staticmethod
    def embed(
        src: str | None = None,
        type: str | None = None,
        width: str | None = None,
        height: str | None = None,
    ) -> Element:
        return Element("embed").attr(src=src, type=type, width=width, height=height)

    @staticmethod
    def object(
        text: str | None = None,
        data: str | None = None,
        type: str | None = None,
        typemustmatch: Literal["true", "false"] | str | None = None,
        name: str | None = None,
        usemap: str | None = None,
        form: str | None = None,
        width: str | None = None,
        height: str | None = None,
    ) -> Element:
        return (
            Element("object")
            .attr(
                data=data,
                type=type,
                typemustmatch=typemustmatch,
                name=name,
                usemap=usemap,
                form=form,
                width=width,
                height=height,
            )
            .text(text)
        )

    @staticmethod
    def param(name: str | None = None, value: str | None = None) -> Element:
        return Element("param").attr(name=name, value=value)

    @staticmethod
    def video(
        text: str | None = None,
        src: str | None = None,
        crossorigin: Literal["anonymous", "use-credentials"] | str | None = None,
        poster: str | None = None,
        preload: Literal["none", "metadata", "auto"] | str | None = None,
        autoplay: Literal["true", "false"] | str | None = None,
        mediagroup: str | None = None,
        loop: Literal["true", "false"] | str | None = None,
        muted: Literal["true", "false"] | str | None = None,
        controls: Literal["true", "false"] | str | None = None,
        width: str | None = None,
        height: str | None = None,
    ) -> Element:
        return (
            Element("video")
            .attr(
                src=src,
                crossorigin=crossorigin,
                poster=poster,
                preload=preload,
                autoplay=autoplay,
                mediagroup=mediagroup,
                loop=loop,
                muted=muted,
                controls=controls,
                width=width,
                height=height,
            )
            .text(text)
        )

    @staticmethod
    def audio(
        text: str | None = None,
        src: str | None = None,
        crossorigin: Literal["anonymous", "use-credentials"] | str | None = None,
        preload: Literal["none", "metadata", "auto"] | str | None = None,
        autoplay: Literal["true", "false"] | str | None = None,
        mediagroup: str | None = None,
        loop: Literal["true", "false"] | str | None = None,
        muted: Literal["true", "false"] | str | None = None,
        controls: Literal["true", "false"] | str | None = None,
    ) -> Element:
        return (
            Element("audio")
            .attr(
                src=src,
                crossorigin=crossorigin,
                preload=preload,
                autoplay=autoplay,
                mediagroup=mediagroup,
                loop=loop,
                muted=muted,
                controls=controls,
            )
            .text(text)
        )

    @staticmethod
    def source(src: str | None = None, type: str | None = None) -> Element:
        return Element("source").attr(src=src, type=type)

    @staticmethod
    def track(
        default: Literal["true", "false"] | str | None = None,
        kind: Literal["subtitles", "captions", "descriptions", "chapters", "metadata"]
        | str
        | None = None,
        label: str | None = None,
        src: str | None = None,
        srclang: str | None = None,
    ) -> Element:
        return Element("track").attr(
            default=default, kind=kind, label=label, src=src, srclang=srclang
        )

    @staticmethod
    def map(text: str | None = None, name: str | None = None) -> Element:
        return Element("map").attr(name=name).text(text)

    @staticmethod
    def area(
        alt: str | None = None,
        coords: str | None = None,
        shape: Literal["circle", "default", "poly", "rect"] | str | None = None,
        href: str | None = None,
        target: Literal["_self", "_blank", "_parent", "_top"] | str | None = None,
        download: str | None = None,
        ping: str | None = None,
        rel: str | None = None,
        hreflang: str | None = None,
        type: str | None = None,
    ) -> Element:
        return Element("area").attr(
            alt=alt,
            coords=coords,
            shape=shape,
            href=href,
            target=target,
            download=download,
            ping=ping,
            rel=rel,
            hreflang=hreflang,
            type=type,
        )

    @staticmethod
    def table(text: str | None = None, border: str | None = None) -> Element:
        return Element("table").attr(border=border).text(text)

    @staticmethod
    def caption(text: str | None = None) -> Element:
        return Element("caption").attr().text(text)

    @staticmethod
    def colgroup(text: str | None = None, span: str | None = None) -> Element:
        return Element("colgroup").attr(span=span).text(text)

    @staticmethod
    def col(span: str | None = None) -> Element:
        return Element("col").attr(span=span)

    @staticmethod
    def tbody(text: str | None = None) -> Element:
        return Element("tbody").attr().text(text)

    @staticmethod
    def thead(text: str | None = None) -> Element:
        return Element("thead").attr().text(text)

    @staticmethod
    def tfoot(text: str | None = None) -> Element:
        return Element("tfoot").attr().text(text)

    @staticmethod
    def tr(text: str | None = None) -> Element:
        return Element("tr").attr().text(text)

    @staticmethod
    def td(
        text: str | None = None,
        colspan: str | None = None,
        rowspan: str | None = None,
        headers: str | None = None,
    ) -> Element:
        return (
            Element("td")
            .attr(colspan=colspan, rowspan=rowspan, headers=headers)
            .text(text)
        )

    @staticmethod
    def th(
        text: str | None = None,
        colspan: str | None = None,
        rowspan: str | None = None,
        headers: str | None = None,
        scope: Literal["row", "col", "rowgroup", "colgroup"] | str | None = None,
        sorted: str | None = None,
        abbr: str | None = None,
    ) -> Element:
        return (
            Element("th")
            .attr(
                colspan=colspan,
                rowspan=rowspan,
                headers=headers,
                scope=scope,
                sorted=sorted,
                abbr=abbr,
            )
            .text(text)
        )

    @staticmethod
    def form(
        text: str | None = None,
        accept_charset: str | None = None,
        action: str | None = None,
        autocomplete: Literal["on", "off"] | str | None = None,
        enctype: Literal[
            "application/x-www-form-urlencoded", "multipart/form-data", "text/plain"
        ]
        | str
        | None = None,
        method: Literal["get", "post", "dialog"] | str | None = None,
        name: str | None = None,
        novalidate: Literal["true", "false"] | str | None = None,
        target: Literal["_self", "_blank", "_parent", "_top"] | str | None = None,
    ) -> Element:
        return (
            Element("form")
            .attr(
                accept_charset=accept_charset,
                action=action,
                autocomplete=autocomplete,
                enctype=enctype,
                method=method,
                name=name,
                novalidate=novalidate,
                target=target,
            )
            .text(text)
        )

    @staticmethod
    def label(
        text: str | None = None, form: str | None = None, for_: str | None = None
    ) -> Element:
        return Element("label").attr(form=form, for_=for_).text(text)

    @staticmethod
    def input(
        accept: str | None = None,
        alt: str | None = None,
        autocomplete: Literal[
            "additional-name",
            "address-level1",
            "address-level2",
            "address-level3",
            "address-level4",
            "address-line1",
            "address-line2",
            "address-line3",
            "bday",
            "bday-year",
            "bday-day",
            "bday-month",
            "billing",
            "cc-additional-name",
            "cc-csc",
            "cc-exp",
            "cc-exp-month",
            "cc-exp-year",
            "cc-family-name",
            "cc-given-name",
            "cc-name",
            "cc-number",
            "cc-type",
            "country",
            "country-name",
            "current-password",
            "email",
            "family-name",
            "fax",
            "given-name",
            "home",
            "honorific-prefix",
            "honorific-suffix",
            "impp",
            "language",
            "mobile",
            "name",
            "new-password",
            "nickname",
            "off",
            "on",
            "organization",
            "organization-title",
            "pager",
            "photo",
            "postal-code",
            "sex",
            "shipping",
            "street-address",
            "tel-area-code",
            "tel",
            "tel-country-code",
            "tel-extension",
            "tel-local",
            "tel-local-prefix",
            "tel-local-suffix",
            "tel-national",
            "transaction-amount",
            "transaction-currency",
            "url",
            "username",
            "work",
        ]
        | str
        | None = None,
        autofocus: Literal["true", "false"] | str | None = None,
        checked: Literal["true", "false"] | str | None = None,
        dirname: str | None = None,
        disabled: Literal["true", "false"] | str | None = None,
        form: str | None = None,
        formaction: str | None = None,
        formenctype: Literal[
            "application/x-www-form-urlencoded", "multipart/form-data", "text/plain"
        ]
        | str
        | None = None,
        formmethod: Literal["get", "post"] | str | None = None,
        formnovalidate: Literal["true", "false"] | str | None = None,
        formtarget: str | None = None,
        height: str | None = None,
        inputmode: Literal[
            "verbatim",
            "latin",
            "latin-name",
            "latin-prose",
            "full-width-latin",
            "kana",
            "kana-name",
            "katakana",
            "numeric",
            "tel",
            "email",
            "url",
        ]
        | str
        | None = None,
        list: str | None = None,
        max: str | None = None,
        maxlength: str | None = None,
        min: str | None = None,
        minlength: str | None = None,
        multiple: Literal["true", "false"] | str | None = None,
        name: str | None = None,
        pattern: str | None = None,
        placeholder: str | None = None,
        popovertarget: str | None = None,
        popovertargetaction: str | None = None,
        readonly: Literal["true", "false"] | str | None = None,
        required: Literal["true", "false"] | str | None = None,
        size: str | None = None,
        src: str | None = None,
        step: str | None = None,
        type: Literal[
            "hidden",
            "text",
            "search",
            "tel",
            "url",
            "email",
            "password",
            "datetime",
            "date",
            "month",
            "week",
            "time",
            "datetime-local",
            "number",
            "range",
            "color",
            "checkbox",
            "radio",
            "file",
            "submit",
            "image",
            "reset",
            "button",
        ]
        | str
        | None = None,
        value: str | None = None,
        width: str | None = None,
    ) -> Element:
        return Element("input").attr(
            accept=accept,
            alt=alt,
            autocomplete=autocomplete,
            autofocus=autofocus,
            checked=checked,
            dirname=dirname,
            disabled=disabled,
            form=form,
            formaction=formaction,
            formenctype=formenctype,
            formmethod=formmethod,
            formnovalidate=formnovalidate,
            formtarget=formtarget,
            height=height,
            inputmode=inputmode,
            list=list,
            max=max,
            maxlength=maxlength,
            min=min,
            minlength=minlength,
            multiple=multiple,
            name=name,
            pattern=pattern,
            placeholder=placeholder,
            popovertarget=popovertarget,
            popovertargetaction=popovertargetaction,
            readonly=readonly,
            required=required,
            size=size,
            src=src,
            step=step,
            type=type,
            value=value,
            width=width,
        )

    @staticmethod
    def button(
        text: str | None = None,
        autofocus: Literal["true", "false"] | str | None = None,
        disabled: Literal["true", "false"] | str | None = None,
        form: str | None = None,
        formaction: str | None = None,
        formenctype: Literal[
            "application/x-www-form-urlencoded", "multipart/form-data", "text/plain"
        ]
        | str
        | None = None,
        formmethod: Literal["get", "post"] | str | None = None,
        formnovalidate: Literal["true", "false"] | str | None = None,
        formtarget: str | None = None,
        name: str | None = None,
        popovertarget: str | None = None,
        popovertargetaction: str | None = None,
        type: Literal["button", "submit", "reset"] | str | None = None,
        value: str | None = None,
    ) -> Element:
        return (
            Element("button")
            .attr(
                autofocus=autofocus,
                disabled=disabled,
                form=form,
                formaction=formaction,
                formenctype=formenctype,
                formmethod=formmethod,
                formnovalidate=formnovalidate,
                formtarget=formtarget,
                name=name,
                popovertarget=popovertarget,
                popovertargetaction=popovertargetaction,
                type=type,
                value=value,
            )
            .text(text)
        )

    @staticmethod
    def select(
        text: str | None = None,
        autocomplete: Literal[
            "additional-name",
            "address-level1",
            "address-level2",
            "address-level3",
            "address-level4",
            "address-line1",
            "address-line2",
            "address-line3",
            "bday",
            "bday-year",
            "bday-day",
            "bday-month",
            "billing",
            "cc-additional-name",
            "cc-csc",
            "cc-exp",
            "cc-exp-month",
            "cc-exp-year",
            "cc-family-name",
            "cc-given-name",
            "cc-name",
            "cc-number",
            "cc-type",
            "country",
            "country-name",
            "current-password",
            "email",
            "family-name",
            "fax",
            "given-name",
            "home",
            "honorific-prefix",
            "honorific-suffix",
            "impp",
            "language",
            "mobile",
            "name",
            "new-password",
            "nickname",
            "off",
            "on",
            "organization",
            "organization-title",
            "pager",
            "photo",
            "postal-code",
            "sex",
            "shipping",
            "street-address",
            "tel-area-code",
            "tel",
            "tel-country-code",
            "tel-extension",
            "tel-local",
            "tel-local-prefix",
            "tel-local-suffix",
            "tel-national",
            "transaction-amount",
            "transaction-currency",
            "url",
            "username",
            "work",
        ]
        | str
        | None = None,
        autofocus: Literal["true", "false"] | str | None = None,
        disabled: Literal["true", "false"] | str | None = None,
        form: str | None = None,
        multiple: Literal["true", "false"] | str | None = None,
        name: str | None = None,
        required: Literal["true", "false"] | str | None = None,
        size: str | None = None,
    ) -> Element:
        return (
            Element("select")
            .attr(
                autocomplete=autocomplete,
                autofocus=autofocus,
                disabled=disabled,
                form=form,
                multiple=multiple,
                name=name,
                required=required,
                size=size,
            )
            .text(text)
        )

    @staticmethod
    def datalist(text: str | None = None) -> Element:
        return Element("datalist").attr().text(text)

    @staticmethod
    def optgroup(
        text: str | None = None,
        disabled: Literal["true", "false"] | str | None = None,
        label: str | None = None,
    ) -> Element:
        return Element("optgroup").attr(disabled=disabled, label=label).text(text)

    @staticmethod
    def option(
        text: str | None = None,
        disabled: Literal["true", "false"] | str | None = None,
        label: str | None = None,
        selected: Literal["true", "false"] | str | None = None,
        value: str | None = None,
    ) -> Element:
        return (
            Element("option")
            .attr(disabled=disabled, label=label, selected=selected, value=value)
            .text(text)
        )

    @staticmethod
    def textarea(
        text: str | None = None,
        autocomplete: Literal[
            "additional-name",
            "address-level1",
            "address-level2",
            "address-level3",
            "address-level4",
            "address-line1",
            "address-line2",
            "address-line3",
            "bday",
            "bday-year",
            "bday-day",
            "bday-month",
            "billing",
            "cc-additional-name",
            "cc-csc",
            "cc-exp",
            "cc-exp-month",
            "cc-exp-year",
            "cc-family-name",
            "cc-given-name",
            "cc-name",
            "cc-number",
            "cc-type",
            "country",
            "country-name",
            "current-password",
            "email",
            "family-name",
            "fax",
            "given-name",
            "home",
            "honorific-prefix",
            "honorific-suffix",
            "impp",
            "language",
            "mobile",
            "name",
            "new-password",
            "nickname",
            "off",
            "on",
            "organization",
            "organization-title",
            "pager",
            "photo",
            "postal-code",
            "sex",
            "shipping",
            "street-address",
            "tel-area-code",
            "tel",
            "tel-country-code",
            "tel-extension",
            "tel-local",
            "tel-local-prefix",
            "tel-local-suffix",
            "tel-national",
            "transaction-amount",
            "transaction-currency",
            "url",
            "username",
            "work",
        ]
        | str
        | None = None,
        autofocus: Literal["true", "false"] | str | None = None,
        cols: str | None = None,
        dirname: str | None = None,
        disabled: Literal["true", "false"] | str | None = None,
        form: str | None = None,
        inputmode: Literal[
            "verbatim",
            "latin",
            "latin-name",
            "latin-prose",
            "full-width-latin",
            "kana",
            "kana-name",
            "katakana",
            "numeric",
            "tel",
            "email",
            "url",
        ]
        | str
        | None = None,
        maxlength: str | None = None,
        minlength: str | None = None,
        name: str | None = None,
        placeholder: str | None = None,
        readonly: Literal["true", "false"] | str | None = None,
        required: Literal["true", "false"] | str | None = None,
        rows: str | None = None,
        wrap: Literal["soft", "hard"] | str | None = None,
    ) -> Element:
        return (
            Element("textarea")
            .attr(
                autocomplete=autocomplete,
                autofocus=autofocus,
                cols=cols,
                dirname=dirname,
                disabled=disabled,
                form=form,
                inputmode=inputmode,
                maxlength=maxlength,
                minlength=minlength,
                name=name,
                placeholder=placeholder,
                readonly=readonly,
                required=required,
                rows=rows,
                wrap=wrap,
            )
            .text(text)
        )

    @staticmethod
    def output(
        text: str | None = None,
        for_: str | None = None,
        form: str | None = None,
        name: str | None = None,
    ) -> Element:
        return Element("output").attr(for_=for_, form=form, name=name).text(text)

    @staticmethod
    def progress(
        text: str | None = None, value: str | None = None, max: str | None = None
    ) -> Element:
        return Element("progress").attr(value=value, max=max).text(text)

    @staticmethod
    def meter(
        text: str | None = None,
        value: str | None = None,
        min: str | None = None,
        max: str | None = None,
        low: str | None = None,
        high: str | None = None,
        optimum: str | None = None,
    ) -> Element:
        return (
            Element("meter")
            .attr(value=value, min=min, max=max, low=low, high=high, optimum=optimum)
            .text(text)
        )

    @staticmethod
    def fieldset(
        text: str | None = None,
        disabled: Literal["true", "false"] | str | None = None,
        form: str | None = None,
        name: str | None = None,
    ) -> Element:
        return (
            Element("fieldset").attr(disabled=disabled, form=form, name=name).text(text)
        )

    def legend(text: str | None = None) -> Element:
        return Element("legend").attr().text(text)

    def details(
        text: str | None = None,
        open: Literal["true", "false"] | str | None = None,
        name: str | None = None,
    ) -> Element:
        return Element("details").attr(open=open, name=name).text(text)

    def summary(text: str | None = None) -> Element:
        return Element("summary").attr().text(text)

    def dialog(text: str | None = None) -> Element:
        return Element("dialog").attr().text(text)

    def script(
        text: str | None = None,
        src: str | None = None,
        type: str | None = None,
        charset: str | None = None,
        async_: Literal["true", "false"] | str | None = None,
        defer: Literal["true", "false"] | str | None = None,
        crossorigin: Literal["anonymous", "use-credentials"] | str | None = None,
        nonce: str | None = None,
    ) -> Element:
        return (
            Element("script")
            .attr(
                src=src,
                type=type,
                charset=charset,
                async_=async_,
                defer=defer,
                crossorigin=crossorigin,
                nonce=nonce,
            )
            .text(text)
        )

    def noscript(text: str | None = None) -> Element:
        return Element("noscript").attr().text(text)

    def template(text: str | None = None) -> Element:
        return Element("template").attr().text(text)

    def canvas(
        text: str | None = None, width: str | None = None, height: str | None = None
    ) -> Element:
        return Element("canvas").attr(width=width, height=height).text(text)

    def slot(text: str | None = None, name: str | None = None) -> Element:
        return Element("slot").attr(name=name).text(text)

    def data(text: str | None = None, value: str | None = None) -> Element:
        return Element("data").attr(value=value).text(text)

    def hgroup(text: str | None = None) -> Element:
        return Element("hgroup").attr().text(text)

    def menu(text: str | None = None) -> Element:
        return Element("menu").attr().text(text)

    def search(text: str | None = None) -> Element:
        return Element("search").attr().text(text)

    def fencedframe(
        text: str | None = None,
        allow: str | None = None,
        height: str | None = None,
        width: str | None = None,
    ) -> Element:
        return (
            Element("fencedframe")
            .attr(allow=allow, height=height, width=width)
            .text(text)
        )

    def selectedcontent(text: str | None = None) -> Element:
        return Element("selectedcontent").attr().text(text)


# Utility
_html_attr_looks_like = re.compile(r"^[a-zA-Z-_][a-zA-Z0-9_-]*$")


def convert_thing_to_python_identifier(thing: str) -> str | None:
    if thing == "":
        return None
    if "_" in thing or thing[-1] == "-":
        return None

    if not thing.isidentifier():
        thing = thing.replace("-", "_")
        if not thing.isidentifier():
            return None  # some other characters causes this failure rather than hyphen

    if thing in keyword.kwlist:
        thing += "_"
    return thing


def recover_thing_from_python_identifier(python_identifier: str) -> str | None:
    "recovers what converted using `convert_thing_to_python_identifier`"
    if python_identifier == "":
        return None

    if python_identifier[-1] == "_":
        if python_identifier[-1] == "_":
            python_identifier = python_identifier[:-1]

        if python_identifier not in keyword.kwlist:
            return None

    thing = python_identifier.replace("_", "-")
    return thing


def is_valid_attr_name(attr_name: str):
    return _html_attr_looks_like.match(attr_name)


# Storage Classes
class PermanentStore(Cache):
    def __init__(self, directory=None, timeout=60, disk=None, **settings):
        # Force eviction_policy regardless of what the caller passed.
        settings["eviction_policy"] = "none"
        kwargs = {}
        if disk is not None:
            kwargs["disk"] = disk
        super().__init__(directory=directory, timeout=timeout, **kwargs, **settings)

    def set(self, key, value, expire=None, read=False, tag=None, retry=False):
        if expire is not None:
            raise ValueError(
                f"PermanentCache does not support expiry (got expire={expire!r}). "
                "This store is permanent by design — use SessionCache for TTL'd data."
            )
        return super().set(key, value, expire=None, read=read, tag=tag, retry=retry)

    def add(self, key, value, expire=None, read=False, tag=None, retry=False):
        if expire is not None:
            raise ValueError(
                f"PermanentCache does not support expiry (got expire={expire!r})."
            )
        return super().add(key, value, expire=None, read=read, tag=tag, retry=retry)

    def touch(self, key, expire=None, retry=False):
        if expire is not None:
            raise ValueError(
                f"PermanentCache does not support expiry (got expire={expire!r}). "
                "touch() with expire=None is a no-op here since keys never expire."
            )
        return super().touch(key, expire=None, retry=retry)

    def push(
        self,
        value,
        prefix=None,
        side="back",
        expire=None,
        read=False,
        tag=None,
        retry=False,
    ):
        if expire is not None:
            raise ValueError(
                f"PermanentCache does not support expiry (got expire={expire!r})."
            )
        return super().push(
            value,
            prefix=prefix,
            side=side,
            expire=None,
            read=read,
            tag=tag,
            retry=retry,
        )

    def memoize(self, name=None, typed=False, expire=None, tag=None, ignore=()):
        if expire is not None:
            raise ValueError(
                f"PermanentCache does not support expiry (got expire={expire!r})."
            )
        return super().memoize(
            name=name, typed=typed, expire=None, tag=tag, ignore=ignore
        )


class SessionStore(Cache):
    MAX_SIZE_LIMIT = 10 * 1024 * 1024 * 1024
    VALID_POLICIES = {
        "least-recently-stored",
        "least-recently-used",
        "least-frequently-used",
    }

    DEFAULT_SIZE = 512 * 1024 * 1024
    DEFAULT_EXPIRY = 3600
    DEFAULT_POLICY = "least-recently-used"

    def __init__(
        self,
        directory=None,
        size: int = DEFAULT_SIZE,
        expiry: int = DEFAULT_EXPIRY,
        policy: str = DEFAULT_POLICY,
        timeout: int = 60,
        disk=None,
        **settings,
    ):
        if size is None or size <= 0:
            raise ValueError(
                "SessionCache requires a finite, positive `size` in bytes."
            )
        if size > self.MAX_SIZE_LIMIT:
            raise ValueError(
                f"size={size} exceeds SessionCache.MAX_SIZE_LIMIT ({self.MAX_SIZE_LIMIT})."
            )
        if expiry is None or expiry <= 0:
            raise ValueError(
                "SessionCache requires a finite, positive `expiry` (seconds)."
            )
        if policy not in self.VALID_POLICIES:
            raise ValueError(
                f"policy={policy!r} is not allowed. Must be one of {sorted(self.VALID_POLICIES)}."
            )

        self._default_expiry = expiry

        settings["size_limit"] = size
        settings["eviction_policy"] = policy

        kwargs = {}
        if disk is not None:
            kwargs["disk"] = disk

        super().__init__(directory=directory, timeout=timeout, **kwargs, **settings)

        # context-scoping state — lives on the instance, not module-level,
        # so multiple SessionCache instances never share context by accident
        self._context: ContextVar[str | None] = ContextVar("session_uuid", default=None)

    # ---- context management ----

    def set_context(self, browser_uuid: str) -> Token:
        return self._context.set(browser_uuid)

    def reset_context(self, token: Token) -> None:
        self._context.reset(token)

    def _current_uuid(self) -> str:
        uuid_ = self._context.get()
        if uuid_ is None:
            raise RuntimeError(
                "No browser context set — call set_context() before using SessionCache."
            )
        return uuid_

    def _scoped(self, key) -> str:
        return f"{self._current_uuid()}:{key}"

    def _resolve_expiry(self, expire):
        if expire is None:
            return self._default_expiry
        if expire is False:
            raise ValueError(
                "SessionCache does not support non-expiring keys (expire=False)."
            )
        if expire <= 0:
            raise ValueError(f"expire must be positive, got {expire!r}.")
        return expire

    # ---- scoped overrides of Cache's core methods ----

    def set(self, key, value, expire=None, read=False, tag=None, retry=False):
        return super().set(
            self._scoped(key),
            value,
            expire=self._resolve_expiry(expire),
            read=read,
            tag=tag,
            retry=retry,
        )

    def get(
        self, key, default=None, read=False, expire_time=False, tag=False, retry=False
    ):
        return super().get(
            self._scoped(key),
            default=default,
            read=read,
            expire_time=expire_time,
            tag=tag,
            retry=retry,
        )

    def add(self, key, value, expire=None, read=False, tag=None, retry=False):
        return super().add(
            self._scoped(key),
            value,
            expire=self._resolve_expiry(expire),
            read=read,
            tag=tag,
            retry=retry,
        )

    def touch(self, key, expire=None, retry=False):
        return super().touch(
            self._scoped(key), expire=self._resolve_expiry(expire), retry=retry
        )

    def delete(self, key, retry=False):
        return super().delete(self._scoped(key), retry=retry)

    def pop(self, key, default=None, expire_time=False, tag=False, retry=False):
        return super().pop(
            self._scoped(key),
            default=default,
            expire_time=expire_time,
            tag=tag,
            retry=retry,
        )

    def has_key(self, key) -> bool:
        return key in self

    def __contains__(self, key):
        return super().__contains__(self._scoped(key))

    def __getitem__(self, key):
        return super().__getitem__(self._scoped(key))

    def __setitem__(self, key, value):
        return self.set(key, value)  # routes through set() -> enforced expiry

    def __delitem__(self, key):
        return super().__delitem__(self._scoped(key))

    def __iter__(self):
        prefix = f"{self._current_uuid()}:"
        for full_key in super().__iter__():
            if isinstance(full_key, str) and full_key.startswith(prefix):
                yield full_key[len(prefix) :]

    def __len__(self):
        prefix = f"{self._current_uuid()}:"
        return sum(
            1 for k in super().__iter__() if isinstance(k, str) and k.startswith(prefix)
        )


class ContextStore(MutableMapping):
    def __init__(self, name: str):
        self.name = name
        self._context: ContextVar[dict | None] = ContextVar(name, default=None)

    # --- context lifecycle -------------------------------------------------

    def set_context(self, value: dict) -> Token:
        return self._context.set(value)

    def reset_context(self, token: Token) -> None:
        self._context.reset(token)

    def _current_dict(self) -> dict:
        d = self._context.get()
        if d is None:
            raise RuntimeError(f"No context provided for store: {self.name}")
        return d

    # --- MutableMapping required methods -----------------------------------

    def __getitem__(self, key):
        return self._current_dict()[key]

    def __setitem__(self, key, value) -> None:
        self._current_dict()[key] = value

    def __delitem__(self, key) -> None:
        del self._current_dict()[key]

    def __iter__(self) -> Iterator:
        return iter(self._current_dict())

    def __len__(self) -> int:
        return len(self._current_dict())

    def __contains__(self, key) -> bool:
        return key in self._current_dict()

    def __repr__(self) -> str:
        try:
            return f"{self.__class__.__name__}({self.name!r}, {self._current_dict()!r})"
        except RuntimeError:
            return f"{self.__class__.__name__}({self.name!r}, <no context>)"


# Storage
PRIVATE_DIR_NAME = "ooklept_privates"
DATABASE_DIR_NAME = "ookleptdb"

APP_STORAGE_DIR_NAME = "app"
PAGE_STORAGE_DIR_NAME = "page"
USER_STORAGE_DIR_NAME = "user"
SESSION_STORAGE_DIR_NAME = "session"


PAGE_SHARD_NUM = 8


# Internal Functions


def _shard_index(key: str, num_shards: int) -> int:
    digest = hashlib.md5(key.encode()).hexdigest()
    return int(digest, 16) % num_shards


def _set_up_storage_files():
    # cwd will be the folder there serve.py acts
    cwd = os.getcwd()

    database_dir = Path(cwd) / PRIVATE_DIR_NAME / DATABASE_DIR_NAME
    database_dir.mkdir(parents=True, exist_ok=True)

    app_storage_dir = database_dir / APP_STORAGE_DIR_NAME
    app_storage_dir.mkdir(exist_ok=True)

    page_storage_dir = database_dir / PAGE_STORAGE_DIR_NAME
    page_storage_dir.mkdir(exist_ok=True)

    prev_shards = [
        i for i in os.listdir(page_storage_dir) if re.match(r"^shard_[\d]+$", i)
    ]
    if prev_shards and len(prev_shards) != PAGE_SHARD_NUM:
        raise RuntimeError(
            f"Previous sharded data in {page_storage_dir} does not match the current number: {PAGE_SHARD_NUM}, Manually clear the directory."
        )

    for i in range(PAGE_SHARD_NUM):
        (page_storage_dir / f"shard_{i}").mkdir(exist_ok=True)

    user_storage_dir = database_dir / USER_STORAGE_DIR_NAME
    user_storage_dir.mkdir(exist_ok=True)

    session_storage_dir = database_dir / SESSION_STORAGE_DIR_NAME
    session_storage_dir.mkdir(exist_ok=True)


def _get_app_store():
    p = Path(PRIVATE_DIR_NAME) / DATABASE_DIR_NAME / APP_STORAGE_DIR_NAME
    if p.exists() and p.is_dir():
        return PermanentStore(p)
    raise NotADirectoryError(
        f"{p} is not a dir. you should run `set_up_storage_files` before accessing it."
    )


def _get_user_store():
    p = Path(PRIVATE_DIR_NAME) / DATABASE_DIR_NAME / USER_STORAGE_DIR_NAME
    if p.exists() and p.is_dir():
        return PermanentStore(p)
    raise NotADirectoryError(
        f"{p} is not a dir. you should run `set_up_storage_files` before accessing it."
    )


def _get_page_store(page_path: str):
    shard = _shard_index(page_path, PAGE_SHARD_NUM)
    p = (
        Path(PRIVATE_DIR_NAME)
        / DATABASE_DIR_NAME
        / PAGE_STORAGE_DIR_NAME
        / f"shard_{shard}"
    )
    if p.exists() and p.is_dir():
        return PermanentCache(p)
    raise NotADirectoryError(
        f"{p} is not a dir. you should run `set_up_storage_files` before accessing it."
    )


def _get_session_store():
    p = Path(PRIVATE_DIR_NAME) / DATABASE_DIR_NAME / SESSION_STORAGE_DIR_NAME
    if p.exists() and p.is_dir():
        return SessionStore(p)
    raise NotADirectoryError(
        f"{p} is not a dir. you should run `set_up_storage_files` before accessing it."
    )


class Stores:
    def __init__(self):
        self._app_store = None
        self._user_store = None
        self._session_store = None
        self.get_store = ContextStore("get")
        self.post_store = ContextStore("post")
        self._page_stores: dict[int, PermanentStore] = {}

    @property
    def app_store(self):
        if self._app_store is None:
            self._app_store = _get_app_store()
        return self._app_store

    @property
    def user_store(self):
        if self._user_store is None:
            self._user_store = _get_user_store()
        return self._user_store

    @property
    def session_store(self):
        if self._session_store is None:
            self._session_store = _get_session_store()
        return self._session_store

    def page_store(self, page_path: str):
        shard = _shard_index(page_path, PAGE_SHARD_NUM)
        if shard not in self._page_stores:
            self._page_stores[shard] = _get_page_store(page_path)
        return self._page_stores[shard]


stores = Stores()


# CSRF
CSRF_SESSION_KEY = "_csrf_token"
CSRF_FIELD_NAME = "_csrf_token"
CSRF_EXEMPT_CONTENT_TYPES = {"application/json"}
CSRF_EXEMPT_PATHS = (
    set()
)  # e.g. {"webhooks/stripe.py"} for routes that legitimately receive third-party POSTs


def get_or_create_csrf_token() -> str:
    """
    Returns this session's CSRF token, generating one on first use.
    One token per session — persists across pages until the session
    ends or rotates.
    """
    existing = stores.session_store.get(CSRF_SESSION_KEY)
    if existing:
        return existing
    token = secrets.token_urlsafe(32)
    stores.session_store.set(CSRF_SESSION_KEY, token)
    return token


def verify_csrf_token(submitted: str | None) -> bool:
    expected = stores.session_store.get(CSRF_SESSION_KEY)
    if not expected or not submitted:
        return False
    return secrets.compare_digest(submitted, expected)


# Cookies

SECRET_KEY = os.environ.get("OOKLEPT_SECRET_KEY", secrets.token_hex(32)).encode()


def sign_session_id(session_id: str) -> str:
    sig = hmac.new(SECRET_KEY, session_id.encode(), hashlib.sha256).hexdigest()
    return f"{session_id}.{sig}"


def verify_session_cookie(cookie_value: str) -> str | None:
    """Returns the session_id if valid, else None."""
    try:
        session_id, sig = cookie_value.rsplit(".", 1)
    except ValueError:
        return None

    expected_sig = hmac.new(SECRET_KEY, session_id.encode(), hashlib.sha256).hexdigest()

    # constant-time comparison — prevents timing attacks on the signature check
    if hmac.compare_digest(sig, expected_sig):
        return session_id
    return None


# O
_form = tags.form


def row(
    justify: CSSPropertyTypes.justify_content = None,
    align: CSSPropertyTypes.align_items = None,
    gap: str | None = None,
):
    e = Element("div").style(display="flex", flex_direction="row")
    if justify:
        e.style(justify_content=justify)
    if align:
        e.style(align_items=align)
    if gap:
        e.style(gap=gap)
    return e


def column(
    justify: CSSPropertyTypes.justify_content = None,
    align: CSSPropertyTypes.align_items = None,
    gap: str | None = None,
):
    e = Element("div").style(display="flex", flex_direction="column")
    if justify:
        e.style(justify_content=justify)
    if align:
        e.style(align_items=align)
    if gap:
        e.style(gap=gap)
    return e


def csrf_field():
    """Call inside a `with form():` block to embed the anti-CSRF token."""
    token = get_or_create_csrf_token()
    Element("input").attr(type="hidden", name=CSRF_FIELD_NAME, value=token)


# forms upgraded with CSRF
def form(
    text: str | None = None,
    accept_charset: str | None = None,
    action: str | None = None,
    autocomplete: Literal["on", "off"] | str | None = None,
    enctype: Literal[
        "application/x-www-form-urlencoded", "multipart/form-data", "text/plain"
    ]
    | str
    | None = None,
    method: Literal["get", "post", "dialog"] | str | None = None,
    name: str | None = None,
    novalidate: Literal["true", "false"] | str | None = None,
    target: Literal["_self", "_blank", "_parent", "_top"] | str | None = None,
) -> Element:
    el = (
        Element("form")
        .attr(
            accept_charset=accept_charset,
            action=action,
            autocomplete=autocomplete,
            enctype=enctype,
            method=method,
            name=name,
            novalidate=novalidate,
            target=target,
        )
        .text(text)
    )
    if method is not None and method.strip().lower() == "post":
        with el:
            csrf_field()

    return el


app = FastAPI()

ROOT = Path.cwd()

COOKIE_NAME = "ooklet_id"
EXECUTABLE_EXTENSION = ".py"
STATIC_PREFIX = "static/"


def execute(path: str | Path, request_context: dict) -> str:
    """
    Execute an Ooklept page and return the generated HTML.
    """

    path = Path(path)

    root = Element("__root__")

    BROWSER_UUID = request_context["BROWSER_UUID"]

    get_token = stores.get_store.set_context(request_context["GET"].copy())
    post_token = stores.post_store.set_context(request_context["POST"].copy())
    session_token = stores.session_store.set_context(BROWSER_UUID)

    try:
        with root:
            runpy.run_path(path, run_name="__main__")
            # if the page called stores.session_store.rotate(), reflect the
            # new id back to the caller before we tear the context down
            rotated = stores.session_store.get_rotated_id()
            if rotated is not None:
                request_context["BROWSER_UUID"] = rotated
    finally:
        stores.get_store.reset_context(get_token)
        stores.post_store.reset_context(post_token)
        stores.session_store.reset_context(session_token)

    return "".join(str(child) for child in root._children)


@app.api_route("/{path:path}", methods=["GET", "POST"], response_class=HTMLResponse)
async def serve(path: str, request: Request):
    global ROOT

    if path == "":
        path = "index.py"

    file = (ROOT / path).resolve()

    # Prevent directory traversal
    try:
        file.relative_to(ROOT.resolve())
    except ValueError:
        raise HTTPException(403)

    if not file.exists():
        raise HTTPException(404)

    # --- static branch: serve raw bytes, never touches runpy ---
    if path.startswith(STATIC_PREFIX):
        if file.is_dir():
            raise HTTPException(404)  # no directory listing
        return FileResponse(file)
        # --- end static branch ---

    if file.is_dir():
        file = file / "index.py"

    if not file.exists():
        raise HTTPException(404)

    if file.suffix != EXECUTABLE_EXTENSION:
        raise HTTPException(404)

    # # clear local stores
    # stores.session_store.cleanup_stale_sessions()

    get_params = dict(request.query_params)
    post_params = {}

    if request.method == "POST":
        form_data = await request.form()
        post_params = dict(form_data)

    raw_cookie = request.cookies.get(COOKIE_NAME)
    session_id = verify_session_cookie(raw_cookie) if raw_cookie else None

    if session_id is None:
        session_id = str(uuid.uuid4())

    # --- CSRF check ---
    # Must run before execute(), so a forged POST never reaches page code.
    if request.method == "POST" and path not in CSRF_EXEMPT_PATHS:
        content_type = request.headers.get("content-type", "").split(";")[0].strip()

        if content_type not in CSRF_EXEMPT_CONTENT_TYPES:
            # session_id here came from verify_session_cookie above — if it was
            # None, we just minted a fresh one, which can't have a token issued
            # against it yet, so any submitted token is necessarily invalid.
            check_token = stores.session_store.set_context(session_id)
            try:
                submitted = post_params.get(CSRF_FIELD_NAME)
                token_ok = verify_csrf_token(submitted)
            finally:
                stores.session_store.reset_context(check_token)

            if not token_ok:
                raise HTTPException(403, "CSRF token missing or invalid")
    # --- end CSRF check ---

    context = {
        "GET": get_params,
        "POST": post_params,
        "BROWSER_UUID": session_id,
    }

    html = await anyio.to_thread.run_sync(execute, file, context)
    final_session_id = context["BROWSER_UUID"]
    response = HTMLResponse(html)

    response.set_cookie(
        key=COOKIE_NAME,
        value=sign_session_id(final_session_id),
        httponly=True,
        samesite="lax",
        secure=True,
    )

    return response


def main_run():
    global ROOT

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory to serve",
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--reload", action="store_true")

    args = parser.parse_args()

    ROOT = Path(args.directory).resolve()
    os.chdir(ROOT)  # Changing the directory so storage works out of the box
    _set_up_storage_files()

    uvicorn.run(
        "ooklept.serve:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        reload_dirs=[str(ROOT)],
    )


if __name__ == "__main__":
    main_run()
