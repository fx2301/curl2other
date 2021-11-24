"""
Scrapes curl options from master branch on github. Persists the options in `curl_options.json` for use at runtime.

Requires requests library:
$ pip3 install requests
"""
import json
import re
import requests

r = requests.get('https://raw.githubusercontent.com/curl/curl/master/src/tool_listhelp.c')
help = r.content.decode('UTF-8')

# NOTE: there are more aliases under the hood - see https://raw.githubusercontent.com/curl/curl/master/src/tool_getparam.c

OPTION_REGEX = r'\{"\s*' + \
    r'(?:(?P<alias>-.), )?' + \
    r'(?P<option>[^" ]+)' + \
    r'(?: (?P<argument><[^>]+>))?' + \
r'",'
options = [option.groupdict() for option in re.compile(OPTION_REGEX).finditer(help)]

with open('curl_options.json', 'w') as f:
    json.dump(options, f, indent=2)