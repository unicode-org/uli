#
#
#

# edit Makefile.local to include:  CLDR_JSON=/home/srl/src/cldr-aux/json/22.1

include Makefile.local

all:	spread cook

spread:
	python ./xls2json.py

cook:
	python ./cookjson.py $(CLDR_JSON)


.PHONY:	spread cook all
