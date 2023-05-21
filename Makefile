exe:


appimage:
	pip install python-appimage
	python-appimage build app -p 3.10 .
	mkdir -p dist/linux/data
	rm -r -f dist/linux/data/*
	rm -f dist/linux/art_xou-x86_64.AppImage
	cp -R assets source main.py dist/linux/data
	cp art_xou-x86_64.AppImage dist/linux/art_xou.AppImage
