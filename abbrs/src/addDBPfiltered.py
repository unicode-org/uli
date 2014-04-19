# -*- coding: utf-8 -*-

#
# need xlutils (and xlrd/xlwt) - use 'easy_install xlutils'  - see http://www.python-excel.org/
# srl

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from xlrd import open_workbook
from xlwt import easyxf
from xlutils.copy import copy

import argparse
import json
import os
import string

dbg = False

## FUNCTIONS ##

# this really needs to be made common!
def scanHeader(sheet):
    '''Scan a header for common markers. Return a dictionary or None'''

    if args.verbose > 2: print 'Scanning headers of sheet %s' % (sheet.name)
    # create array of header strings
    header = []

    for col in range(sheet.ncols):
        header.append(str(sheet.cell_value(0,col)).strip()) # do cast this to string

    # short sheet?
    if(len(header)==0):
        if args.verbose > 4:
            print 'short sheet'
        return None

    if args.verbose > 8: print ' Raw Sheet Header: %s' % (','.join(header))

    # now, find the headers we want
    # Entry example,Full entry name,Example tested,isException,Note
    entryHeader = -1
    exceptionHeader = -1

    hdrMap = {}

    unknownHeaders = set()

    for i in range(len(header)):

        if header[i]=='Entry example'  or header[i]=='Abbreviation':
            hdrMap['entryHeader'] = i
        elif header[i]=='isException' or header[i]=='Exception?':
            hdrMap['exceptionHeader'] = i
        elif header[i]=='Percentage in TMB memory':
            hdrMap['tmbPercentageHeader'] = i
        elif header[i]=='Usage Frequency':
            hdrMap['usage'] = i
        elif header[i]=='Full entry name' or header[i]=='Full form':
            hdrMap['full'] = i
        elif header[i]=='Translation to English' or header[i]=='English':
            hdrMap['english'] = i
        elif header[i]=='Comment' or header[i]=='comments':
            hdrMap['comment'] = i
        else:
            unknownHeaders.add(header[i])

    if len(unknownHeaders)>0 and args.verbose>4:
        print 'Unknown headers: %s' % unknownHeaders

    if len(hdrMap)==0:
        if args.verbose>4:
            print 'no headers found'
        return None

    if args.verbose>4:
        print hdrMap
    return hdrMap

def insertLoc(newstr,data,start=1,reverse=True):
    newstr = string.lower(newstr) # normalize
    '''Calculate rough insertion location'''
    searchRange = range(start,len(data))
    if(reverse):
        searchRange.reverse()
        for n in searchRange:
            if string.lower(data[n]) < newstr:
                return n+1 # found
        return start
    else:
        for n in searchRange:
            if string.lower(data[n]) > newstr:
                return n # found
        return len(data) # end


parser = argparse.ArgumentParser(description='Incorporate DBpedia data, filtered according to a TMB controlfile', epilog='ULI tool, http://uli.unicode.org')
parser.add_argument('-u',
                    '--uli',
                    action='store',
                    help='set the original ULI xls file, such as "de.xls"',
                    dest='ulixls',
                    required=True)
parser.add_argument('-d',
                    '--dbpedia',
                    action='store',
                    help='set the original DBpedia xls file, such as "de_dbpedia.xls"',
                    dest='dbxls',
                    required=True)
parser.add_argument('-t',
                    '--tmb',
                    action='store',
                    help='set the original TMB (filter) xls file, such as "TMB_de.xls"',
                    dest='tmbxls',
                    required=True)
parser.add_argument('-o',
                    '--out',
                    action='store',
                    help='set the output xls file, such as "de_updated.xls"',
                    dest='outxls',
                    required=True)
parser.add_argument('--verbose',
                    '-v',
                    help='Increase verbosity',
                    action='count',
                    default=0)
args = parser.parse_args()

locs = []

if args.verbose>0: print 'Beginning ULI->DBpedia->TMB->ULI processing..'

def getEntryList(sheet, hdrMap):
    ''' given a sheet and headermap, get a list of the entry strings (including None for row 0, header)'''
    data = []
    data.append(None)
    for row in range(1, sheet.nrows):
        entry = sheet.cell_value(row, hdrMap['entryHeader']).strip()
        data.append(entry)
    return data

def getEntryMap(tmbxls, needTMB=False, needExamples=False):
    ''' get a map of TMB entries '''
    # the TMB workbook. This is the 'filter' on the DBpedia workbook.
    with open_workbook(tmbxls) as wbtmb: # don’t need formatting
        if args.verbose>0: print 'Read TMB workbook %s, with %d sheets' % (tmbxls, wbtmb.nsheets)

        for s in wbtmb.sheets():
            hdrMap = scanHeader(s)
            if hdrMap == None:
                if args.verbose>4: print ".. no headers found"
            elif not hdrMap.has_key('entryHeader'):
                if args.verbose>4: print ".. entryHeader not found"
            elif needTMB and not hdrMap.has_key('tmbPercentageHeader'):
                if args.verbose>4: print ".. tmbPercentageHeader not found"
            else:
                # got some TMB data
                tmbMap = {}
                for row in range(1, s.nrows):
                    # get entry name (primary key)
                    entry = unicode(s.cell_value(row, hdrMap['entryHeader'])).strip()
                    if(len(entry)==0):
                        if args.verbose > 4: print "skipping empty value on row %d" % (row)
                        continue
                    # create or load dict
                    if(tmbMap.has_key(entry)):
                        entryDict = tmbMap[entry]
                        if args.verbose > 8: print "Note: duplicate TMB entry %s" % (entry)
                    else:
                        entryDict = {}
                    # load any data
                    if needTMB:
                        entryDict['tmbPercent'] = s.cell_value(row, hdrMap['tmbPercentageHeader']) # may be %
                    if needExamples:
                        if hdrMap.has_key('full'):
                            entryDict['full'] = s.cell_value(row, hdrMap['full'])
                        else:
                            entryDict['full'] = ''
                        if hdrMap.has_key('english'):
                            entryDict['english'] = s.cell_value(row, hdrMap['english'])
                        else:
                            entryDict['english'] = ''
                    # store data to map
                    tmbMap[entry] = entryDict
                if len(tmbMap) == 0:
                    if args.verbose>0: print 'Note: TMB headers but no TMB data.'
                else:
                    if args.verbose>0: print 'Read %d lines of data from %s (%d row sheet including header)' % (len(tmbMap), tmbxls, s.nrows)
                    return tmbMap

    if args.verbose>0: print 'No TMB data found in %s, error' % (tmbxls)
    return None

def findSheet(wb):
    ''' returns the sheet with data. Returns (sheet, sheetnum, hdrmap)'''
    if args.verbose>7: print "Scanning workbook (findSheet).."
    for sheetnum in range(wb.nsheets):
        s = wb.sheet_by_index(sheetnum)
        hdrMap = scanHeader(s)
        if hdrMap == None:
            if args.verbose>7: print ".. no headers found on sheet %d" % sheetnum
        elif not hdrMap.has_key('entryHeader'):
            if args.verbose>7: print ".. no entryHeader on sheet %d" % sheetnum
        else:
            if args.verbose>7: print "found sheetnum %d" % sheetnum
            return (s, sheetnum, hdrMap)
    # not found
    return (None,None,None)


# First, we need to get a list (probably a map) of the TMB entries we will be adding.
tmbMap = getEntryMap(args.tmbxls, needTMB=True)
tmbSet = set(tmbMap.keys())

if not tmbMap:
    print 'No TMB data in %s, exitting' % (args.tmbxls)
    sys.exit(1)

newRowColor = 'pattern: pattern solid, fore_colour light_orange;'
newRowStyle = easyxf(newRowColor)
newRowStylePct0 = easyxf(newRowColor, num_format_str='0%')
newRowStylePct4 = easyxf(newRowColor, num_format_str='0.00000%')
headingStyle = easyxf('Font: bold true;')
plainStyle = easyxf('')

styleCache = None

def cacheStyle(xf_index, wbuli):
    global styleCache
    if styleCache == None:
        # must be a way to do this more easily..
        styleCache = []
        for n in range(0,len(wbuli.xf_list)):
            styleCache.insert(n,None)
    if styleCache[xf_index] == None:
        xf= wbuli.xf_list[xf_index]
        fmt=wbuli.format_map[xf.format_key]
        format_str=fmt.format_str
        font=wbuli.font_list[xf.font_index]
        if args.verbose>8: print 'Caching style %d,  nfs=%s, fg=%d bg=%d bold=%d' % (xf_index, format_str, xf.background.pattern_colour_index, xf.background.background_colour_index, font.bold)
        styleStr = ""
        if (font.bold != 0):
            styleStr = styleStr + "Font: bold on;"
        styleCache[xf_index] = easyxf(styleStr, num_format_str=format_str)
        # then, set these two directly
        styleCache[xf_index].pattern.pattern = xf.background.fill_pattern
        styleCache[xf_index].pattern.pattern_back_colour = xf.background.background_colour_index;
        styleCache[xf_index].pattern.pattern_fore_colour = xf.background.pattern_colour_index;
    return styleCache[xf_index]

# The original workbook. Will be copied.
with open_workbook(args.ulixls, formatting_info=True) as wbuli:
    if args.verbose>0: print 'Read ULI workbook %s, with %d sheets' % (args.ulixls, wbuli.nsheets)
    ## Setup output sheet
    wb    = copy(wbuli)
    if args.verbose>0: print 'Will write output to %s' % (args.outxls)

    ## Get list of input items
    uliMap = getEntryMap(args.ulixls)
    uliSet = set(uliMap.keys())

    ## *gulp* read dbPedia map
    dbpMap = getEntryMap(args.dbxls, needExamples=True)
    dbpSet = set(dbpMap.keys())

    ## now, what is the delta?
    newSet = tmbSet - uliSet
    dupSet = tmbSet & uliSet
    if args.verbose>1: print 'TMB keys: %d, ULI keys: %d.  %d to add, %d dup' % (len(tmbSet), len(uliSet), len(newSet), len(dupSet))

    ## locate correct sheet for output
    (uliSheet,uliSheetNum, uliHdr) = findSheet(wbuli)
    if uliSheet == None:
        print 'ERROR: could not find input sheet in %s' % (ulixls)
        sys.exit(1)

    # get the output sheet
    outSheet = wb.get_sheet(uliSheetNum)

    # get a list of the output entries - for sheet insertion.
    # when we insert into the sheet, we will update this.
    outEntryList = getEntryList(uliSheet, uliHdr)
    # list of source row lines, or None for 'new' lines.
    outEntryRows = range(0,len(outEntryList))

    if len(newSet)==0:
        if args.verbose>1: print 'No new entries to add.'
    else:
        ## First, let's add in the additional lines.
        addList = list(newSet)
        addList.sort()
        for addEntry in addList:
            addLoc = insertLoc(addEntry, outEntryList)
            if args.verbose>5: print '+ Add: "%s" to loc %d/%d' % (addEntry, addLoc, len(outEntryList))
            outEntryList.insert(addLoc, addEntry)
            outEntryRows.insert(addLoc, None) # marker - "new row"

    ##Write Changed Rows
    if args.verbose>0: print 'Calculating changed lines..'
    #outSheet.cell_overwrite_ok=True
    for row in range(0,len(outEntryRows)):
        aRow = outSheet.row(row)
        aRow.set_style(plainStyle)
        if outEntryRows[row] == None:
            addEntry = outEntryList[row]
            for col in range(0, uliSheet.ncols):
                ## new row.
                aStyle = newRowStyle
                value = None
                if col == uliHdr['entryHeader']:
                    value = addEntry
                elif col == uliHdr['usage']:
                    value = .51
                    aStyle = newRowStylePct0
                elif col == uliHdr['tmbPercentageHeader']:
                    value = tmbMap[addEntry]['tmbPercent']
                    aStyle=newRowStylePct4
                elif col == uliHdr['english']:
                    value = dbpMap[addEntry]['english']
                elif col == uliHdr['full']:
                    value = dbpMap[addEntry]['full']
                elif col == uliHdr['comment']:
                    value = 'Updated from DBpedia/IBM TMB'
                elif col == uliHdr['exceptionHeader']:
                    value = 'Yes'
                aRow.write(col, value, style=aStyle)
        else:
            inRow = uliSheet.row(outEntryRows[row])
            for col in range(0,len(inRow)):
                # http://stackoverflow.com/questions/3723793/preserving-styles-using-pythons-xlrd-xlwt-and-xlutils-copy
                cell=inRow[col]
                xf_index=cell.xf_index

                if row == 0:
                    theStyle = headingStyle
                else:
                    theStyle = cacheStyle(xf_index, wbuli)
                aRow.write(col, inRow[col].value, theStyle); # TODO style
            aRow.height = uliSheet.rowinfo_map[outEntryRows[row]].height

    ## SAVE
    if args.verbose>0: print 'Saving to %s' % (args.outxls)
    wb.save(args.outxls)
    if args.verbose>0: print '..saved'

    print "## Duplicates - please check manually"
    print dupSet


