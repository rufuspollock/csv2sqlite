Script to load CSV into an SQLite database (with type guessing!).

Note if you are looking for something more powerful (but also a bit more
complex) check out:

* [Data Converters](http://okfnlabs.org/dataconverters/)
* [Messy Tables](http://github.com/okfn/messytables/)

## Usage

Download the script to your local machine. Then run:

```
csv2sqlite.py {csv-file-path} {sqlite-db-path} [{table-name}]
```

The `table-name` argument is optional and defaults to “data”. The script
supports several other options, all of which can be seen by running the script
with the `--help` argument:

```
usage: csv2sqlite.py [-h] [--headers [HEADERS]] [--types [TYPES]]
                     [--bz2 | --gzip]
                     csv_file sqlite_db_file [table_name]

Convert a CSV file to a table in a SQLite database. The database is created if
it does not yet exist.

positional arguments:
  csv_file             Input CSV file path
  sqlite_db_file       Output SQLite file
  table_name           Name of table to write to in SQLite file

optional arguments:
  -h, --help           show this help message and exit
  --headers [HEADERS]  Headers are read from this file, if provided.
  --types [TYPES]      Types are read from this file, if provided.
  --bz2                Input csv file is compressed using bzip2.
  --gzip               Input csv file is compressed using gzip.
```

By default, the script tries to guess the column types of the input CSV file by
checking the first 100 rows. The desired types can be enforced by supplying the
`--types` argument pointing at an auxiliary CSV file. The file should contain
one row specifying the types of all the column of the input CSV file. The
possible types are “integer”, “real”, and “string”.

## LICENSE

This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any
means.

In jurisdictions that recognize copyright laws, the author or authors
of this software dedicate any and all copyright interest in the
software to the public domain. We make this dedication for the benefit
of the public at large and to the detriment of our heirs and
successors. We intend this dedication to be an overt act of
relinquishment in perpetuity of all present and future rights to this
software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

For more information, please refer to <http://unlicense.org/>

