#!python

import sys
sys.path.append("../..")

import os.path
import subprocess

from h11._events import *
from h11._state import *
from h11._state import (
    _SWITCH_UPGRADE, _SWITCH_CONNECT,
    EVENT_TRIGGERED_TRANSITIONS, STATE_TRIGGERED_TRANSITIONS,
)

_EVENT_COLOR = "#002092"
_STATE_COLOR = "#017517"
_SPECIAL_COLOR = "#7600a1"

HEADER = """
digraph {
  graph [fontname = "Lato" bgcolor="transparent"]
  node  [fontname = "Lato"]
  edge  [fontname = "Lato"]
"""

def finish(machine_name):
    return ("""
  labelloc="t"
  labeljust="l"
  label=<<FONT POINT-SIZE="20">h11 state machine: {}</FONT>>
}}
""".format(machine_name))

class Edges:
    def __init__(self):
        self.edges = []

    def e(self, source, target, label, color, italicize=False, weight=1):
        if italicize:
            quoted_label = f"<<i>{label}</i>>"
        else:
            quoted_label = f'<{label}>'
        self.edges.append(
            f'{source} -> {target} [\n'
            f'  label={quoted_label},\n'
            f'  color="{color}", fontcolor="{color}",\n'
            f'  weight={weight},\n'
            f']\n'
            )

    def write(self, f):
        self.edges.sort()
        f.write("".join(self.edges))

def make_dot_special_state(out_path):
    with open(out_path, "w") as f:
        f.write(HEADER)
        f.write("""
  kaT [label=<<i>keep-alive is enabled<br/>initial state</i>>]
  kaF [label=<<i>keep-alive is disabled</i>>]

  upF [label=<<i>No potential Upgrade: pending<br/>initial state</i>>]
  upT [label=<<i>Potential Upgrade: pending</i>>]

  coF [label=<<i>No potential CONNECT pending<br/>initial state</i>>]
  coT [label=<<i>Potential CONNECT pending</i>>]
""")
        edges = Edges()
        for s in ["kaT", "kaF"]:
            edges.e(s, "kaF",
                    "Request/response with<br/>HTTP/1.0 or Connection: close",
                    color=_EVENT_COLOR,
                    italicize=True)

        edges.e("upF", "upT",
                "Request with Upgrade:",
                color=_EVENT_COLOR, italicize=True)
        edges.e("upT", "upF",
                "Response",
                color=_EVENT_COLOR, italicize=True)

        edges.e("coF", "coT",
                "Request with CONNECT",
                color=_EVENT_COLOR, italicize=True)
        edges.e("coT", "coF",
                "Response without 2xx status",
                color=_EVENT_COLOR, italicize=True)

        edges.write(f)

        f.write(finish("special states"))

def make_dot(role, out_path):
    pass

my_dir = os.path.dirname(__file__)
out_dir = os.path.join(my_dir, "_static")
if not os.path.exists(out_dir):
    os.path.mkdir(out_dir)
for role in (CLIENT, SERVER):
    dot_path = os.path.join(out_dir, str(role) + ".dot")
    svg_path = dot_path[:-3] + "svg"
    make_dot(role, dot_path)
    subprocess.check_call(["dot", "-Tsvg", dot_path, "-o", svg_path])

dot_path = os.path.join(out_dir, "special-states.dot")
svg_path = dot_path[:-3] + "svg"
make_dot_special_state(dot_path)
subprocess.check_call(["dot", "-Tsvg", dot_path, "-o", svg_path])
