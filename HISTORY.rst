.. :changelog:

History
-------


1.0.0 (2022-05-06)
______________________

* Bumped to version 1.0.0.
* Fixed a bug where field visibility is default-visible and/or cannot be set if Reference field does not contain an 'effects' property.
* Fixed some string-splitting and unicode bugs in `find_by_key()` that manifested in Python 2.


0.2.0 (2021-07-28)
______________________

* Added ``--no_range, -nr`` option to disable hyphenated ranges when components are grouped, explicitly showing each component in a group.


0.1.19 (2021-07-27)
______________________

* Bug fix: Add ``sexpdata`` to install requirements.
* Bug fix: Add import of ``reduce`` from ``functools``.
* Bug fix: Correct disappearance of default part fields when extracting from schematic to spreadsheet file.
* Bug fix: Explode collapsed references when importing a spreadsheet file.


0.1.18 (2021-06-28)
______________________

* KiCad V6 schematic and library files are now supported (well, V5.99 actually, but the file formats shouldn't change).


0.1.17 (2021-03-25)
______________________

* Part fields are cleaned up if they contain newlines.
* Lines in a schematic file which were broken by a newline within a quoted string are rejoined.
* Generated spreadsheet cells have their format set to TEXT if they contain a string.


0.1.16 (2020-07-26)
______________________

* Fixed problem with unescaped quote being inserted into schematics/libraries.


0.1.15 (2019-02-17)
______________________

* Fixed problems caused by new 2.6.0 version of openpyxl.


0.1.14 (2019-01-08)
______________________

* Fixed handling of relative sheetpaths in hierarchical schematics.
* Fixed string problems that occur under Anaconda.


0.1.13 (2018-10-28)
______________________

* Now works on files outside the current directory.
* Clearer error explanation when part field extraction fails.
* Simplified installation instructions.


0.1.12 (2018-01-22)
______________________

* Fixed error where output was not produced because KiField was first trying to backup a non-existent output file.


0.1.11 (2018-01-04)
______________________

* Line-feeds and carriage-returns are stripped from strings inserted into .sch or .lib files.
* Fixed error where reading .lib files was ignoring the first line after the EESchema-LIBRARY header and missing a part DEF.


0.1.10 (2018-01-01)
______________________

* File backup now works on all files in a hierarchical schematic.


0.1.9 (2017-12-31)
______________________

* Fixed mishandling of quoted strings containing escaped quotation marks.


0.1.8 (2017-09-23)
______________________

* Catch exception caused by numeric fields that aren't strings interacting with vis/invis option.


0.1.7 (2017-08-14)
______________________

* Added visibility/invisibility option for fields.


0.1.6 (2017-01-30)
______________________

* Added "grouping" option (`--group`) for gathering components with the same field values onto a single line of the XLSX/CSV/TSV file.


0.1.5 (2016-11-29)
______________________

* Added recursive operations on hierarchical schematics so everything can be handled just by processing the top-level file.


0.1.4 (2016-05-29)
______________________

* Added support for TSV files (thanks, kaspar.emanuel@gmail.com).


0.1.3 (2016-05-29)
______________________

* Fixed issue where all the fields from multi-unit components in a schematic were not appearing in the csv file.


0.1.2 (2016-04-13)
______________________

* Fixed issues #3 and #4 regarding incompatibilities with openpyxl 2.4.0a1.


0.1.1 (2016-02-20)
______________________

* Added the ability to extract/insert fields in DCM files.
* Added the ability to explicitly exclude fields from extraction/insertion.


0.1.0 (2016-01-29)
______________________

* First release on PyPI.
