#
# To setup:
#
#  ( needs python-devel or equivalent, libsxslt-devel or equivalent, and easy_install )
#
#  $ easy_install xlrd lxml 
#  $ ln -s <path-to>/cldr.jar .
#  $ ln -s <path-to-cldr-aux>/json/23.1 ./cldr-json
#  $ make
#

-include Makefile.local

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
	java -classpath ./cldr.jar org.unicode.cldr.util.XMLValidator ../xml/common/segments/*.xml && echo 'XML files OK'

.PHONY:	spread cook all 

merge:
	java  -DCLDR_DIR=./cldr -classpath ./cldr.jar:./icu4j.jar:./utilities.jar org.unicode.cldr.tool.CLDRModify -j../xml/common/segments/junk/ -ir -d./cldr-new -s./cldr/common/main/ -asegments
