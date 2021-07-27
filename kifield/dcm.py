# -*- coding: utf-8 -*-

# MIT License / Copyright (c) 2021 by Dave Vandenbout.


import re
import sys


class Component(object):
    def __init__(self):

        self.name = None
        self.description = None
        self.keywords = None
        self.docfile = None

    def read(self, file):

        while True:
            line = file.readline()
            if not line:
                return False
            mtch = re.match(r"^(?P<tag>[$\w]+)\s+(?P<contents>.*)$", line)
            if mtch:
                tag = str(mtch.group("tag").upper())
                contents = str(mtch.group("contents"))
                if tag == r"$CMP":
                    self.name = contents
                elif tag == "D":
                    self.description = contents
                elif tag == "K":
                    self.keywords = contents
                elif tag == "F":
                    self.docfile = contents
                elif tag == r"$ENDCMP":
                    return True
            elif re.match(r"^\$ENDCMP\s*$", line):
                return True

    def str(self):
        s = []
        if self.name is None:
            return s
        s.append("#\n")
        s.append("$CMP " + self.name + "\n")
        if self.description is not None and len(self.description) > 0:
            s.append("D " + self.description + "\n")
        if self.keywords is not None and len(self.keywords) > 0:
            s.append("K " + self.keywords + "\n")
        if self.docfile is not None and len(self.docfile) > 0:
            s.append("F " + self.docfile + "\n")
        s.append("$ENDCMP\n")
        s.append("#\n")
        return s


class Dcm(object):
    """
    A class to parse description files for KiCad schematic libraries.
    """

    def __init__(self, filename=None):

        self.filename = filename
        self.header = "EESchema-DOCLIB  Version 2.0\n"
        self.components = []

        if filename is None:
            return

        with open(filename) as file:
            self.header = file.readline()

            if not self.header.startswith("EESchema-DOCLIB"):
                self.header = None
                sys.stderr.write(
                    "The file is not a KiCad schematic library description file\n"
                )
                return

            while True:
                c = Component()
                if c.read(file):
                    self.components.append(c)
                else:
                    break

    def save(self, filename=None):

        if not filename:
            filename = self.filename

        # Insert the header.
        to_write = [self.header]

        # Insert components.
        for c in self.components:
            to_write.extend(c.str())

        with open(filename, "w") as file:
            file.writelines(to_write)
