"""
libs.strings

By default, uses `en-gb.json` file inside the `strings` top-level folder.

If language changes, set `libs.strings.default_locale` and run `libs.strings.refresh()`.
"""
import json

#now using this to handle all our error rresponse

default_locale = "en-gb"
cached_strings = {}


def refresh(): #it takes the global cached string and open it then load the language json file
    print("Refreshing...")
    global cached_strings
    with open(f"strings/{default_locale}.json") as f:
        cached_strings = json.load(f)


def gettext(name):
    return cached_strings[name] 
    #this actually gets the name of stored in our json

#Cashing means temporarily storing a piece of data that is being used multiple times, so it doesn't need to be generated or retrieved many times

refresh() # the cached_strings wait for the refresh() to load the file before have it's json content
