#!/usr/bin/env python
# A simple Python script to convert csv files to sqlite (with type guessing)
#
# @author: Rufus Pollock
# Placed in the Public Domain
# Bug fixes by Simon Heimlicher <sh@nine.ch> marked by `shz:'
import csv
import sqlite3

def convert(filepath_or_fileobj, dbpath, table='data'):
    # detects table name from filename
    table = os.path.basename(filepath_or_fileobj).split(".")[0]
    
    if isinstance(filepath_or_fileobj, basestring):
        fo = open(filepath_or_fileobj, 'rU')
    else:
        fo = filepath_or_fileobj
    reader = csv.reader(fo)

    types = _guess_types(fo)
    fo.seek(0)
    headers = reader.next()

    _columns = ','.join(
        ['"%s" %s' % (header, _type) for (header,_type) in zip(headers, types)]
        )

    conn = sqlite3.connect(dbpath)
    # shz: fix error with non-ASCII input
    conn.text_factory = str
    c = conn.cursor()

    try:
        c.execute('CREATE table %s (%s)' % (table, _columns))
    except:
        pass

    _insert_tmpl = 'insert into %s values (%s)' % (table,
        ','.join(['?']*len(headers)))
    for row in reader:
        # we need to take out commas from int and floats for sqlite to
        # recognize them properly ...
        row = [
            None if x == ''
            else float(x.replace(',', '')) if y == 'real'
            else int(x) if y == 'integer'
            else x for (x,y) in zip(row, types) ]
        # shz: output line on which exception occurred and continue
        try:
            c.execute(_insert_tmpl, row)
        except Exception, e:
            print "Error on line '%s'" % row, e


    conn.commit()
    c.close()

def _guess_types(fileobj, max_sample_size=100):
    '''Guess column types (as for SQLite) of CSV.

    :param fileobj: read-only file object for a CSV file.
    '''
    reader = csv.reader(fileobj)
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
    for count,row in enumerate(reader):
        for idx,cell in enumerate(row):
            cell = cell.strip()
            # replace ',' with '' to improve cast accuracy for ints and floats
            cell = cell.replace(',', '')
            for key,cast in options:
                try:
                    # for null cells we can assume success
                    if cell:
                        cast(cell)
                    results[idx][key] += 1
                # shz: ignore all exceptions
                except (Exception), inst:
                    pass
        if count >= max_sample_size:
            break
    for idx,colresult in enumerate(results):
        for _type, dontcare in options:
            if colresult[_type] == count + 1:
                types[idx] = _type
    return types


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print('''csv2sqlite.py {csv-file-path} {sqlite-db-path} [{table-name}]

Convert a csv file to a table in an sqlite database (which need not yet exist).

* table-name is optional and defaults to 'data'
''')
        sys.exit(1)
    convert(*sys.argv[1:])
