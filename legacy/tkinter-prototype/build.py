# build.py
import sys
import PyInstaller.__main__

# Increase recursion limit
sys.setrecursionlimit(5000)

# Call PyInstaller with the .spec file
PyInstaller.__main__.run([
    'fmea_app.spec',  # if you want a windowed app without the console
])
