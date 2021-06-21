# -*- coding: utf-8 -*-

# MIT License / Copyright (c) 2021 by XESS Corporation.

import sys
import logging

USING_PYTHON2 = sys.version_info.major == 2
USING_PYTHON3 = not USING_PYTHON2

if USING_PYTHON2:
    reload(sys)
    sys.setdefaultencoding("utf8")
else:
    # Python3 doesn't have basestring, so create one.
    basestring = type("")


DEBUG_OVERVIEW = logging.DEBUG
DEBUG_DETAILED = logging.DEBUG - 1
DEBUG_OBSESSIVE = logging.DEBUG - 2


def sexp_indent(s, tab="    "):
    """Add linebreaks and indents to an S-expression."""

    out_s = ""
    indent = ""
    nl = ""  # First '(' will not be preceded by a newline.
    in_quote = False
    backslash = False

    for c in s:
        if c == "(" and not in_quote:
            out_s += nl + indent
            nl = "\n"  # Every '(' from now on gets preceded by a newline.
            indent += tab
        elif c == ")" and not in_quote:
            indent = indent[len(tab) :]
        elif c == '"' and not backslash:
            in_quote = not in_quote

        if c == "\\":
            backslash = True
        else:
            backslash = False

        out_s += c

    return out_s
