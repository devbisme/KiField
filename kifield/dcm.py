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

    def __init__(self,file):

        self.name = None
        self.description = None
        self.keywords = None
        
        while True:
            line = file.readline()
            if not line:
                break
            mtch = re.match('^(?P<tag>[$\w]+)\s+(?P<contents>.*)\s*$', line)
            if mtch:
                tag = str(mtch.group('tag').upper())
                contents = str(mtch.group('contents'))
                if tag == r'$CMP':
                    self.name = contents
                elif tag == 'D':
                    self.description = contents
                elif tag == 'K':
                    self.keywords = contents

    def str():
        s = []
        if self.name is None:
            return s
        s += ['#']
        s += ['$CMP ' + self.name]
        if self.description is not None:
            s += ['D ' + self.description]
        if self.keywords is not None:
            s += ['K ' + self.keywords]
        s += ['$ENDCMP']
        s += ['#']
        return s

class Dcm(object):
    """
    A class to parse description files for KiCad schematic libraries.
    """
    def __init__(self, filename):

        self.filename = filename
        self.components = []

        with open(filename) as file:
            self.header = file.readline()

            if not self.header.startswith('EESchema-DOCLIB'):
                self.header = None
                sys.stderr.write('The file is not a KiCad schematic library description file\n')
                return

            while True:
                file_pos = file.tell()

                line = file.readline()

                if not line:
                    break

                if line.startswith('$CMP '):
                    file.seek(file_pos)
                    self.components.append(Component(file))

    def save(self, filename=None):
        # check whether it has header, what means that sch file was loaded fine
        if not self.header:
            return

        if not filename:
            filename = self.filename

        # Insert the header.
        to_write = []
        to_write += [self.header]

        # Insert components.
        for c in components:
            to_write += c.str()

        with open(filename, 'w') as file:
            file.writelines(to_write)
