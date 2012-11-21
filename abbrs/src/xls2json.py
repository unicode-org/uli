# -*- coding: utf-8 -*-

#
# need xlrd - use 'easy_install xlrd'  - see http://www.python-excel.org/

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from xlrd import open_workbook
import json
import os

#testing
#locs = ['en']
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

for loc in locs:
    print 'Locale: %s' % (loc)
    exceptionEntries = set()
    nonExceptionEntries = set()
    wb = open_workbook('../xls/%s.xls' % (loc))
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
            elif header[i]=='isException':
                exceptionHeader = i
            elif header[i]=='Exception?':
                exceptionHeader = i

        if(entryHeader==-1 and exceptionHeader==-1):
            print '   Skipping this sheet: could not find entryHeader and exceptionHeader in %s' % (loc)
            continue
            # exit?
        

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

    #print 'Entries: '
    #print ' ','|'.join(remainEntries)
    jsonOut = {};
    jsonOut[loc] = list(remainEntries);
    jsonOut[loc].sort()
    #print json.dumps(jsonOut, sort_keys=True, indent=4)
    fn = '../json/%s.js' % (loc)
    f = open(fn, 'wb')
    print >>f, '// Generated from %s.xls' % (loc)
    print >>f, "// For locale %s: %d rows processed, %d exception entries, %d nonexception (%d unique) - %d total usable" % (loc, nrows, len(exceptionEntries), len(nonExceptionEntries), len(uniqueEntries), len(remainEntries))
    print >>f, json.dumps(jsonOut, sort_keys=True, indent=4)
    print "*** Wrote %s with %d entries" % (fn,len(remainEntries))
    print
    
