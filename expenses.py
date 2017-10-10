#!/usr/bin/env python
"""
Reconcile expenses totaled by categories

Usage:
  expenses -f <csvfile> [-v]
  expenses -h

Options:
  -f csvfile  Path to CSV formatted expenses file.
  -v          Print out expense entries
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
    for category in sorted(set([e.Category for e in expenses])):
        amounts = [cents(e.Amount) for e in expenses if e.Category == category]
        if amounts:
            total = reduce(lambda x, y: x+y, amounts)
            print('  {:<32}{:>12}'.format(category + ':', dollars(total)))

def find_duplicates(expense_items, duplicate_sets=[]):
    if len(expense_items) <= 1:
        return duplicate_sets
    else:
        item = expense_items.pop()
        dups_for_item = [e for e in expense_items
                if (e.Date, e.Amount, e.Category, e.Property, e.Source, e.CheckNum) ==
                (item.Date, item.Amount, item.Category, item.Property, item.Source, item.CheckNum)]
        if dups_for_item:
            dups_for_item.append(item)
            duplicate_sets.append(dups_for_item)
            expense_items = [x for x in expense_items if x not in dups_for_item]
        return find_duplicates(expense_items, duplicate_sets)


def main():
    args = docopt(__doc__)
    expenses = []
    with open(args['-f'], newline='') as f:
        reader = csv.reader(f)
        header = next(reader)
        Expense = namedtuple('Expense', [h.strip() for h in header] + ['line_num'])
        for row in reader:
            if not row:
                continue
            try:
                expense = Expense._make(row + [reader.line_num])
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

    if args['-v']:
        for e in expenses: print(e)

    by_property = dict()
    for property in set([e.Property for e in expenses]):
        if property:
            by_property[property] = []
        else:
            by_property['General'] = []
    for e in expenses:
        if not e.Property:
            by_property['General'].append(e)
        else:
            by_property[e.Property].append(e)
    general = by_property.pop('General')
    for property in sorted(by_property.keys()):
        print("\nProperty: %s" % property)
        report_by_categories(by_property[property])
    print("\nProperty: General")
    report_by_categories(general)

    duplicates = find_duplicates(list(expenses))
    if duplicates:
        print("\nPosible duplicate expense entries:")
        for dup_list in duplicates:
            for item in dup_list:
                print(item)
            print()


if __name__ == "__main__":
    main()

