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

def report_by_categories(expenses, split_facter=0):
    total = 0
    for category in sorted(set([e.Category for e in expenses])):
        amounts = [cents(e.Amount) for e in expenses if e.Category == category]
        if amounts:
            summed = reduce(lambda x, y: x+y, amounts)
            total += summed
            if split_facter:
                print('  {:<32}{:>12}{:>12}'.format(
                        category + ':', dollars(summed), dollars(summed / split_facter)))
            else:
                print('  {:<32}{:>12}'.format(category + ':', dollars(summed)))
    if total:
        if split_facter:
            print('{:>46}{:>12}'.format('-'*8, '-'*8))
            print('Total:{:>40}{:>12}'.format(dollars(total), dollars(total / split_facter)))
        else:
            print('{:>46}'.format('-'*8))
            print('Total:{:>40}'.format(dollars(total)))

def find_duplicates(expense_items, duplicate_sets=[]):
    if len(expense_items) <= 1:
        return duplicate_sets
    else:
        item = expense_items.pop()
        dups_for_item = [e for e in expense_items
                if (e.Date, e.Amount, e.Category, e.CheckNum) ==
                (item.Date, item.Amount, item.Category, item.CheckNum)]
                #if (e.Date, e.Amount, e.Category) == (item.Date, item.Amount, item.Category)]
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
                if not expense.Date:
                    print('Amount missing at line %s: %s' % (reader.line_num, row))
                elif not expense.Amount:
                    print('Amount missing at line %s: %s' % (reader.line_num, row))
                elif not expense.Category:
                    print('Category missing at line %s: %s' % (reader.line_num, row))
                else:
                    expenses.append(expense)

    if args['-v']:
        for e in expenses: print(e)

    expenses_by_property = dict()
    for property in set([e.Property for e in expenses]):
        if property:
            expenses_by_property[property] = list()
    general_expenses = list()
    for e in expenses:
        if not e.Property:
            general_expenses.append(e)
        else:
            expenses_by_property[e.Property].append(e)
    for property in sorted(expenses_by_property.keys()):
        print("\nProperty: %s" % property)
        report_by_categories(expenses_by_property[property])
    if general_expenses:
        print("\nProperty: General")
        report_by_categories(general_expenses, len(expenses_by_property))


    duplicates = find_duplicates(list(expenses))
    if duplicates:
        print("\nPosible duplicate expense entries:")
        for dup_list in duplicates:
            for item in dup_list:
                print(item)
            print()


if __name__ == "__main__":
    main()

