# -*- coding: utf-8 -*-
# by srl

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
CLDR_JSON='/home/srl/src/cldr-aux/json/22.1'

for loc in locs:
    print 'Locale: %s' % (loc)
    fni = '../json/%s.json' % (loc)
    fi  = open(fni, 'rb')
    data = json.load(fi)
    fi.close()

    #print(data)

    cldrfn = '%s/main/%s.json' % (CLDR_JSON, loc)
    cldrf = open(cldrfn, 'rb')
    cldr = json.load(cldrf)
    cldrf.close()

    # read ULI data
    abbrs = list(data['data']['abbrs'])

    lists = [cldr["dates"]["calendars"]["gregorian"]["months"]["format"]["abbreviated"], cldr["dates"]["calendars"]["gregorian"]["days"]["format"]["abbreviated"],cldr["dates"]["calendars"]["gregorian"]["eras"]["eraAbbr"]]

    # list of stuff to add
    #print lists
    len0 = len(abbrs)
    print "len: %d" % len(abbrs)

    for cldrlist in lists:
        for k in cldrlist.keys():
            v = cldrlist[k]
            # print v
            if v[len(v)-1] == '.':
                # ends with dot
                abbrs.append(v)

    len1 = len(abbrs) 

    print "new len: %d - added %d" % (len(abbrs), (len1-len0))
    abbrs.sort()
    # copy back
    data['data']['abbrs'] = abbrs
    if len1 > len0:
        data['about']['cooked'] = 'Loaded %d abbrs from CLDR' % (len1-len0)
    else:
        data['about']['cooked'] = 'No abbrs loaded from CLDR'

    fn = '../json-cooked/%s.json' % (loc)
    f = open(fn, 'wb')
    print >>f, json.dumps(data, sort_keys=True, indent=4)
    

