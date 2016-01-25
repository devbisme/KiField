# MIT license
#
# Copyright (C) 2016 by XESS Corporation
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
from builtins import open
from builtins import range
from builtins import int
from builtins import str
from future import standard_library
standard_library.install_aliases()

import sys
import os
import re
import operator
import csv
import logging
from copy import deepcopy
from pprint import pprint
from difflib import get_close_matches
import openpyxl as pyxl
from .sch import Schematic
from .schlib import SchLib
import pdb

logger = logging.getLogger('kifield')

DEBUG_OVERVIEW = logging.DEBUG
DEBUG_DETAILED = logging.DEBUG-1
DEBUG_OBSESSIVE = logging.DEBUG-2

# Assign some names to the unnamed fields in a schematic or library component.
sch_field_id_to_name = {'1': 'value', '2': 'footprint', '3': 'datasheet'}
sch_field_name_to_id = {v: k for k, v in sch_field_id_to_name.items()}
lib_field_id_to_name = {'0': 'prefix', '1': 'value', '2': 'footprint', '3': 'datasheet'}
lib_field_name_to_id = {v: k for k, v in lib_field_id_to_name.items()}


def quote(s):
    '''Surround a string with quote marks.'''
    if s is None:
        return s
    return '"' + str(s) + '"'


def unquote(s):
    '''Remove any quote marks around a string.'''
    if type(s) not in (type(u''), str):
        return s
    try:
        # This returns inner part of "..." or '...' strings.
        return re.match('^([\'"])(.*)\\1$', s).group(2)
    except (IndexError, AttributeError):
        # Just return an unquoted string.
        return s


def explode(ref):
    '''Explode references like 'C1-C3,C7,C10-C13' into [C1,C2,C3,C7,C10,C11,C12,C13]'''

    individual_refs = []
    if type(ref) in (type(u''), str):
        range_refs = re.split(',|;', ref)
        for r in range_refs:
            mtch = re.match(
                '^(?P<part_prefix>\D+)(?P<range_start>\d+)[-:]\1(?P<range_end>\d+)$',
                r)
            if mtch is None:
                individual_refs.append(r)
            else:
                part_prefix = mtch.group('part_prefix')
                range_start = int(mtch.group('range_start'))
                range_end = int(mtch.group('range_end'))
                for i in range(range_start, range_end + 1):
                    individual_refs.append(part_prefix + str(i))
    logger.log(DEBUG_OBSESSIVE, 'Exploding {} => {}.'.format(ref, individual_refs))
    return individual_refs


def csvfile_to_wb(csv_filename):
    '''Open a CSV file and return an openpyxl workbook.'''

    logger.log(DEBUG_DETAILED, 'Converting CSV file {} into an XLSX workbook.'.format(csv_filename))
    with open(csv_filename) as csv_file:
        reader = csv.reader(csv_file)
        wb = pyxl.Workbook()
        ws = wb.active
        for row_index, row in enumerate(reader, 1):
            for column_index, cell in enumerate(row, 1):
                if cell not in ('', None):
                    ws.cell(row=row_index, column=column_index).value = cell
    return wb


def wb_to_csvfile(wb, csv_filename):
    '''Save an openpyxl workbook as a CSV file.'''

    logger.log(DEBUG_DETAILED, 'Converting an XLSX workbook and saving as CSV file {}.'.format(csv_filename))
    ws = wb.active
    mode = 'w'
    if sys.version_info.major < 3:
        mode += 'b'
    with open(csv_filename, mode) as csv_file:
        writer = csv.writer(csv_file, lineterminator='\n')
        for row in ws.rows:
            writer.writerow([cell.value for cell in row])


class FieldExtractionError(Exception):
    pass


class FindLabelError(Exception):
    pass


def find_header(ws):
    '''Find the spreadsheet row that most likely contains the field headers.'''
    # Look for the first occurrence of the row with the most entries.
    # That's probably the header row.
    max_width = 0
    header_row_num = 0
    header = []
    r = enumerate(ws.rows, 1)
    for row_num, row in r:
        width = len(row) - [c.value for c in row].count(None)
        if width > max_width:
            max_width = width
            header_row_num = row_num
            header = [cell for cell in row]
    logger.log(DEBUG_DETAILED, 'Header on row {}: {}.'.format(header_row_num, [c.value for c in header]))
    return header_row_num, header


def find_header_column(header, lbl):
    '''Find the field header column containing the closest match to the given label.'''
    header_labels = [cell.value for cell in header]
    lbl_match = get_close_matches(lbl, header_labels, 1, 0.0)[0]
    for cell in header:
        if str(cell.value).lower() == lbl_match.lower():
            logger.log(DEBUG_OBSESSIVE, 'Found {} on header column {}.'.format(lbl, cell.column))
            return pyxl.cell.column_index_from_string(cell.column)
    raise FindLabelError('{} not found in spreadsheet'.format(lbl))


def extract_part_fields_from_wb(wb, field_names):
    part_fields = {}
    try:
        ws = wb.active
        # Find the header with the part field labels.
        header_row, header = find_header(ws)
        # Find the column with the part references.
        refs_c = find_header_column(header, 'references')
        # Get the list of part references.
        refs = [r.value for r in ws.columns[refs_c - 1][header_row:]]
        # Get the column for each field name that can be found.
        field_cols = {}
        if field_names is None or len(field_names) == 0:
            # Use the header labels if the list of field names is empty.
            field_cols = {c.value: pyxl.cell.column_index_from_string(c.column)
                          for c in header}
            # Get rid of the extra references field in field_cols.
            del field_cols[ws.cell(row=header_row, column=refs_c).value]
        else:
            for field_name in field_names:
                try:
                    field_cols[field_name] = find_header_column(header,
                                                                field_name)
                except FindLabelError:
                    logger.warn('No field matching {} found in this worksheet.'.format(field_name))
                    pass  # Skip fields that can't be found in this sheet.
        # Get the field values for each part reference.
        for row, ref in enumerate(refs, header_row + 1):
            if ref is None:
                continue  # Skip lines with no part reference.
            # Get the field values from the row of the current part reference.
            field_values = {}
            for field_name, col in field_cols.items():
                value = ws.cell(row=row, column=col).value
                if value is not None:
                    field_values[field_name] = value
                else:
                    field_values[field_name] = ''
            # Explode the part reference into its individual references and
            # assign the field values to each part.
            for single_ref in explode(ref):
                part_fields[single_ref] = field_values
    except FindLabelError:
        logger.warn('No references column found.')
        raise FieldExtractionError

    if logger.isEnabledFor(DEBUG_DETAILED):
        print('Extracted Part Fields:')
        pprint(part_fields)

    return part_fields


def extract_part_fields_from_xlsx(filename, field_names):
    logger.log(DEBUG_OVERVIEW, 'Extracting fields {} from XLSX file {}.'.format(field_names, filename))
    try:
        wb = pyxl.load_workbook(filename)
        return extract_part_fields_from_wb(wb, field_names)
    except FieldExtractionError:
        logger.warn('Field extraction failed on {}.'.format(filename))
    return {}


def extract_part_fields_from_csv(filename, field_names):
    logger.log(DEBUG_OVERVIEW, 'Extracting fields {} from CSV file {}.'.format(field_names, filename))
    try:
        # Convert the CSV file into an XLSX workbook object and extract fields from that.
        wb = csvfile_to_wb(filename)
        return extract_part_fields_from_wb(wb, field_names)
    except FieldExtractionError:
        logger.warn('Field extraction failed on {}.'.format(filename))
    return {}


def get_component_refs(component):
    '''Return a list of references for a component.'''
    # Get the references of the component. (There may be more than one
    # if the component is part of a hierarchical sheet that's replicated.)
    refs = [r['ref'] for r in component.references]
    refs = [re.search(r'="(.*)"', r).group(1) for r in refs]
    refs = set(refs)
    refs.add(component.labels['ref'])  # Non-hierarchical ref.
    return refs


def extract_part_fields_from_sch(filename, field_names):
    logger.log(DEBUG_OVERVIEW, 'Extracting fields {} from schematic file {}.'.format(field_names, filename))
    part_fields_dict = {}
    sch = Schematic(filename)
    # Go through each component of the schematic, extracting its fields.
    for component in sch.components:
        # Get the fields and their values from the component.
        part_fields = {}
        for f in component.fields:
            id = unquote(f['id'])
            value = unquote(f['ref'])
            # Assign a name for the unnamed fields (F1, F2 & F3).
            # Use the name for the higher fields (F4...).
            # Don't use the reference field (F0) because that's already used as the dict key.
            name = sch_field_id_to_name.get(id, unquote(f['name']))
            # Store the field and its value if the field name is in the list of
            # allowed fields. (An empty list means that all fields are allowed.)
            if field_names is None or len(field_names) == 0 or name in field_names:
                part_fields[name] = value
        try:
            del part_fields['']
        except KeyError:
            pass
        # Create a dictionary entry for each ref and assign the part fields to it.
        for ref in get_component_refs(component):
            if ref[0] == '#' or ref[-1] == '?':
                continue  # Skip pseudo-parts (e.g. power nets) and unallocated parts.
            part_fields_dict[ref] = part_fields

    if logger.isEnabledFor(DEBUG_DETAILED):
        print('Extracted Part Fields:')
        pprint(part_fields_dict)

    return part_fields_dict


def extract_part_fields_from_lib(filename, field_names):
    logger.log(DEBUG_OVERVIEW, 'Extracting fields {} from part library {}.'.format(field_names, filename))
    part_fields_dict = {}
    lib = SchLib(filename)
    # Go through each component in the library, extracting its fields.
    for component in lib.components:
        component_name = component.definition['name']
        # Get the fields and their values from the component.
        part_fields = {}
        for id, f in enumerate(component.fields):
            if 'reference' in list(f.keys()):
                name = 'prefix'
                value = unquote(f['reference'])
            elif 'name' in list(f.keys()):
                # Assign a name for the unnamed fields (F1, F2 & F3).
                # Use the name for the higher fields (F4...).
                name = lib_field_id_to_name.get(str(id), unquote(f['fieldname']))
                value = unquote(f['name'])
            else:
                logger.warn('Unknown type of field in part {}: {}.'.format(component_name, f))
                continue
            # Store the field and its value if the field name is in the list of
            # allowed fields. (An empty list means that all fields are allowed.)
            logger.log(DEBUG_OBSESSIVE, 'Extracted library part: {} {} {}.'.format(component_name,name,value))
            if field_names is None or len(field_names) == 0 or name in field_names:
                part_fields[name] = value
        try:
            del part_fields['']
        except KeyError:
            pass
        # Create a dictionary entry for this library component.
        part_fields_dict[component_name] = part_fields

    if logger.isEnabledFor(DEBUG_DETAILED):
        print('Extracted Part Fields:')
        pprint(part_fields_dict)

    return part_fields_dict


def extract_part_fields(filenames, field_names):
    extraction_functions = {
        '.xlsx': extract_part_fields_from_xlsx,
        '.csv': extract_part_fields_from_csv,
        '.sch': extract_part_fields_from_sch,
        '.lib': extract_part_fields_from_lib,
    }
    logger.log(DEBUG_OVERVIEW, 'Extracting fields {} from files {}.'.format(field_names, filenames))
    part_fields_dict = {}
    if type(filenames) == str:
        filenames = [filenames]
    for f in filenames:
        try:
            f_extension = os.path.splitext(f)[1].lower()
            logger.log(DEBUG_DETAILED, 'Extracting fields from {}.'.format(f))
            f_part_fields = extraction_functions[f_extension](f, field_names)
            part_fields_dict.update(f_part_fields)
        except IOError:
            logger.warn('File not found: {}.'.format(f))
        except KeyError:
            logger.warn('Unknown file type for field extraction: {}.'.format(
                f))
    return part_fields_dict


def insert_part_fields_into_wb(part_fields_dict, wb):

    id_label = 'Refs'

    # Get all the unique field labels used in the dictionary of part fields.
    field_labels = set([])
    for fields_and_values in part_fields_dict.values():
        for field_label in fields_and_values:
            field_labels.add(field_label)
    field_labels = sorted(field_labels)
    field_labels.insert(0, id_label)

    if wb is None:
        wb = pyxl.Workbook()  # No workbook given, so create one.

    ws = wb.active  # Get the active sheet from the workbook.

    if ws.min_column == ws.max_column:
        # If the given worksheet is empty, then create one using the part field labels.
        # Create header row with a column for each part field.
        for c, lbl in enumerate(field_labels, 1):
            ws.cell(row=1, column=c).value = lbl
        # Enter the part references into the part reference column.
        for row, ref in enumerate(sorted(part_fields_dict.keys()), 2):
            ws.cell(row=row, column=1).value = ref

    # Get the header row from the worksheet.
    header_row, headers = find_header(ws)
    header_labels = [cell.value for cell in headers]
    # Get column for each header field.
    header_columns = {h.value: pyxl.cell.column_index_from_string(h.column)
                      for h in headers}
    # Next open column. Combine with [0] in case there are no headers.
    next_header_column = max(list(header_columns.values()) + [0]) + 1
    # Find the column with the part references.
    id_col = find_header_column(headers, id_label)
    # Go through each row, see if any identifier is in the part dictionary, and
    # insert/overwrite fields from the dictionary.
    for row in range(header_row + 1, ws.max_row + 1):
        for id in explode(ws.cell(row=row, column=id_col).value):
            try:
                fields = part_fields_dict[id]
                for field, value in fields.items():
                    # Change None field values to empty strings.
                    if value is None:
                        value = ''
                    try:
                        # Match the field name to one of the headers and overwrite the
                        # cell value with the dictionary value.
                        header = get_close_matches(field, header_labels, 1,
                                                   0.3)[0]
                        cell_value = ws.cell(row=row,column=header_columns[header]).value
                        logger.log(DEBUG_OBSESSIVE, 'Updating {} field {} from {} to {}'.format(
                            id, field, cell_value, value))
                        ws.cell(row=row,
                                column=header_columns[header]).value = value
                    except IndexError:
                        # The dictionary field didn't match any sheet header closely enough,
                        # so add a new column with the field name as the header label.
                        cell_value = ws.cell(row=row,column=header_columns[header]).value
                        logger.log(DEBUG_OBSESSIVE, 'Adding {} field {} with value {}'.format(
                            id, field, value))
                        ws.cell(row=row,
                                column=next_header_column).value = value
                        new_header_cell = ws.cell(row=header_row,
                                                  column=next_header_column)
                        new_header_cell.value = field
                        headers.append(new_header_cell)
                        header_labels.append(field)
                        header_columns[field] = next_header_column
                        next_header_column += 1
            except KeyError:
                pass  # The part reference doesn't exist in the dictionary.
    return wb


def insert_part_fields_into_xlsx(part_fields_dict, filename):
    logger.log(DEBUG_OVERVIEW, 'Inserting extracted fields into XLSX file {}.'.format(filename))
    try:
        wb = pyxl.load_workbook(filename)
    except IOError:
        wb = None
    wb = insert_part_fields_into_wb(part_fields_dict, wb)
    wb.save(filename)


def insert_part_fields_into_csv(part_fields_dict, filename):
    logger.log(DEBUG_OVERVIEW, 'Inserting extracted fields into CSV file {}.'.format(filename))
    try:
        wb = csvfile_to_wb(filename)
    except IOError:
        wb = None
    wb = insert_part_fields_into_wb(part_fields_dict, wb)
    wb_to_csvfile(wb, filename)


def reorder_sch_fields(fields):
    '''Return the part fields with the named fields ordered alphabetically.'''
    # Don't sort the first four, unnamed fields.
    named_fields = sorted(fields[4:], key=operator.itemgetter('name','id'))
    # Renumber the ids of the sorted fields.
    for id, field in enumerate(named_fields, 4):
        field['id'] = str(id)
    # Return the first four fields plus the remaining sorted fields.
    return fields[:4] + named_fields


def insert_part_fields_into_sch(part_fields_dict, filename):
    logger.log(DEBUG_OVERVIEW, 'Inserting extracted fields into schematic file {}.'.format(filename))
    try:
        sch = Schematic(filename)
    except IOError:
        logger.warn('Schematic file {} not found.'.format(filename))
        return

    # Go through all the schematic components, replacing field values and
    # adding new fields from the part fields dictionary.
    for component in sch.components:
        prev_part_fields = None
        refs = get_component_refs(component)
        for ref in refs:
            # Get fields for the part with the same reference as this component.
            part_fields = part_fields_dict.get(ref, {})
            if prev_part_fields is not None and part_fields != prev_part_fields:
                logger.warn("The inserted part lists for hierarchically-instantiated components {} have different values.".format(refs))
            prev_part_fields = deepcopy(part_fields)    
            for field_name, field_value in part_fields.items():
                # Get the field id associated with this field name (if there is one).
                field_id = lib_field_name_to_id.get(field_name, None)
                # Search for an existing field with a matching name in the component.
                for f in component.fields:
                    if unquote(f['name']).lower() == field_name.lower():
                        # Update existing named field in component.
                        logger.log(DEBUG_OBSESSIVE, 'Updating {} field {} from {} to {}'.format(
                            ref, f['id'], f['ref'], field_value))
                        f['ref'] = quote(field_value)
                        break
                    elif f['id'] == field_id:
                        # Update one of the default, unnamed fields in component.
                        logger.log(DEBUG_OBSESSIVE, 'Updating {} field {} from {} to {}'.format(
                                ref, f['id'], f['ref'], field_value))
                        f['ref'] = quote(field_value)
                        break
                else:
                    if field_value not in (None,''):
                        # Add new named field to component.
                        new_field = {'ref': quote(field_value),
                                     'name': quote(field_name)}
                        component.addField(new_field)
                        logger.log(DEBUG_OBSESSIVE, 'Adding {} field {} with value {}'.format(
                            ref, component.fields[-1]['id'], field_value))
                # Remove any named fields with empty values. 
                component.fields = [f for f in component.fields 
                    if unquote(f.get('name',None)) in (None,'','~') 
                    or unquote(f.get('ref',None)) not in (None,'')]
                # Canonically order the fields to make schematic comparisons
                # easier during acceptance testing.
                component.fields = reorder_sch_fields(component.fields)

    sch.save(filename)


def insert_part_fields_into_lib(part_fields_dict, filename):
    logger.log(DEBUG_OVERVIEW, 'Inserting extracted fields into library file {}.'.format(filename))
    try:
        lib = SchLib(filename)
    except IOError:
        logger.warn('Library file {} not found.'.format(filename))
        return

    # Go through all the library components, replacing field values and
    # adding new fields from the part fields dictionary.
    for component in lib.components:
        component_name = component.definition['name']
        # Get fields for the part with the same name as this component.
        part_fields = part_fields_dict.get(component_name, {})
        for field_name, field_value in part_fields.items():
            # Get the field id associated with this field name (if there is one).
            field_id = lib_field_name_to_id.get(field_name, None)
            # Search for an existing field with a matching name in the component.
            for id, f in enumerate(component.fields):
                if unquote(f.get('fieldname','')).lower() == field_name.lower():
                    # Update existing named field in component.
                    logger.log(DEBUG_OBSESSIVE, 'Updating {} field {} from {} to {}'.format(
                        component_name, field_name, f['name'], field_value))
                    f['name'] = quote(field_value)
                    break
                elif str(id) == field_id:
                    if id == 0:
                        # Update the F0 field of the component.
                        logger.log(DEBUG_OBSESSIVE, 'Updating {} field {} from {} to {}'.format(
                                component_name, field_id, f['reference'], field_value))
                        f['reference'] = quote(field_value)
                    else:
                        # Update one of the F1, F2, or F3 fields in the component.
                        logger.log(DEBUG_OBSESSIVE, 'Updating {} field {} from {} to {}'.format(
                                component_name, field_id, f['name'], field_value))
                        f['name'] = quote(field_value)
                    break
            else:
                if field_value not in (None,''):
                    # Add new named field to component.
                    new_field = deepcopy(component.fields[-1])
                    new_field['name'] = quote(field_value)
                    new_field['fieldname'] = quote(field_name)
                    component.fields.append(new_field)
                    logger.log(DEBUG_OBSESSIVE, 'Adding {} field {} with value {}'.format(
                        component_name, field_name, field_value))
        # Remove any named fields with empty values. 
        component.fields = [f for f in component.fields 
            if unquote(f.get('fieldname',None)) in (None,'','~') 
            or unquote(f.get('name',None)) not in (None,'')]
        # Canonically order the fields to make schematic comparisons
        # easier during acceptance testing.
        #component.fields = reorder_lib_fields(component.fields)

    lib.save(filename)


def insert_part_fields(part_fields_dict, filenames):
    insertion_functions = {
        '.xlsx': insert_part_fields_into_xlsx,
        '.csv': insert_part_fields_into_csv,
        '.sch': insert_part_fields_into_sch,
        '.lib': insert_part_fields_into_lib,
    }
    logger.log(DEBUG_OVERVIEW, 'Inserting extracted fields into files {}.'.format(filenames))
    if len(part_fields_dict) == 0:
        logger.warn("There are no field values to insert!")
        return
    if type(filenames) == str:
        filenames = [filenames]
    for f in filenames:
        try:
            logger.log(DEBUG_DETAILED, 'Inserting fields into {}.'.format(f))
            f_extension = os.path.splitext(f)[1].lower()
            insertion_functions[f_extension](part_fields_dict, f)
        except IOError:
            logger.warn('Unable to write to file: {}.'.format(f))
        except KeyError:
            logger.warn('Unknown file type for field insertion: {}'.format(f))


def kifield(extract_filenames, insert_filenames, field_names):
    part_fields_dict = extract_part_fields(extract_filenames, field_names)
    insert_part_fields(part_fields_dict, insert_filenames)
