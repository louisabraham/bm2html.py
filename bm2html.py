#!/usr/bin/env python3

"""
The MIT License (MIT)
Copyright (c) 2016 Louis Abraham <louis.abraham@yahoo.fr>

\x1B[34m\033[F\033[F

bm2html.py exports Google Chrome bookmarks to a nice html
file that uses only CSS to render the folder arborescence.

\x1B[0m\033[1m\033[F\033[F

example of usage:

    bm2html.py > bookmarks.html

\033[0m\033[F\033[F
"""


import json
from html import escape
import urllib.parse
import os
import argparse


class CustomFormatter(
    argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter
):
    pass


parser = argparse.ArgumentParser(
    prog="bmk", description=__doc__, formatter_class=CustomFormatter
)
parser.add_argument(
    "path",
    nargs="?",
    default="~/Library/Application Support/Google/Chrome/Profile 1/Bookmarks",
    help="path of your Chrome bookmarks file",
)
parser.add_argument("--folders", nargs="+", help="extract only those folders")
parser.add_argument(
    "--include-hidden", action="store_true", help="include folders prefixed with a dot"
)
parser.add_argument(
    "--hide-netloc", action="store_true", help="hide the base url of the site"
)

CSSSTYLE = """<style>
    * {
        font-family: monospace;
    }
    label {
        font-weight: bold;
    }
    a {
        color: black;
    }
    a:hover {
        background: #dddddd;
    }
    input {
        display: none;
    }
    input~ul {
        display: none;
    }
    input:checked~ul {
        display: block;
    }
    input~.f {
        display: block;
    }
    input:checked~.f {
        display: none;
    }
    .f:hover {
        background: #e6ffed;
    }
    input~.s {
        display: none;
    }
    input:checked~.s {
        display: block;
    }
    .s:hover {
        background: #ffeef0;
    }
    #show-all:checked~ul ul {
        display: block;
    }
    #show-all:checked~ul .f {
        display: none;
    }
    #show-all:checked~ul .s {
        display: block;
    }
</style>
"""

CHECKBOX = (
    '<input type="checkbox" id="{id}"/>'
    '<label class="f" for="{id}">{name} [+]</label>'
    '<label class="s" for="{id}">{name} [-]</label>'
)

SHOW_ALL = (
    '<input type="checkbox" id="show-all"/><label for="show-all">'
    "Show all ! (useful on small screens)"
    "</label><br><br>\n"
)


def encode(text):
    return escape(text).encode("ascii", "xmlcharrefreplace").decode()


def netloc(url):
    return urllib.parse.urlsplit(url).netloc


def make_list(elements):
    contents = "\n".join("<li>%s</li>" % el for el in elements)
    return "<ul>\n%s\n</ul>" % contents


def selected(node):
    if node["type"] != "folder":
        return True
    elif node["name"].startswith("."):
        return args.include_hidden
    return True


def convert(j):
    global number
    t = j["type"]
    if t == "url":
        number += 1
        ans = '<a href="%s">%s</a>' % (j["url"], encode(j["name"]))
        if not args.hide_netloc:
            ans += " (%s)" % netloc(j["url"])
        return ans
    elif t == "folder":
        return CHECKBOX.format(id=j["id"], name=encode(j["name"])) + make_list(
            map(convert, filter(selected, j["children"]))
        )


def extract_folders(j):
    t = j["type"]
    if t == "url":
        return ""
    elif t == "folder":
        if j["name"] in args.folders:
            return convert(j)
        return "".join(extract_folders(i) for i in j["children"])


if __name__ == "__main__":

    args = parser.parse_args()
    args.path = os.path.expanduser(args.path)
    args.folders = set(args.folders or {})

    with open(args.path) as fd:
        json_tree = json.load(fd)["roots"]["other"]

    number = 0
    html = extract_folders(json_tree) if args.folders else convert(json_tree)

    print(CSSSTYLE + "There are %s links.<br><br>\n" % number + SHOW_ALL + html)
