#!/usr/bin/python
# -*- coding: utf-8 -*-

# create a '-unique.txt' file from each xls.
#
# need xlrd - use 'easy_install xlrd'  - see http://www.python-excel.org/

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from xlrd import open_workbook
import json
import os

dbg = False

files = []

for wbfn in sys.argv[1::]:
    print 'Opening File: %s' % (wbfn)
    entries = set()
    wb = open_workbook(wbfn)
    nrows = 0
    print '.. reading'
    for s in wb.sheets():
        header = []
        for col in range(s.ncols):
            header.append(str(s.cell(0,col).value))

        # the header row counts
        nrows = nrows + 1

        # short sheet?
        if(len(header)==0):
            continue
        print header
        print '.. Sheet Header: %s' % str(','.join(header))

        # now, find the headers we want
        # Entry example,Full entry name,Example tested,isException,Note
        entryHeader = -1
        exceptionHeader = -1

        for i in range(len(header)):
            if header[i]=='Entry example':
                entryHeader = i
            elif header[i]=='Abbreviation':
                entryHeader = i
            elif header[i]=='isException':
                exceptionHeader = i
            elif header[i]=='Exception?':
                exceptionHeader = i

        if(entryHeader==-1):
            print '   Skipping this sheet: could not find entryHeader and exceptionHeader in sheet %s' % (s.name)
            continue
            # exit?

        #print "EntryHeader %d, exceptionHeader %d" % (entryHeader,exceptionHeader)

        rows = []
        for row in range(1,s.nrows):
            nrows = nrows + 1
            values = []
            for col in range(s.ncols):
                values.append(s.cell(row,col).value)
            rows.append(values)

            entry = str(values[entryHeader]).strip()

            if(len(entry)==0):
                if dbg:
                    print "Skipping empty value on row %d" % row
                continue

            entries.add(entry)

    print ".. Read %s: %d rows processed, %d entries unique. Writing.." % (wbfn, nrows, len(entries))

    fn = '%s-unique.txt' % (wbfn)
    f = open(fn, 'wb')
    aslist = list(entries)
    aslist.sort()
    for entry in aslist:
        print >>f, "%s" % (entry)
    f.close()
    print ".. Wrote %s with %d entries" % (fn,len(entries))
    print

