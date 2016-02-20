========
Usage
========

KiField is usually employed in a three-step process:

#. First use KiField to extract the part field labels and values from a
   schematic or library and place them into a CSV or XLSX spreadsheet file.

#. Edit the spreadsheet file to change existing field values, add entirely
   new fields, or completely delete fields.

#. Finally, use KiField to insert the updated field labels and values from
   the spreadsheet file into the schematic or library. 

Command-line Options
------------------------

::

    usage: kifield.py [-h] [--version]
                      [--extract file.[xlsx|csv|sch|lib|dcm]
                                [file.[xlsx|csv|sch|lib|dcm] ...]]
                      [--insert file.[xlsx|csv|sch|lib|dcm]
                               [file.[xlsx|csv|sch|lib|dcm] ...]] 
                      [--overwrite]
                      [--nobackup]
                      [--fields name|/name|~name [name|/name|~name ...]]
                      [--debug [LEVEL]]

    Insert fields from spreadsheets into KiCad schematics or libraries, or gather
    fields from schematics or libraries and place them into a spreadsheet.

    optional arguments:
      -h, --help            show this help message and exit
      --version, -v         show program's version number and exit
      --extract file.[xlsx|csv|sch|lib|dcm] [file.[xlsx|csv|sch|lib|dcm] ...], 
             -x file.[xlsx|csv|sch|lib|dcm] [file.[xlsx|csv|sch|lib|dcm] ...]
                            Extract field values from one or more spreadsheet or
                            schematic files.
      --insert file.[xlsx|csv|sch|lib|dcm] [file.[xlsx|csv|sch|lib|dcm] ...],
            -i file.[xlsx|csv|sch|lib|dcm] [file.[xlsx|csv|sch|lib|dcm] ...]
                            Insert extracted field values into one or more
                            schematic or spreadsheet files.
      --overwrite, -w       Allow field insertion into an existing file.
      --nobackup, -nb       Do *not* create backups before modifying files.
                            (Default is to make backup files.)
      --fields name|/name|~name [name|/name|~name ...], 
            -f name|/name|~name [name|/name|~name ...]
                            Specify the names of the fields to extract and insert.
                            Place a '/' or '~' in front of a field you wish to
                            omit. (Leave blank to extract/insert *all* fields.)
      --debug [LEVEL], -d [LEVEL]
                            Print debugging info. (Larger LEVEL means more info.)

Examples
------------------------

Adding Fields to a Schematic or Library
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To extract the fields from one or more schematics and place them in a CSV file::

  kifield -x my_design.sch -i my_design_fields.csv

Or you can place them in an XLSX spreadsheet::

  kifield -x my_design.sch -i my_Design_fields.xlsx

The result will look something like this (I added spaces to format it into
nice columns)::

    Refs,     datasheet, footprint,                        value
    C1,       ,          Capacitors_SMD:c_elec_6.3x5.3,    100uF
    C2,       ,          Capacitors_SMD:C_0805,            10uF
    CON1,     ,          Connect:BARREL_JACK,              BARREL_JACK
    GPIO1,    ,          RPi_Hat:Pin_Header_Straight_2x20, RPi_GPIO
    JP2,      ,          XESS:HDR_1x3,                     JUMPER3
    LED1,     ,          LEDs:LED-0603,                    LED
    LED2,     ,          LEDs:LED-0603,                    LED
    R2,       ,          Resistors_SMD:R_0402,             100
    R3,       ,          Resistors_SMD:R_0402,             100
    RN1,      ,          XESS:CTS_742C043,                 4.7K
    RN2,      ,          XESS:CTS_742C043,                 100
    RN5,      ,          XESS:CTS_742C083,                 100
    U1,       ,          XESS:SOT-223,                     AZ1117EH-3.3
    U2,       ,          SMD_Packages:SOIC-8-N,            I2C Flash
    U3,       ,          XESS:SOT-223,                     AZ1117EH-1.2

Now suppose you want to add the manufacturers part number to some of the
components. Just add a new column named ``manf#`` and fill in some of the
values like so::

    Refs,     datasheet, footprint,                        value,        manf#
    C1,       ,          Capacitors_SMD:c_elec_6.3x5.3,    100uF,        UWX1A101MCL1GB
    C2,       ,          Capacitors_SMD:C_0805,            10uF,         UWX1A101MCL1GB
    CON1,     ,          Connect:BARREL_JACK,              BARREL_JACK,  PJ002A
    GPIO1,    ,          RPi_Hat:Pin_Header_Straight_2x20, RPi_GPIO,
    JP2,      ,          XESS:HDR_1x3,                     JUMPER3,
    LED1,     ,          LEDs:LED-0603,                    LED,          LTST-C190KFKT
    LED2,     ,          LEDs:LED-0603,                    LED,          LTST-C190KFKT
    R2,       ,          Resistors_SMD:R_0402,             100,
    R3,       ,          Resistors_SMD:R_0402,             100,
    RN1,      ,          XESS:CTS_742C043,                 4.7K,
    RN2,      ,          XESS:CTS_742C043,                 100,
    RN5,      ,          XESS:CTS_742C083,                 100,
    U1,       ,          XESS:SOT-223,                     AZ1117EH-3.3, AZ1117EH-3.3TRG1
    U2,       ,          SMD_Packages:SOIC-8-N,            I2C Flash,    CAT24C32WI-GT3
    U3,       ,          XESS:SOT-223,                     AZ1117EH-1.2,

To insert the manufacturer's numbers back into the schematic, just swap the roles
of the CSV and schematic files::

  kifield -x my_design_fields.csv -i my_design.sch -w

Now when you examine the parts in eeschema, you should see the added manufacturer's
part numbers:

.. image:: example1.png

Adding fields to a schematic parts library is done in an equivalent manner.
In this case, however, the ``Refs`` column will hold the library name of the
component rather than its reference designator in a schematic.

You can also use kifield with the description (`.dcm`) file associated with a parts library.
However, description files only support three fields with specific names:
``description``, ``keywords`` and ``docfile``.
Any other fields will be ignored.


Removing Fields from a Schematic or Library
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It's also easy to remove fields from a schematic or library.
Just delete all the data for a spreadsheet column but **leave the header** like so::

    Refs,     datasheet, footprint, value,        manf#
    C1,       ,          ,          100uF,        
    C2,       ,          ,          10uF,         
    CON1,     ,          ,          BARREL_JACK,  
    GPIO1,    ,          ,          RPi_GPIO,
    JP2,      ,          ,          JUMPER3,
    LED1,     ,          ,          LED,          
    LED2,     ,          ,          LED,          
    R2,       ,          ,          100,
    R3,       ,          ,          100,
    RN1,      ,          ,          4.7K,
    RN2,      ,          ,          100,
    RN5,      ,          ,          100,
    U1,       ,          ,          AZ1117EH-3.3, 
    U2,       ,          ,          I2C Flash,    
    U3,       ,          ,          AZ1117EH-1.2,

After inserting the spreadsheet values into the schematic, all the PCB footprints and 
manufacturer's part numbers will be erased.

Removing fields from a schematic parts library is done in an equivalent manner.


Restricting the Range of Field Changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are two ways to prevent KiField from making changes in a schematic
or library:

#. Clear one or more spreadsheet cells holding part references. KiField will 
   not insert or change any field values for those parts because there is no way to locate
   them in the schematic or library file with the reference removed.
   You can also achieve the same result by deleting the entire row of the spreadsheet.

#. Use KiField's ``--fields`` option to specify the names of one or more spreadsheet columns
   whose values will be inserted into the schematic or library file.
   The values in any other column will be ignored.
   You can also omit one or more fields by adding a '/' or '~' to the beginning
   of their names. In that case, the values in all the other columns are inserted.
   (Omitting the ``--fields`` option or entering a blank list causes KiField to
   insert the values from **all** the columns in the spreadsheet.)


Preventing Disasters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A lot of work goes into creating a schematic or parts library.
It would be a shame if anything happened to them.
For this reason, KiField makes a backup of any file it is about to change.
You can turn off this behavior using KiField's ``--nobackup`` option.

In addition, if KiField is inserting values into an existing schematic
or library file, then you must use the ``--overwrite`` option.

