===============================
kifield
===============================

.. image:: https://img.shields.io/pypi/v/kifield.svg
        :target: https://pypi.python.org/pypi/kifield


A utility for manipulating part fields in KiCad schematic files or libraries.
KiField can extract all the component fields from a schematic or library
and place them into a spreadsheet for bulk editing, after which you can insert the
edited values from the spreadsheet back into the schematic or library.

* Free software: MIT license
* Documentation: https://kifield.readthedocs.org.

Features
--------

* Extracts all fields and values from one or more KiCad schematic libraries or files
  (even hierarchical designs), and inserts them into a spreadsheet (either
  CSV or XLSX format).
* Extracts all fields and values from one or more CSV or XLSX spreadsheet files
  and inserts them into one or more KiCad schematics or libraries.
