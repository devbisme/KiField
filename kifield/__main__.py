# -*- coding: utf-8 -*-

# MIT License / Copyright (c) 2021 by Dave Vandenbout.

from __future__ import absolute_import, division, print_function, unicode_literals

import argparse
import logging
import os
import shutil
import sys

from future import standard_library

from .kifield import *
from .pckg_info import __version__

standard_library.install_aliases()


###############################################################################
# Command-line interface.
###############################################################################


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Insert fields from spreadsheets into KiCad schematics or libraries, "
            "or gather fields from schematics or libraries and place them into "
            "a spreadsheet."
        )
    )
    parser.add_argument(
        "--extract",
        "-x",
        nargs="+",
        type=str,
        metavar="file",
        help="Extract field values from one or more XLSX, CSV, TSV, SCH, LIB or DCM files.",
    )
    parser.add_argument(
        "--insert",
        "-i",
        nargs="+",
        type=str,
        metavar="file",
        help="Insert field values into one or more XLSX, CSV, TSV, SCH, LIB or DCM files.",
    )
    parser.add_argument(
        "--recurse",
        "-r",
        action="store_true",
        help="Allow recursion from a top-level schematic into lower-level sub-schematics.",
    )
    parser.add_argument(
        "--fields",
        "-f",
        nargs="+",
        type=str,
        default=[],
        metavar="name|/name|~name",
        help=(
            "Specify the names of the fields to extract and insert. "
            "Place a '/' or '~' in front of a field you wish to omit. "
            "(Leave blank to extract/insert *all* fields.)"
        ),
    )
    parser.add_argument(
        "--overwrite",
        "-w",
        action="store_true",
        help="Allow field insertion into an existing file.",
    )
    parser.add_argument(
        "--nobackup",
        "-nb",
        action="store_true",
        help="Do *not* create backups before modifying files. (Default is to make backup files.)",
    )
    parser.add_argument(
        "--group",
        "-g",
        action="store_true",
        help=(
            "Group components with the same field values into single lines when "
            "inserting into a spreadsheet or CSV/TSV. "
            "(Default is to have one component per line)"
        ),
    )
    parser.add_argument(
        "--norange",
        "-nr",
        action="store_true",
        help=(
            "Disable hyphenated ranges when components are grouped, explicitly showing each component in a group."
        ),
    )
    parser.add_argument(
        "--debug",
        "-d",
        nargs="?",
        type=int,
        default=0,
        metavar="LEVEL",
        help="Print debugging info. (Larger LEVEL means more info.)",
    )
    parser.add_argument(
        "--version", "-v", action="version", version="KiField " + __version__
    )

    args = parser.parse_args()

    logger = logging.getLogger("kifield")
    if args.debug is not None:
        log_level = logging.DEBUG + 1 - args.debug
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(log_level)
        logger.addHandler(handler)
        logger.setLevel(log_level)

    if args.extract is None:
        logger.critical("Hey! Give me some files to extract field values from!")
        sys.exit(2)

    if args.insert is None:
        print("Hey! I need some files where I can insert the field values!")
        sys.exit(1)

    for file in args.insert:
        if os.path.isfile(file):
            if not args.overwrite and args.nobackup:
                logger.critical(
                    """File {} already exists! Use the --overwrite option to
                    allow modifications to it or allow backups.""".format(
                        file
                    )
                )
                sys.exit(1)

    inc_fields = []
    exc_fields = []
    for f in args.fields:
        if f[0] in [r"/", r"~"]:
            exc_fields.append(f[1:])
        else:
            inc_fields.append(f)

    kifield(
        extract_filenames=args.extract,
        insert_filenames=args.insert,
        inc_field_names=inc_fields,
        exc_field_names=exc_fields,
        group_components=args.group,
        no_range=args.norange,
        recurse=args.recurse,
        backup=not args.nobackup,
    )


###############################################################################
# Main entrypoint.
###############################################################################
if __name__ == "__main__":
    main()
