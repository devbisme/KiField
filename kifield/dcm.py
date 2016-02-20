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


import sys
import re

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
            mtch = re.match('^(?P<tag>[$\w]+)\s+(?P<contents>.*)$', line)
            if mtch:
                tag = str(mtch.group('tag').upper())
                contents = str(mtch.group('contents'))
                if tag == r'$CMP':
                    self.name = contents
                elif tag == 'D':
                    self.description = contents
                elif tag == 'K':
                    self.keywords = contents
                elif tag == 'F':
                    self.docfile = contents
                elif tag == r'$ENDCMP':
                    return True
            elif re.match('^\$ENDCMP\s*$', line):
                return True

    def str(self):
        s = []
        if self.name is None:
            return s
        s.append('#\n')
        s.append('$CMP ' + self.name + '\n')
        if self.description is not None and len(self.description) > 0:
            s.append('D ' + self.description + '\n')
        if self.keywords is not None and len(self.keywords) > 0:
            s.append('K ' + self.keywords + '\n')
        if self.docfile is not None and len(self.docfile) > 0:
            s.append('F ' + self.docfile + '\n')
        s.append('$ENDCMP\n')
        s.append('#\n')
        return s

class Dcm(object):
    """
    A class to parse description files for KiCad schematic libraries.
    """
    def __init__(self, filename=None):

        self.filename = filename
        self.header = 'EESchema-DOCLIB  Version 2.0\n'
        self.components = []

        if filename is None:
            return

        with open(filename) as file:
            self.header = file.readline()

            if not self.header.startswith('EESchema-DOCLIB'):
                self.header = None
                sys.stderr.write('The file is not a KiCad schematic library description file\n')
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

        with open(filename, 'w') as file:
            file.writelines(to_write)
