import os
import sys
from functools import reduce
from typing import List

from wrapper import execute_options, to_options

IGNORED_OPTIONS = ['-v', '--verbose', '-s', '--silent']

def _fail(msg):
    sys.stderr.write('Aborting. ')
    sys.stderr.write(msg)
    sys.stderr.write(' See https://github.com/fx2301/curl2min#Troubleshooting\n')
    exit(1)

def minimal_curl_args(curl_args: List[str], verbose: bool = True) -> List[str]:
    log = sys.stderr if verbose else open(os.devnull, 'w')

    # set aside ignored options
    options_required = [
        option
        for option in to_options(curl_args)
        if option.name in IGNORED_OPTIONS
    ]
    options_undecided = [
        option
        for option in to_options(curl_args)
        if option.name not in IGNORED_OPTIONS
    ]
    
    log.write("Testing for identical responses...\n")
    result_initial = execute_options(options_required + options_undecided)
    result = execute_options(options_required + options_undecided)
    if result_initial != result:
        _fail(f"Expected identical responses for identical calls: {result_initial} vs {result}")

    # expand options into finer grained sets of options
    options_undecided = reduce(
        lambda acc, option: acc + option.to_component_options(),
        options_undecided,
        []
    )
    log.write("Testing for identical response after expanding options into finer grained options...\n")
    result = execute_options(options_required + options_undecided)
    if result_initial != result:
        _fail(f"Report this bug! Expected identical responses: {result_initial} vs {result}")

    return curl_args