#!/usr/bin/env python

import sys
from tornkts.manage import Manage

manage = Manage()
try:
    manage.run(sys.argv[1])
except IndexError:
    manage.help()
