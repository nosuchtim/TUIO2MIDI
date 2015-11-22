default:
	rm -fr tuio2midi dist build
	c:\python27\python setup.py py2exe
	mv dist tuio2midi
	copy msvcp100.dll tuio2midi
	copy msvcr100.dll tuio2midi
	zip32 -r tuio2midi.zip tuio2midi
	rm -fr tuio2midi build

clean :
	rm -f *~ *.bak *.pyc
