#!/usr/bin/env python

import StringIO
import csv
import os
import sqlite3
import tempfile
import unittest

from csv2sqlite import convert

DEFAULT_TABLE_NAME = 'data'
TEMP_DB_PATH = os.path.join(tempfile.gettempdir(), 'csv2sqlite-test.sqlite')

class Csv2SqliteTestCase(unittest.TestCase):
    def setUp(self):
        if os.path.exists(TEMP_DB_PATH):
            os.remove(TEMP_DB_PATH)

    def convert_csv(self, csv, table = DEFAULT_TABLE_NAME):
        '''Converts a CSV file to a SQLite database and returns a database cursor
           into the resulting file'''
        dbpath = TEMP_DB_PATH
        convert(StringIO.StringIO(csv), dbpath, table)
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
        row = c.next()
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
        row = c.next()
        self.assertEqual(row[0], 3)

    def test_strips_headers(self):
        c = self.convert_csv('''col_a    , col_b''')
        c.execute('SELECT sql FROM sqlite_master WHERE name = "%s"' % DEFAULT_TABLE_NAME)
        row = c.next()
        self.assertEqual(row[0], 'CREATE TABLE data ("col_a" text,"col_b" text)')

    def test_ignores_nulls_when_guessing_col_types(self):
        '''Ignore nulls when guessing column types'''
        c = self.convert_csv(
    '''col_a, col_b
    ,
    ,
    1,text'''
        )
        c.execute('SELECT sql FROM sqlite_master WHERE name = "%s"' % DEFAULT_TABLE_NAME)
        row = c.next()
        self.assertEqual(row[0], 'CREATE TABLE data ("col_a" integer,"col_b" text)')

if __name__ == '__main__':
    unittest.main()
