#!/usr/bin/env python
"""
Read csv statement from chase and convert it into expense report format

Usage:
  convert_chase.py -f <csvfile> -o <output>
  convert_chase.py -h

Options:
  -f csvfile  Path to CSV formatted chase statement
  -o output   Path to CSV formatted output file. defaults to stdout.
  -h          Help message

Notes:

chase statement headers:
  Type,Post Date,Description,Amount,Check or Slip #

expense report headers:
  Date,Amount,Category,Property,Source,Account,CheckNum,Notes

conversions:
  Type: no conversion; skip all CREDIT rows
  Post Date => Date
  Description => Notes
  Amount: drop negative sign => Amount
  Check or Slip # => CheckNum

insertions:
  set Source to 'statement'
  set Account to 'chase'
  set Category to ''
  set Propery to ''
"""

import csv
from collections import namedtuple
from functools import reduce

from docopt import docopt

def main():
    args = docopt(__doc__)

    output_colunms = [
        'Date',
        'Amount',
        'Category',
        'Property',
        'Source',
        'Account',
        'CheckNum',
        'Notes',
    ]
    output_file = open(args['-o'], 'w', newline='')
    output = csv.DictWriter(output_file, fieldnames=output_colunms)
    output.writeheader()

    with open(args['-f'], newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Type'] == 'CREDIT':
                continue
            output.writerow(dict(
                Date=row['Post Date'],
                Amount=row['Amount'][1:] if row['Amount'].startswith('-',0,1) else row['Amount'],
                Category='',
                Property='',
                Source='statement',
                Account='chase',
                CheckNum=row['Check or Slip #'],
                Notes=row['Description'],
            ))

if __name__ == "__main__":
    main()
