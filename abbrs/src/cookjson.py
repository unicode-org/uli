# -*- coding: utf-8 -*-
# by srl
#
# Cook the ULI JSON by loading CLDR data

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import json
import os

dbg = False

locs = []

# doing it wrong.
files = os.walk('../json')
for ent in files:
    (path,dirs,files) = ent
    if(path.find("/.svn") != -1):
        continue
    for file in files:
        if(file.endswith('.json')):
            locs.append(file.split('.')[0])

#testing
#locs = ['de']

# TODO: read this from argv[1]
# cldr-json must be local or symlink
CLDR_JSON='./cldr-json'

for loc in locs:
    print 'Locale: %s' % (loc)


    #print(data)

    ulifn= '../json/%s.json' % (loc)
    ulif = open(ulifn, 'rb')
    data = json.load(ulif)
    ulif.close()


    cldr = {}

    # don't load all of cldr
    subfiles = ['ca-gregorian']

    for subfile in subfiles:
        fni = '%s/main/%s/%s.json' % (CLDR_JSON, loc, subfile)
        print "Reading %s" % (fni)
        fi  = open(fni, 'rb')
        cldr[subfile] = json.load(fi)
        fi.close()

    # read ULI data
    abbrs = set(data['data']['abbrs'])

    # TODO: parameterize, use all calendars. Additional items.
    lists = [cldr["ca-gregorian"]["main"][loc]["dates"]["calendars"]["gregorian"]["months"]["format"]["abbreviated"], cldr["ca-gregorian"]["main"][loc]["dates"]["calendars"]["gregorian"]["days"]["format"]["abbreviated"],cldr["ca-gregorian"]["main"][loc]["dates"]["calendars"]["gregorian"]["eras"]["eraAbbr"]]

    # list of stuff to add
    #print lists
    len0 = len(abbrs)
    print "len: %d" % len(abbrs)

    for cldrlist in lists:
        for k in cldrlist.keys():
            v = cldrlist[k]
            # print v
            # TODO: use other abbrs besides '.'.  Find out which items cause break.
            if v[len(v)-1] == '.':
                # ends with dot
                abbrs.add(v)

    len1 = len(abbrs)

    print "new len: %d - added %d" % (len(abbrs), (len1-len0))
    #abbrs.sort()
    # copy back
    data['data']['abbrs'] = list(abbrs)
    data['data']['abbrs'].sort()

    # changed from @cldrVersion to _cldrVersion
    cldrver = cldr["ca-gregorian"]["main"][loc]["identity"]["version"]["_cldrVersion"]


    if len1 > len0:
        data['about']['cooked'] = 'Loaded %d abbrs from CLDR %s' % (len1-len0, cldrver)
        data['about']['cldrVer'] = cldrver
    else:
        data['about']['cooked'] = 'No abbrs loaded from CLDR %s' % (cldrver)

    fn = '../json-cooked/%s.json' % (loc)
    f = open(fn, 'wb')
    print >>f, json.dumps(data, sort_keys=True, indent=4)
