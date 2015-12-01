default:
	rm -fr tuio2midi dist build
	c:\python27\python setup.py py2exe --includes sip
	mv dist tuio2midi
	copy msvcp100.dll tuio2midi
	copy msvcr100.dll tuio2midi
	rm -fr build
	cd installer
	"c:\Program Files\InstallMate 9\BinX64\tin.exe" /build tuio2midi.iw9
	cd ..
	copy installer\TUIO2MIDI\TUIO2MIDI\*.* p:\tmp\tuio2midi
	rm -fr *~ *.bak *.pyc build tuio2midi tuio2midi.zip

clean :
	rm -fr *~ *.bak *.pyc build tuio2midi tuio2midi.zip
