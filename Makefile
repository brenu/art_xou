exe:
	del /S /Q "dist/windows"
	if not exist "dist/windows" mkdir "dist/windows"
	pyinstaller main.py --icon="assets/icons/game_icon.ico" --onefile --noconsole
	xcopy /E /Q "assets" "dist\windows\assets"
	xcopy /Q "dist\main.exe" "dist\windows"
	ren "dist\windows\main.exe" "art_xou.exe"
	del "dist\main.exe"

appimage:
	pip install python-appimage
	python-appimage build app -p 3.10 .
	mkdir -p dist/linux/data
	rm -r -f dist/linux/data/*
	rm -f dist/linux/art_xou-x86_64.AppImage
	cp -R assets source main.py dist/linux/data
	cp art_xou-x86_64.AppImage dist/linux/art_xou.AppImage
