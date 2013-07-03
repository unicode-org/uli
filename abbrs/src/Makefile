#
#
#

# edit Makefile.local to include:  CLDR_JSON=/home/srl/src/cldr-aux/json/22.1

include Makefile.local

all:	spread cook xml

spread:
	python ./xls2json.py

cook:
	@if [ ! -f ./cldr-json/main/root/ca-gregorian.json ]; \
	then \
		echo "Error: ./cldr-json needs to be a symlink to the latest CLDR JSON data" ; \
		exit 1 ; \
	fi
	python ./cookjson.py

xml:
	python ./json2cldr.py
	@if [ ! -f ./cldr.jar ]; \
	then \
		echo "Error: ./cldr.jar needs to be a symlink to the latest cldr.jar" ; \
		exit 1 ; \
	fi
	java -classpath ./cldr.jar org.unicode.cldr.util.XMLValidator ../xml/*.xml

.PHONY:	spread cook all 
