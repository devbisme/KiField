# -*- coding: utf-8 -*-

# MIT License / Copyright (c) 2021 by XESS Corporation.

import sys
import logging

USING_PYTHON2 = sys.version_info.major == 2
USING_PYTHON3 = not USING_PYTHON2

if USING_PYTHON2:
    reload(sys)
    sys.setdefaultencoding("utf8")
else:
    # Python3 doesn't have basestring, so create one.
    basestring = type("")


DEBUG_OVERVIEW = logging.DEBUG
DEBUG_DETAILED = logging.DEBUG - 1
DEBUG_OBSESSIVE = logging.DEBUG - 2
