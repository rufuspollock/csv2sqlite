Script to load CSV into an SQLite database (with type guessing!).

Note if you are looking for something more powerful (but also a bit more
complex) check out:

* [Data Converters](http://okfnlabs.org/dataconverters/)
* [Messy Tables](http://github.com/okfn/messytables/)

## Usage

Grab the script and download to your local machine. Then do:

    csv2sqlite.py {csv-file-path} {sqlite-db-path} [{table-name}]

* table-name is optional and defaults to 'data'

