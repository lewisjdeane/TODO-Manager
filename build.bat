@echo off

echo.
echo Starting build...

pyinstaller -v >nul 2>&1 && (
	pyinstaller --onefile --log-level ERROR todo.py

	SET p=%cd%\dist

	echo Build successful! Executable added to '%p%'.
	echo Add '%p%' to your path to run 'todo' from anywhere.
) || (
	echo Build failed. 'Pyinstaller' is needed to generate an executable.
	echo Install 'Pyinstaller' with 'pip' and try again, or alternatively, you can paste
	echo the python files into the root of any necessary directories and run it as a python
	echo script from there using 'python todo.py ARGS'.
)

echo.