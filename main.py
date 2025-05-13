#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

# Asegurarnos de que los scripts sean encontrados
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

from ui.app import PostgreSQLBackupApp

if __name__ == "__main__":
    app = PostgreSQLBackupApp()
    app.mainloop()