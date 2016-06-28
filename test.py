#!/usr/bin/env python

import os
import sqlite3
import tempfile
import unittest
import bz2
import gzip
from io import BytesIO, StringIO

from csv2sqlite import convert

DEFAULT_TABLE_NAME = 'data'
TEMP_DB_PATH = os.path.join(tempfile.gettempdir(), 'csv2sqlite-test.sqlite')

class Csv2SqliteTestCase(unittest.TestCase):
    def setUp(self):
        if os.path.exists(TEMP_DB_PATH):
            os.remove(TEMP_DB_PATH)

    def convert_csv(self, csv, table = DEFAULT_TABLE_NAME, headers = None, types = None):
        '''Converts a CSV to a SQLite database and returns a database cursor
           into the resulting file'''
        dbpath = TEMP_DB_PATH
        if headers is not None:
            try:
                headerObj = StringIO(headers)
            except TypeError:
                headerObj = BytesIO(headers)
        else:
            headerObj = None
        if types is not None:
            try:
                typeObj = StringIO(types)
            except TypeError:
                typeObj = BytesIO(types)
        else:
            typeObj = None
        try:
            infile = StringIO(csv) # Python 3
        except:
            infile = BytesIO(csv)  # Python 2
        convert(infile, dbpath, table, headerObj, None, typeObj)
        conn = sqlite3.connect(dbpath)
        c = conn.cursor()
        return c

    def convert_file(self, path, table = DEFAULT_TABLE_NAME, compression = None):
        '''Converts a CSV file to a SQLite database and returns a database cursor
           into the resulting file'''
        dbpath = TEMP_DB_PATH
        convert(path, dbpath, table, compression=compression)
        conn = sqlite3.connect(dbpath)
        c = conn.cursor()
        return c

    def test(self):
        '''Simple test case'''
        c = self.convert_csv(
    '''heading_1,heading_2,heading_3
    abc,1,1.0
    xyz,2,2.0
    efg,3,3.0'''
        )
        c.execute('SELECT COUNT(heading_3) FROM %s' % DEFAULT_TABLE_NAME);
        row = next(c)
        self.assertEqual(row[0], 3)

    def test_semicolon(self):
        '''Simple test case (semicolon)'''
        c = self.convert_csv(
    '''heading_1;heading_2;heading_3
    abc;1;1,0
    xyz;2;2,0
    efg;3;3,0'''
        )
        c.execute('SELECT COUNT(heading_3) FROM %s' % DEFAULT_TABLE_NAME);
        row = next(c)
        self.assertEqual(row[0], 3)

    def test_separate_headers(self):
        '''Headers passed separately test case.'''
        csv = '''abc,1,1,0
              xyz,2,2,1'''
        headers = '''heading_1,heading_2,heading_3,heading_4'''
        c = self.convert_csv(csv, headers=headers)
        c.execute('SELECT COUNT(heading_3) FROM %s' % DEFAULT_TABLE_NAME);
        row = next(c)
        self.assertEqual(row[0], 2)

    def test_strips_headers(self):
        c = self.convert_csv('''col_a    , col_b''')
        c.execute('SELECT sql FROM sqlite_master WHERE name = "%s"' % DEFAULT_TABLE_NAME)
        row = next(c)
        self.assertEqual(row[0], 'CREATE TABLE data ("col_a" text,"col_b" text)')

    def test_separate_types(self):
        '''Types passed separately test case.'''
        csv = "one,two,three\n1,1,abc\n2,2,xyz"
        types = "integer,real,text"
        c = self.convert_csv(csv, types=types)
        c.execute('PRAGMA table_info(%s)' % DEFAULT_TABLE_NAME)
        row = next(c)
        self.assertEqual(row[2], 'integer')
        row = next(c)
        self.assertEqual(row[2], 'real')
        row = next(c)
        self.assertEqual(row[2], 'text')

    def test_ignores_nulls_when_guessing_col_types(self):
        '''Ignore nulls when guessing column types'''
        c = self.convert_csv(
    '''col_a, col_b
    ,
    ,
    1,text'''
        )
        c.execute('SELECT sql FROM sqlite_master WHERE name = "%s"' % DEFAULT_TABLE_NAME)
        row = next(c)
        self.assertEqual(row[0], 'CREATE TABLE data ("col_a" integer,"col_b" text)')

    def test_csv_file(self):
        '''Should handle uncompressed files.'''
        (_, csvFile) = tempfile.mkstemp()
        with open(csvFile, 'wb') as csvFileObj:
            csvFileObj.write(b'''heading_1,heading_2,heading_3
                             abc,1,1.0
                             xyz,2,2.0
                             efg,3,3.0''')
        c = self.convert_file(csvFile)
        c.execute('SELECT COUNT(heading_3) FROM %s' % DEFAULT_TABLE_NAME)
        row = next(c)
        self.assertEqual(row[0], 3)
        os.remove(csvFile)

    def test_gzip_file(self):
        '''Should handle gzip compressed files.'''
        (_, gzFile) = tempfile.mkstemp()
        with gzip.open(gzFile, 'wb') as gzFileObj:
            try:
                gzFileObj.write('''heading_1,heading_2,heading_3
                                abc,1,1.0
                                xyz,2,2.0
                                efg,3,3.0''')
            except TypeError:
                gzFileObj.write(bytes('''heading_1,heading_2,heading_3
                                abc,1,1.0
                                xyz,2,2.0
                                efg,3,3.0''', 'utf8'))
        c = self.convert_file(gzFile, compression='gzip')
        c.execute('SELECT COUNT(heading_3) FROM %s' % DEFAULT_TABLE_NAME)
        row = next(c)
        self.assertEqual(row[0], 3)
        os.remove(gzFile)

    def test_bz2_file(self):
        '''Should handle bz2 compressed files.'''
        (_, bz2File) = tempfile.mkstemp()
        with bz2.BZ2File(bz2File, 'wb') as bz2FileObj:
            try:
                bz2FileObj.write('''heading_1,heading_2,heading_3
                                abc,1,1.0
                                xyz,2,2.0
                                efg,3,3.0''')
            except TypeError:
                bz2FileObj.write(bytes('''heading_1,heading_2,heading_3
                                abc,1,1.0
                                xyz,2,2.0
                                efg,3,3.0''', 'utf8'))
        c = self.convert_file(bz2File, compression='bz2')
        c.execute('SELECT COUNT(heading_3) FROM %s' % DEFAULT_TABLE_NAME)
        row = next(c)
        self.assertEqual(row[0], 3)
        os.remove(bz2File)

if __name__ == '__main__':
    unittest.main()
