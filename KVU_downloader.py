#!/usr/bin/env python3
"""Backward compatibility wrapper.

This file is kept for backward compatibility with existing scripts.
For new usage, please use the 'kvu-download' command instead.

Example:
    kvu-download https://knigavuhe.org/book/anafem/
    kvu-download anafem -t 8 --no-cover
"""

import sys
from kvu import main

if __name__ == "__main__":
    sys.exit(main())
