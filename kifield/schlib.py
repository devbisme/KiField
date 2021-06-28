# -*- coding: utf-8 -*-

#
# Much of this code was taken from https://github.com/KiCad/kicad-library-utils/tree/master/schlib.
# It's covered by GPL3.
#
# The KiCad V6-related code was developed by Dave Vandenbout and is covered by the MIT license.
#

import os.path
import re
import sys
from copy import deepcopy

import sexpdata

from .common import *


class Documentation(object):
    """
    A class to parse documentation files (dcm) of Schematic Libraries Files Format of the KiCad
    """

    def __init__(self, filename):
        self.components = {}

        dir_path = os.path.dirname(os.path.realpath(filename))
        filename = os.path.splitext(os.path.basename(filename))
        filename = os.path.join(dir_path, filename[0] + ".dcm")
        self.filename = filename

        if not os.path.isfile(filename):
            return

        f = open(filename)
        self.header = f.readline()

        if self.header and not "EESchema-DOCLIB" in self.header:
            self.header = None
            sys.stderr.write("The file is not a KiCad Documentation Library File\n")
            return

        name = None
        description = None
        keywords = None
        datasheet = None
        f.seek(0)
        for i, line in enumerate(f.readlines()):
            line = line.replace("\n", "")
            if line.startswith("$CMP "):
                name = line[5:]
                description = None
                keywords = None
                datasheet = None
            elif line.startswith("D "):
                description = line[2:]
            elif line.startswith("K "):
                keywords = line[2:]
            elif line.startswith("F "):
                datasheet = line[2:]
            elif line.startswith("$ENDCMP"):
                self.components[name] = {
                    "description": description,
                    "keywords": keywords,
                    "datasheet": datasheet,
                    "lines_range": {"start": i - 5, "end": i},
                }


class Component(object):
    """
    A class to parse components of Schematic Libraries Files Format of the KiCad
    """

    _DEF_KEYS = [
        "name",
        "reference",
        "unused",
        "text_offset",
        "draw_pinnumber",
        "draw_pinname",
        "unit_count",
        "units_locked",
        "option_flag",
    ]
    _F0_KEYS = [
        "reference",
        "posx",
        "posy",
        "text_size",
        "text_orient",
        "visibility",
        "htext_justify",
        "vtext_justify",
    ]
    _FN_KEYS = [
        "name",
        "posx",
        "posy",
        "text_size",
        "text_orient",
        "visibility",
        "htext_justify",
        "vtext_justify",
        "fieldname",
    ]
    _ARC_KEYS = [
        "posx",
        "posy",
        "radius",
        "start_angle",
        "end_angle",
        "unit",
        "convert",
        "thickness",
        "fill",
        "startx",
        "starty",
        "endx",
        "endy",
    ]
    _CIRCLE_KEYS = ["posx", "posy", "radius", "unit", "convert", "thickness", "fill"]
    _POLY_KEYS = ["point_count", "unit", "convert", "thickness", "points", "fill"]
    _RECT_KEYS = [
        "startx",
        "starty",
        "endx",
        "endy",
        "unit",
        "convert",
        "thickness",
        "fill",
    ]
    _TEXT_KEYS = [
        "direction",
        "posx",
        "posy",
        "text_size",
        "text_type",
        "unit",
        "convert",
        "text",
        "italic",
        "bold",
        "hjustify",
        "vjustify",
    ]
    _PIN_KEYS = [
        "name",
        "num",
        "posx",
        "posy",
        "length",
        "direction",
        "name_text_size",
        "num_text_size",
        "unit",
        "convert",
        "electrical_type",
        "pin_type",
    ]

    _DRAW_KEYS = {
        "arcs": _ARC_KEYS,
        "circles": _CIRCLE_KEYS,
        "polylines": _POLY_KEYS,
        "rectangles": _RECT_KEYS,
        "texts": _TEXT_KEYS,
        "pins": _PIN_KEYS,
    }
    _DRAW_ELEMS = {
        "arcs": "A",
        "circles": "C",
        "polylines": "P",
        "rectangles": "S",
        "texts": "T",
        "pins": "X",
    }

    _KEYS = {
        "DEF": _DEF_KEYS,
        "F0": _F0_KEYS,
        "F": _FN_KEYS,
        "A": _ARC_KEYS,
        "C": _CIRCLE_KEYS,
        "P": _POLY_KEYS,
        "S": _RECT_KEYS,
        "T": _TEXT_KEYS,
        "X": _PIN_KEYS,
    }

    def __init__(self, data, comments, documentation):
        self.comments = comments
        self.fplist = []
        self.aliases = []
        building_fplist = False
        building_draw = False
        for line in data:

            line = line.replace("\n", "")

            # Extract all the non-quoted and quoted text pieces, accounting for escaped quotes.
            pieces = re.findall(r'[^\s"]+|(?<!\\)".*?(?<!\\)"', line)

            line = []
            for i in range(len(pieces)):
                # Merge a piece ending with equals sign with the next piece.
                if pieces[i] and pieces[i][-1] == "=":
                    pieces[i] = pieces[i] + pieces[i + 1]
                    pieces[
                        i + 1
                    ] = ""  # Empty the next piece because it was merged with this one.
                # Append any non-empty piece.
                if pieces[i]:
                    line.append(pieces[i])

            if line[0] in self._KEYS:
                key_list = self._KEYS[line[0]]
                values = line[1:] + ["" for n in range(len(key_list) - len(line[1:]))]

            if line[0] == "DEF":
                self.definition = dict(zip(self._DEF_KEYS, values))

            elif line[0] == "F0":
                self.fields = []
                self.fields.append(dict(zip(self._F0_KEYS, values)))

            elif line[0][0] == "F":
                values = line[1:] + [
                    "" for n in range(len(self._FN_KEYS) - len(line[1:]))
                ]
                self.fields.append(dict(zip(self._FN_KEYS, values)))

            elif line[0] == "ALIAS":
                self.aliases = [alias for alias in line[1:]]

            elif line[0] == "$FPLIST":
                building_fplist = True
                self.fplist = []

            elif line[0] == "$ENDFPLIST":
                building_fplist = False

            elif line[0] == "DRAW":
                building_draw = True
                self.draw = {
                    "arcs": [],
                    "circles": [],
                    "polylines": [],
                    "rectangles": [],
                    "texts": [],
                    "pins": [],
                }

            elif line[0] == "ENDDRAW":
                building_draw = False

            else:
                if building_fplist:
                    self.fplist.append(line[0])

                elif building_draw:
                    if line[0] == "A":
                        self.draw["arcs"].append(dict(zip(self._ARC_KEYS, values)))
                    if line[0] == "C":
                        self.draw["circles"].append(
                            dict(zip(self._CIRCLE_KEYS, values))
                        )
                    if line[0] == "P":
                        n_points = int(line[1])
                        points = line[5 : 5 + (2 * n_points)]
                        values = line[1:5] + [points]
                        if len(line) > (5 + len(points)):
                            values += [line[-1]]
                        else:
                            values += [""]
                        self.draw["polylines"].append(
                            dict(zip(self._POLY_KEYS, values))
                        )
                    if line[0] == "S":
                        self.draw["rectangles"].append(
                            dict(zip(self._RECT_KEYS, values))
                        )
                    if line[0] == "T":
                        self.draw["texts"].append(dict(zip(self._TEXT_KEYS, values)))
                    if line[0] == "X":
                        self.draw["pins"].append(dict(zip(self._PIN_KEYS, values)))

        # define some shortcuts
        self.name = self.definition["name"]
        self.reference = self.definition["reference"]
        self.pins = self.draw["pins"]

        # get documentation
        try:
            self.documentation = documentation.components[self.name]
        except KeyError:
            self.documentation = {}

    def getPinsByName(self, name):
        pins = []
        for pin in self.pins:
            if pin["name"] == name:
                pins.append(pin)

        return pins

    def getPinByNumber(self, num):
        for pin in self.draw["pins"]:
            if pin["num"] == str(num):
                return pin

        return None

    def filterPins(self, name=None, direction=None, electrical_type=None):
        pins = []

        for pin in self.pins:
            if (
                (name and pin["name"] == name)
                or (direction and pin["direction"] == direction)
                or (electrical_type and pin["electrical_type"] == electrical_type)
            ):
                pins.append(pin)

        return pins


class SchLib(object):
    """
    A class to parse Schematic Libraries Files Format of the KiCad
    """

    def __init__(self, filename, create=False):
        self.filename = filename
        self.header = []
        self.components = []

        documentation = Documentation(filename)
        self.documentation_filename = documentation.filename

        if create:
            if not os.path.isfile(filename):
                f = open(filename, "w")
                self.header = ["EESchema-LIBRARY Version 2.3\n", "#encoding utf-8\n"]
                return

        f = open(filename)
        self.header = [f.readline()]

        if self.header and not "EESchema-LIBRARY" in self.header[0]:
            self.header = None
            sys.stderr.write("The file is not a KiCad Schematic Library File\n")
            return

        building_component = False

        comments = []
        for i, line in enumerate(f.readlines()):
            if line.startswith("#"):
                comments.append(line)

            elif line.startswith("DEF"):
                building_component = True
                component_data = []
                component_data.append(line)

            elif building_component:
                component_data.append(line)
                if line.startswith("ENDDEF"):
                    building_component = False
                    self.components.append(
                        Component(component_data, comments, documentation)
                    )
                    comments = []

    def getComponentByName(self, name):
        for component in self.components:
            if component.definition["name"] == name:
                return component

        return None

    def save(self, filename=None):
        # check whether it has header, what means that schlib file was loaded fine
        if not self.header:
            return

        if not filename:
            filename = self.filename

        # insert the header
        to_write = self.header

        # insert the components
        for component in self.components:
            # append the component comments
            to_write += component.comments

            # DEF
            line = "DEF "
            for key in Component._DEF_KEYS:
                line += component.definition[key] + " "

            line = line.rstrip() + "\n"
            to_write.append(line)

            # FIELDS
            line = "F"
            for i, f in enumerate(component.fields):
                line = "F" + str(i) + " "

                if i == 0:
                    keys_list = Component._F0_KEYS
                else:
                    keys_list = Component._FN_KEYS

                for key in keys_list:
                    line += component.fields[i][key] + " "

                line = line.rstrip() + "\n"
                to_write.append(line)

            # ALIAS
            if len(component.aliases) > 0:
                line = "ALIAS "
                for alias in component.aliases:
                    line += alias + " "

                line = line.rstrip() + "\n"
                to_write.append(line)

            # $FPLIST
            if len(component.fplist) > 0:
                to_write.append("$FPLIST\n")
                for fp in component.fplist:
                    to_write.append(" " + fp + "\n")

                # $ENDFPLIST
                to_write.append("$ENDFPLIST\n")

            # DRAW
            to_write.append("DRAW\n")
            for elem in component.draw.items():
                for item in component.draw[elem[0]]:
                    keys_list = Component._DRAW_KEYS[elem[0]]
                    line = Component._DRAW_ELEMS[elem[0]] + " "
                    for k in keys_list:
                        if k == "points":
                            for i in item["points"]:
                                line += i + " "
                        else:
                            line += item[k] + " "

                    line = line.rstrip() + "\n"
                    to_write.append(line)

            # ENDDRAW
            to_write.append("ENDDRAW\n")

            # ENDDEF
            to_write.append("ENDDEF\n")

        # insert the footer
        to_write.append("#\n")
        to_write.append("#End Library\n")

        # Remove all CR, LF from each line and re-append LF to the line.
        # This prevents errors caused by an internal CR, LF breaking a line.
        to_write = [re.sub(r"[\n\r]", "", l) + "\n" for l in to_write]

        f = open(filename, "w")
        f.writelines(to_write)


class Component_V6(object):
    """
    A class to parse components of KiCad V6 Schematic Files.
    """

    def __init__(self, data):
        self.data = data

        self.name = unquote(data[1])

        self.fields = []
        for prop in find_by_key("property", data):
            id = get_value_by_key("id", prop)
            self.fields.append(
                {
                    "name": unquote(prop[1]),
                    "value": unquote(prop[2]),
                    "id": id,
                    "prop": prop,
                }
            )

    def get_field_names(self):
        """Return the set of all the field names found in a component."""

        return {f["name"] for f in self.fields}

    def get_ref(self):
        """Return the reference for a component."""

        return [f["value"] for f in self.fields if f["name"] == "Reference"][0]

    def get_field(self, field_name):
        for field in self.fields:
            if field["name"] == field_name:
                return field
        return None

    def set_field_value(self, field_name, value):
        """Set the value of a component field."""
        field = self.get_field(field_name)
        field["value"] = value
        field["prop"][2] = value

    def set_ref(self, ref):
        """Set the component reference identifier."""
        self.set_field_value("Reference", ref)

    def set_field_visibility(self, field_name, visible):
        """Set the visibility of a component field."""

        # Leave visibility unaffected if passed None.
        if visible == None:
            return

        field = self.get_field(field_name)
        if field:
            effects = find_by_key("effects", field["prop"])[0]
            if effects:
                try:
                    effects.remove(sexpdata.Symbol("hide"))
                except ValueError:
                    pass
                if not visible:
                    effects.append(sexpdata.Symbol("hide"))

    def get_field_pos(self, field_name):
        field = self.get_field(field_name)
        if field:
            at = find_by_key("at", field["prop"])[0]
            if at:
                return at[1:4]

    def set_field_pos(self, field_name, pos):
        field = self.get_field(field_name)
        if field:
            at = find_by_key("at", field["prop"])[0]
            if at:
                at[1:4] = pos[:]

    def copy_field(self, src, dst):
        """Add a copy of a component field with a different name."""
        src_field = self.get_field(src)
        if not src_field:
            return
        dst_field = self.get_field(dst)
        if not dst_field:
            dst_field = deepcopy(src_field)
            dst_field["name"] = dst
            dst_field["id"] = len(self.fields)
            dst_field["prop"][1] = dst
            id = find_by_key("id", dst_field["prop"])[0]
            id[1] = dst_field["id"]
            self.fields.append(dst_field)
        else:
            dst_field["prop"] = deepcopy(src_field["prop"])
        self.set_field_value(dst, src_field["value"])
        self.data.append(dst_field["prop"])

    def del_field(self, field_name):
        """Delete a component field."""
        for i, field in enumerate(self.fields):
            if field["name"] == field_name:
                prop = field["prop"]
                del self.fields[i]
                for j, elem in enumerate(self.data):
                    if elem is prop:
                        del self.data[j]
                        return


class SchLib_V6(object):
    """A class to parse KiCad V6 schematic symbol libraries."""

    def __init__(self, filename):

        # Parse the library file into a nested list.
        with open(filename) as fp:
            try:
                self.sexpdata = sexpdata.loads("\n".join(fp.readlines()))
                if self.sexpdata[0].value() != "kicad_symbol_lib":
                    raise AssertionError
            except AssertionError:
                sys.stderr.write("The file is not a KiCad V6 Schematic Library File\n")
                return

        self.filename = filename

        # Get any components included in this schematic file.
        self.components = [
            Component_V6(comp) for comp in find_by_key("symbol", self.sexpdata)
        ]

    def get_field_names(self):
        """Return a list all the field names found in a library's components."""

        field_names = set()

        # Add field names from each component.
        for component in self.components:
            field_names.update(component.get_field_names())

        return list(field_names)

    def save(self, backup=True, filename=None):
        """Save schematic in a file."""

        if not filename:
            filename = self.filename

        if backup:
            create_backup(filename)

        with open(filename, "w") as fp:
            fp.write(sexp_indent(sexpdata.dumps(self.sexpdata)))
