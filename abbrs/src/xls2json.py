# -*- coding: utf-8 -*-

#
# need xlrd - use 'easy_install xlrd'  - see http://www.python-excel.org/

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from xlrd import open_workbook
import json
import os

dbg = False

locs = []

# doing it wrong.
files = os.walk('../xls')
for ent in files:
    (path,dirs,files) = ent
    if(path.find("/.svn") != -1):
        continue
    for file in files:
        if(file.endswith('.xls')):
            locs.append(file.split('.')[0])

#testing
#locs = ['ru']

for loc in locs:
    print 'Locale: %s' % (loc)
    exceptionEntries = set()
    nonExceptionEntries = set()
    wbfn = '../xls/%s.xls' % (loc)
    wb = open_workbook(wbfn)
    nrows = 0
    for s in wb.sheets():
        header = []
        for col in range(s.ncols):
            header.append(s.cell(0,col).value)

        # the header row counts
        nrows = nrows + 1

        # short sheet?
        if(len(header)==0):
            continue
        print ' Sheet Header: %s' % (','.join(header))

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

        if(entryHeader==-1 or exceptionHeader==-1):
            print '   Skipping this sheet: could not find entryHeader and exceptionHeader in %s' % (loc)
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

            entry = str(values[entryHeader])
            isException = str(values[exceptionHeader])
            if(isException == 'Yes'):
                exc = True
            elif(isException == 'yes'):
                exc = True
            elif(isException == 'No'):
                exc = False
            elif(isException == 'no'):
                exc = False
            else:
                print 'Unknown true/false value %s' % (isException)
                exc = True

            #print "Entry %s, exception %s" % (entry,exc)
            #entries.append((entry,exc))
            if(exc):
                exceptionEntries.add(entry)
            else:
                nonExceptionEntries.add(entry)
    # unique (just for statistics) - union
    uniqueEntries = exceptionEntries | nonExceptionEntries
    # remaining:  the exceptions, MINUS those which are also non-exceptions.
    remainEntries = exceptionEntries - nonExceptionEntries

    print "Locale %s: %d rows processed, %d exception entries, %d nonexception (%d unique) - %d total usable" % (loc, nrows, len(exceptionEntries), len(nonExceptionEntries), len(uniqueEntries), len(remainEntries))

    #print 'Entries: ','|'.join(remainEntries)
    data = {};
    data['abbrs'] = list(remainEntries);
    data['abbrs'].sort()
    jsonOut = { 'about': { 'id': loc, 'comment': "COMMENT" }, 'data': data };
    fn = '../json/%s.json' % (loc)
    f = open(fn, 'wb')
    jsonOut['about']['comment'] = "Generated from %s - %d rows processed, %d exception entries, %d nonexception (%d unique) - %d total usable" % (wbfn, nrows, len(exceptionEntries), len(nonExceptionEntries), len(uniqueEntries), len(remainEntries))
    print >>f, json.dumps(jsonOut, sort_keys=True, indent=4)
    print "*** Wrote %s with %d entries" % (fn,len(remainEntries))
    print
    
