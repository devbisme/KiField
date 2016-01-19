# MIT license
#
# Copyright (C) 2016 by XESS Corporation.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()

import argparse
import os
import sys
import logging
from .kifield import *
from . import __version__


###############################################################################
# Command-line interface.
###############################################################################

def main():
    parser = argparse.ArgumentParser(
        description='Insert fields from spreadsheets into KiCad schematics, or gather fields from schematics and place them into a spreadsheet.')
    parser.add_argument('--version', '-v',
                        action='version',
                        version='KiField ' + __version__)
    parser.add_argument('--extract', '-x',
                        nargs='+',
                        type=str,
                        metavar='file.[xlsx|csv|sch]',
                        help='Extract field values from one or more spreadsheet or schematic files.')
    parser.add_argument('--insert', '-i',
                        nargs='+',
                        type=str,
                        metavar='file.[xlsx|csv|sch]',
                        help='Insert extracted field values into one or more schematic or spreadsheet files.')
    parser.add_argument('--overwrite', '-w',
                        action='store_true',
                        help='Allow field insertion into an existing file.')
    parser.add_argument('--fields', '-f',
                        nargs='+',
                        type=str,
                        default=None,
                        metavar='name',
                        help='Specify the names of the fields to extract and insert.')
    parser.add_argument(
        '--debug', '-d',
        nargs='?',
        type=int,
        default=0,
        metavar='LEVEL',
        help='Print debugging info. (Larger LEVEL means more info.)')

    args = parser.parse_args()

    if args.insert is None:
        print('Hey! I need some place to insert the fields!')
        sys.exit(1)

    for file in args.insert:
        if os.path.isfile(file):
            if not args.overwrite:
                print('File {} already exists! Use the --overwrite option to allow modifications to it.'.format(file))
                sys.exit(1)

    if args.extract is None:
        print('Hey! Give me some files to extract field values from!')
        sys.exit(2)

    logger = logging.getLogger('kifield')
    if args.debug is not None:
        log_level = logging.DEBUG - args.debug
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(log_level)
        logger.addHandler(handler)
        logger.setLevel(log_level)

    kifield(extract_filenames=args.extract, insert_filenames=args.insert, field_names=args.fields)


###############################################################################
# Main entrypoint.
###############################################################################
if __name__ == '__main__':
    main()
