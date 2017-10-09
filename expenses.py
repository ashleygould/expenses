#!/usr/bin/env python
"""
Reconcile expenses totaled by categories

Usage:
  expenses -f <csvfile>
  expenses -h

Options:
  -f csvfile  Path to CSV formatted expenses file.
  -h          Help message


"""

import csv
from collections import namedtuple
from functools import reduce

from docopt import docopt
from babel.numbers import parse_decimal, format_currency


def cents(amount_str):
    decimal_str = parse_decimal(amount_str.strip().strip('$'))
    return round(float(decimal_str)*100)

def dollars(amount_in_cents):
    return format_currency(amount_in_cents / 100, 'USD')

def report_by_categories(expenses):
    for category in set([e.Category for e in expenses]):
        amounts = [cents(e.Amount) for e in expenses if e.Category == category]
        if amounts:
            total = reduce(lambda x, y: x+y, amounts)
            print('{:<16}{:>12}'.format(category + ':', dollars(total)))

def main():
    args = docopt(__doc__)
    print(args)
    expenses = []
    with open(args['-f'], newline='') as f:
        reader = csv.reader(f)
        header = next(reader)
        Expense = namedtuple('Expense', [h.strip() for h in header])
        for row in reader:
            #print(row)
            try:
                expense = Expense._make(row)
            except:
                print('bad row at line %s: %s' % (reader.line_num, row))
                continue
            else:
                if not expense.Amount:
                    print('Amount missing at line %s: %s' % (reader.line_num, row))
                elif not expense.Category:
                    print('Category missing at line %s: %s' % (reader.line_num, row))
                else:
                    expenses.append(expense)
    #for e in expenses: print(e)

    by_property = dict()
    for property in set([e.Property for e in expenses]):
        if property:
            by_property[property] = []
        else:
            by_property['All'] = []
    for e in expenses:
        if not e.Property:
            by_property['All'].append(e)
        else:
            by_property[e.Property].append(e)
    for property in sorted(by_property.keys()):
        print("\nProperty: %s" % property)
        report_by_categories(by_property[property])



if __name__ == "__main__":
    main()

