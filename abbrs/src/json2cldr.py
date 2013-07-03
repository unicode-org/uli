# -*- coding: utf-8 -*-
# srl
import sys

reload(sys)
sys.setdefaultencoding("utf-8")

import json
import os
from lxml import etree

dbg = False

src_dir = '../json-cooked'
dst_dir = '../xml/common/segments'

comment = 'From ULI data, http://uli.unicode.org'
draft = 'provisional'
encoding = 'UTF-8' # of course
doctype = '<!DOCTYPE ldml SYSTEM "../../common/dtd/ldml.dtd">'

# list of locales
locs = []

# still doing it wrong.
files = os.walk(src_dir)
for ent in files:
    (path,dirs,files) = ent
    if(path.find("/.svn") != -1):
        continue
    for file in files:
        if(file.endswith('.json')):
            locs.append(file.split('.')[0])

#testing
#locs = ['en']

print '# Converting ULI JSON from %s to CLDR XML in %s' % (src_dir, dst_dir)

for loc in locs:
    print '#   %s' % (loc)
    fni = '%s/%s.json' % (src_dir, loc)
    fi = open(fni,"rb")
    data = json.load(fi)
    fi.close()

    abbrs = set(data['data']['abbrs'])
    # calculate bcp47 segments (todo use a real parser)
    locsplit = loc.split('_')
    nsegs = len(locsplit)
    language = None
    script = None
    region = None
    variant = None
    if dbg:
        print "locsplit = %s, len=%d" % (locsplit,nsegs)
    n=0
    if nsegs>n:
        language = locsplit[n]
        n = n + 1
    if nsegs>n and len(locsplit[n])==4: # it is a script code
        script = locsplit[n]
        n = n + 1
    if nsegs>n and len(locsplit[n])<4: #it is AB or 123 - a region
        region = locsplit[n]
        n = n + 1
    if nsegs>n:
        variant = locsplit[n]
        n = n + 1

    ldml = etree.Element('ldml')
    root = etree.ElementTree(ldml)
    identity = etree.Element('identity')
    identity.append(etree.Element('version',number='$Revision: $'))
    identity.append(etree.Element('generation',date='$Date: $'))
    if language:
        identity.append(etree.Element('language',type=language))
    if script:
        identity.append(etree.Element('script',type=script))
    if region:
        identity.append(etree.Element('region',type=region))
    if variant:
        identity.append(etree.Element('variant',type=variant))

    ldml.append(identity)
    segmentations = etree.Element('segmentations')
    segmentation = etree.Element('segmentation',type='SentenceBreak')
    exceptions = etree.Element('exceptions')
    for k in abbrs:
        exception = etree.Element('exception', draft=draft)
        exception.text = k
        exceptions.append(exception)
    segmentation.append(etree.Comment(comment))
    segmentation.append(exceptions)
    segmentations.append(segmentation)
    ldml.append(segmentations)

    str = etree.tostring(root,xml_declaration=True,pretty_print=True,encoding=encoding,doctype=doctype)
    if dbg:
        print str

    fn = '%s/%s.xml' % (dst_dir, loc)
    f = open(fn, 'wb')
    print >>f, str
    print '#        Wrote %d abbrs. to %s' % (len(abbrs),fn)
