#!/usr/bin/env python3
"""
Command-line interface for the Glasgow Coma Scale Calculator.

Usage:
    python cli.py score --eye 4 --verbal 5 --motor 6
    python cli.py score --eye 3 --verbal 1T --motor 4 --pupils 1
    python cli.py score --eye 2 --verbal 2 --motor 3 --pediatric --json
    python cli.py batch --input patients.csv --output scored.csv
"""

import sys
from gcs import main

if __name__ == "__main__":
    sys.exit(main())
