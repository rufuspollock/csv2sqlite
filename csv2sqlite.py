#!/usr/bin/env python
#
# A simple Python script to convert csv files to sqlite (with type guessing)
#
# @author: Rufus Pollock
# Placed in the Public Domain
# Bug fixes by Simon Heimlicher <sh@nine.ch> marked by `shz:'

from __future__ import print_function

import sys
import argparse
import csv
import sqlite3

def convert(filepath_or_fileobj, dbpath, table):
    if isinstance(filepath_or_fileobj, basestring):
        fo = open(filepath_or_fileobj, 'rU')
    else:
        fo = filepath_or_fileobj

    dialect = csv.Sniffer().sniff(fo.readline())
    fo.seek(0)

    reader = csv.reader(fo, dialect)
    types = _guess_types(reader)
    fo.seek(0)

    reader = csv.reader(fo, dialect)
    headers = [header.strip() for header in reader.next()]

    _columns = ','.join(
        ['"%s" %s' % (header, _type) for (header,_type) in zip(headers, types)]
        )

    conn = sqlite3.connect(dbpath)
    # shz: fix error with non-ASCII input
    conn.text_factory = str
    c = conn.cursor()

    try:
        create_query = 'CREATE TABLE %s (%s)' % (table, _columns)
        c.execute(create_query)
    except:
        pass

    _insert_tmpl = 'INSERT INTO %s VALUES (%s)' % (table,
        ','.join(['?']*len(headers)))

    line = 0
    for row in reader:
        line += 1
        if len(row) == 0:
            continue
        # we need to take out commas from int and floats for sqlite to
        # recognize them properly ...
        try:
            row = [
                None if x == ''
                else float(x.replace(',', '')) if y == 'real'
                else int(x) if y == 'integer'
                else x for (x,y) in zip(row, types) ]
            c.execute(_insert_tmpl, row)
        except ValueError, e:
            print("Unable to convert value '%s' to type '%s' on line %d" % (x, y, line), file=sys.stderr)
        except Exception, e:
            print("Error on line %d: %s" % (line, e), file=sys.stderr)


    conn.commit()
    c.close()

def _guess_types(reader, max_sample_size=100):
    '''Guess column types (as for SQLite) of CSV.

    :param fileobj: read-only file object for a CSV file.
    '''
    # skip header
    _headers = reader.next()
    # we default to text for each field
    types = ['text'] * len(_headers)
    # order matters
    # (order in form of type you want used in case of tie to be last)
    options = [
        ('text', unicode),
        ('real', float),
        ('integer', int)
        # 'date',
        ]
    # for each column a set of bins for each type counting successful casts
    perresult = {
        'integer': 0,
        'real': 0,
        'text': 0
        }

    results = [ dict(perresult) for x in range(len(_headers)) ]
    sample_counts = [ 0 for x in range(len(_headers)) ]

    for row_index,row in enumerate(reader):
        for column,cell in enumerate(row):
            cell = cell.strip()
            if len(cell) == 0:
                continue

            # replace ',' with '' to improve cast accuracy for ints and floats
            if(cell.count(',') > 0):
               cell = cell.replace(',', '')
               if(cell.count('E') == 0):
                  cell = cell + "E0"

            for data_type,cast in options:
                try:
                    cast(cell)
                    results[column][data_type] += 1
                    sample_counts[column] += 1
                except ValueError:
                    pass

        have_max_samples = True
        for column,cell in enumerate(row):
            if sample_counts[column] < max_sample_size:
                have_max_samples = False

        if have_max_samples:
            break

    for column,colresult in enumerate(results):
        for _type, _ in options:
            if colresult[_type] > 0 and colresult[_type] >= colresult[types[column]]:
                types[column] = _type

    return types


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='''
Convert a CSV file to a table in a SQLite database.
The database is created if it does not yet exist.
''')
    parser.add_argument('csv_file', type=str, help='Input CSV file path')
    parser.add_argument('sqlite_db_file', type=str, help='Output SQLite file')
    parser.add_argument('table_name', type=str, nargs='?', help='Name of table to write to in SQLite file', default='data')
    args = parser.parse_args()
    convert(args.csv_file, args.sqlite_db_file, args.table_name)
