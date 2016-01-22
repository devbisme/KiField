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
import csv
import logging
from difflib import get_close_matches
import openpyxl as pyxl
from .sch import Schematic
import pdb

logger = logging.getLogger('kifield')

# Assign some names to the unnamed fields in a schematic component.
field_id_to_name = {'1': 'value', '2': 'footprint', '3': 'datasheet'}
field_name_to_id = {v: k for k, v in field_id_to_name.items()}


def quote(s):
    '''Surround a string with quote marks.'''
    return '"' + str(s) + '"'


def unquote(s):
    '''Remove any quote marks around a string.'''
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
                '^((?P<start_prefix>\D+)(?P<range_start>\d+))[-:]((?P<end_prefix>\D+)(?P<range_end>\d+))$',
                r)
            if mtch is None:
                individual_refs.append(r)
            else:
                start_prefix = mtch.group('start_prefix')
                range_start = int(mtch.group('range_start'))
                end_prefix = mtch.group('end_prefix')
                range_end = int(mtch.group('range_end'))
                for i in range(range_start, range_end + 1):
                    individual_refs.append(start_prefix + str(i))
    logger.log(logging.DEBUG-4, 'Exploding {} => {}.'.format(ref, individual_refs))
    return individual_refs


def csvfile_to_wb(csv_filename):
    '''Open a CSV file and return an openpyxl workbook.'''

    logger.log(logging.DEBUG-4, 'Converting {} into an XLSX workbook.'.format(csv_filename))
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

    logger.log(logging.DEBUG-4, 'Saving XLSX workbook into {}.'.format(csv_filename))
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
    logger.log(logging.DEBUG-4, 'Header on row {}: {}.'.format(header_row_num, header))
    return header_row_num, header


def find_header_column(header, lbl):
    '''Find the field header column containing the closest match to the given label.'''
    header_labels = [cell.value for cell in header]
    lbl_match = get_close_matches(lbl, header_labels, 1, 0.0)[0]
    for cell in header:
        if str(cell.value).lower() == lbl_match.lower():
            logger.log(logging.DEBUG-4, 'Found {} on header column {}.'.format(lbl, cell.column))
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
            logger.warning('extracting fields {}.'.format(field_cols))
        else:
            for field_name in field_names:
                try:
                    field_cols[field_name] = find_header_column(header,
                                                                field_name)
                except FindLabelError:
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

    if logger.isEnabledFor(logging.DEBUG - 4):
        print('Extracted Part Fields:')
        pprint(part_fields)

    return part_fields


def extract_part_fields_from_xlsx(filename, field_names):
    try:
        wb = pyxl.load_workbook(filename)
        return extract_part_fields_from_wb(wb, field_names)
    except FieldExtractionError:
        logger.warn('Field extraction failed on {}.'.format(filename))
    return {}


def extract_part_fields_from_csv(filename, field_names):
    try:
        wb = csvfile_to_wb(filename)
        return extract_part_fields_from_wb(wb, field_names)
    except FieldExtractionError:
        logger.warn('Field extraction failed on {}.'.format(filename))
    return {}


def extract_part_fields_from_sch(filename, field_names):
    part_fields = {}
    sch = Schematic(filename)
    for component in sch.components:
        refs = [r['ref'] for r in component.references]
        refs = [re.search(r'="(.*)"', r).group(1) for r in refs]
        refs = set(refs)
        refs.add(component.labels['ref'])  # Non-hierarchical ref.
        for ref in refs:
            if ref[0] == '#' or ref[-1] == '?':
                continue  # Skip pseudo-parts (e.g. power nets) and unallocated parts.
            part_fields[ref] = {}
            for f in component.fields:
                id = unquote(f['id'])
                value = unquote(f['ref'])
                # Assign a name for the unnamed fields (F1, F2 & F3).
                # Use the name for the higher fields (F4...).
                # Don't use the reference field (F0) because that's already used as the dict key.
                name = field_id_to_name.get(id, unquote(f['name']))
                part_fields[ref][name] = value
                if field_names is not None and len(field_names) != 0:
                    # Remove fields that aren't in the list of field names if that list is non-empty.
                    part_fields[ref] = {n: part_fields[ref][n]
                                        for n in field_names
                                        if n in part_fields[ref]}
            try:
                del part_fields[ref]['']
            except KeyError:
                pass

    if logger.isEnabledFor(logging.DEBUG - 4):
        print('Extracted Part Fields:')
        pprint(part_fields)

    return part_fields


def extract_part_fields(filenames, field_names):
    extraction_functions = {
        '.xlsx': extract_part_fields_from_xlsx,
        '.csv': extract_part_fields_from_csv,
        '.sch': extract_part_fields_from_sch,
    }
    part_fields = {}
    if type(filenames) == str:
        filenames = [filenames]
    for f in filenames:
        try:
            f_extension = os.path.splitext(f)[1].lower()
            logger.log(logging.DEBUG-1, 'Extracting fields from {}.'.format(f))
            f_part_fields = extraction_functions[f_extension](f, field_names)
            part_fields.update(f_part_fields)
        except IOError:
            logger.warn('File not found: {}.'.format(f))
        except KeyError:
            logger.warn('Unknown file type for field extraction: {}.'.format(
                f))
    return part_fields


def insert_part_fields_into_wb(part_fields_dict, wb):

    # Get all the unique field labels used in the dictionary of part fields.
    field_labels = set([])
    for fields_and_values in part_fields_dict.values():
        for field_label in fields_and_values:
            field_labels.add(field_label)
    field_labels = sorted(field_labels)
    field_labels.insert(0, 'Refs')

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
    ref_col = find_header_column(headers, 'Refs')
    # Go through each row, see if any ref is in the part dictionary, and
    # insert/overwrite fields from the dictionary.
    for row in range(header_row + 1, ws.max_row + 1):
        for ref in explode(ws.cell(row=row, column=ref_col).value):
            try:
                fields = part_fields_dict[ref]
                for field, value in fields.items():
                    # Skip fields with empty values.
                    if value is None:
                        value = ''
                    try:
                        # Match the field name to one of the headers and overwrite the
                        # cell value with the dictionary value.
                        header = get_close_matches(field, header_labels, 1,
                                                   0.3)[0]
                        cell_value = ws.cell(row=row,column=header_columns[header]).value
                        logger.debug('Updating {} field {} from {} to {}'.format(
                            ref, field, cell_value, value))
                        ws.cell(row=row,
                                column=header_columns[header]).value = value
                    except IndexError:
                        # The dictionary field didn't match any sheet header closely enough,
                        # so add a new column with the field name as the header label.
                        cell_value = ws.cell(row=row,column=header_columns[header]).value
                        logger.debug('Adding {} field {} from {} to {}'.format(
                            ref, field, cell_value, value))
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
    try:
        wb = pyxl.load_workbook(filename)
    except IOError:
        wb = None
    wb = insert_part_fields_into_wb(part_fields_dict, wb)
    wb.save(filename)


def insert_part_fields_into_csv(part_fields_dict, filename):
    try:
        wb = csvfile_to_wb(filename)
    except IOError:
        wb = None
    wb = insert_part_fields_into_wb(part_fields_dict, wb)
    wb_to_csvfile(wb, filename)


def insert_part_fields_into_sch(part_fields_dict, filename):

    try:
        sch = Schematic(filename)
    except IOError:
        logger.warn('Schematic file {} not found.'.format(filename))
        return

    # Go through all the schematic components, replacing field values and
    # adding new fields from the part fields dictionary.
    for component in sch.components:
        # Get fields for the part with the same reference as this component.
        part_fields = part_fields_dict.get(component.labels['ref'], {})
        for field_name, field_value in part_fields.items():
            field_id = field_name_to_id.get(field_name, None)
            # Search for an existing field in the component.
            for f in component.fields:
                if unquote(f['name']).lower() == field_name.lower():
                    # Update existing named field in component.
                    logger.debug('Updating {} field {} from {} to {}'.format(
                        component.labels['ref'], f['id'], f[
                            'ref'], field_value))
                    f['ref'] = quote(field_value)
                    break
                elif f['id'] == field_id:
                    # Update one of the default, unnamed fields in component.
                    logger.debug('Updating {} field {} from {} to {}'.format(
                        component.labels['ref'], f['id'], f[
                            'ref'], field_value))
                    f['ref'] = quote(field_value)
                    break
            else:
                if field_value is not None:
                    # Add new named field to component.
                    new_field = {'ref': quote(field_value),
                                 'name': quote(field_name)}
                    logger.debug('Adding {} field {} of {}'.format(
                        component.labels['ref'], '???', field_value))
                    component.addField(new_field)
                    logger.debug('Addition result: {}'.format(component.fields))

    sch.save(filename)


def insert_part_fields(part_fields_dict, filenames):
    insertion_functions = {
        '.xlsx': insert_part_fields_into_xlsx,
        '.csv': insert_part_fields_into_csv,
        '.sch': insert_part_fields_into_sch,
    }
    if len(part_fields_dict) == 0:
        logger.warn("There are no field values to insert!")
        return
    if type(filenames) == str:
        filenames = [filenames]
    for f in filenames:
        try:
            f_extension = os.path.splitext(f)[1].lower()
            logger.log(logging.DEBUG-1, 'Inserting fields into {}.'.format(f))
            insertion_functions[f_extension](part_fields_dict, f)
        except IOError:
            logger.warn('Unable to write to file: {}.'.format(f))
        except KeyError:
            logger.warn('Unknown file type for field insertion: {}'.format(f))


def kifield(extract_filenames, insert_filenames, field_names):
    part_fields_dict = extract_part_fields(extract_filenames, field_names)
    insert_part_fields(part_fields_dict, insert_filenames)
