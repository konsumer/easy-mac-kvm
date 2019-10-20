#!/bin/sh

# just a simple wrapper for OSX to keep the params working the same

hdiutil convert "${1}" -format UDTO -o "${2}"
mv "${2}.cdr" "${2}"