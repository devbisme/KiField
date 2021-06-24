# -*- coding: utf-8 -*-

# MIT License / Copyright (c) 2021 by XESS Corporation.

import logging
import os
import re
import shutil
import sys

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


def quote(s):
    """Surround a string with quote marks."""

    if s is None:
        return s

    # Place a backslash before every double-quote and then remove a backslash
    # from any quote with two backslashes because it already had one.
    escq = re.sub(r'"', r"\"", s)
    escq = re.sub(r'\\\\"', r"\"", escq)

    # Surround with double quotes.
    return '"' + escq + '"'


def unquote(s):
    """Remove any quote marks around a string."""

    if not isinstance(s, basestring):
        return s  # Not a string, so just return it.
    try:
        # This returns inner part of "..." or '...' strings.
        return re.match("^(['\"])(.*)\\1$", s).group(2)
    except (IndexError, AttributeError):
        # No surrounding quotes, so just return string.
        return s


def explode(collapsed):
    """Explode references like 'C1-C3,C7,C10-C13' into [C1,C2,C3,C7,C10,C11,C12,C13]"""

    if collapsed == "":
        return []
    individual_refs = []
    if isinstance(collapsed, basestring):
        range_refs = re.split(",|;", collapsed)
        for r in range_refs:
            mtch = re.match(
                "^\s*(?P<part_prefix>\D+)(?P<range_start>\d+)\s*[-:]\s*\\1(?P<range_end>\d+)\s*$",
                r,
            )
            if mtch is None:
                individual_refs.append(r.strip())
            else:
                part_prefix = mtch.group("part_prefix")
                range_start = int(mtch.group("range_start"))
                range_end = int(mtch.group("range_end"))
                for i in range(range_start, range_end + 1):
                    individual_refs.append(part_prefix + str(i))
    return individual_refs


def collapse(individual_refs):
    """
    Collapse references like [C1,C2,C3,C7,C10,C11,C12,C13] into
    'C1-C3, C7, C10-C13'
    """

    parts = []
    for ref in individual_refs:
        mtch = re.match("(?P<part_prefix>\D+)(?P<number>\d+)", ref)
        if mtch is not None:
            part_prefix = mtch.group("part_prefix")
            number = int(mtch.group("number"))
            parts.append((part_prefix, number))

    parts.sort()

    def toRef(part):
        return "{}{}".format(part[0], part[1])

    def make_groups(accumulator, part):
        prev = None
        if len(accumulator) > 0:
            group = accumulator[-1]
            if len(group) > 0:
                prev = group[-1]
        if (prev != None) and (prev[0] == part[0]) and ((prev[1] + 1) == part[1]):
            group.append(part)
            accumulator[-1] = group
        else:
            accumulator.append([part])
        return accumulator

    groups = reduce(make_groups, parts, [])
    groups = map(lambda g: tuple(map(toRef, g)), groups)

    collapsed = ""
    for group in groups:
        if (len(collapsed) > 1) and (collapsed[-2] != ","):
            collapsed += ", "
        if len(group) > 2:
            collapsed += group[0] + "-" + group[-1]
        else:
            collapsed += ", ".join(group)

    return collapsed


# Stores list of file names that have been backed-up before modification.
backedup_files = []


def create_backup(file):
    """Create a backup copy of a file before it gets modified."""
    if file in backedup_files:
        return

    if not os.path.isfile(file):
        return

    index = 1  # Start with this backup file suffix.
    while True:
        backup_file = "{}.{}.bak".format(file, index)
        if not os.path.isfile(backup_file):
            # Found an unused backup file name, so make backup.
            shutil.copy(file, backup_file)
            break  # Backup done, so break out of loop.
        index += 1  # Else keep looking for an unused backup file name.
    backedup_files.append(file)
