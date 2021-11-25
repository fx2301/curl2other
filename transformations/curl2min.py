import os
import sys
from functools import reduce
from typing import List

from wrapper import execute_options, to_arguments, to_options

PRESERVED_OPTIONS = [
    '-v', '--verbose',
    '-s', '--silent',
    '-X', '--request'
]

def _fail(msg):
    sys.stderr.write('Aborting. ')
    sys.stderr.write(msg)
    sys.stderr.write(' See https://github.com/fx2301/curl2min#Troubleshooting\n')
    exit(1)

def minimal_curl_args(curl_args: List[str], verbose: bool = True) -> List[str]:
    log = sys.stderr if verbose else open(os.devnull, 'w')

    # set aside ignored options
    options_required = []
    options_undecided = []
    for option in to_options(curl_args):
        if option.name.startswith('-') and not option.name in PRESERVED_OPTIONS:
            options_undecided.append(option)
        else:
            options_required.append(option)
    
    log.write("Testing for identical responses...\n")
    result_initial = execute_options(options_required + options_undecided)
    result = execute_options(options_required + options_undecided)
    if result != result_initial:
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

    log.write('Testing with minimum options...\n')
    result = execute_options(options_required)
    if result == result_initial:
        options_undecided = []
    else:
        log.write('Testing with leave one out...\n')
        options_remaining = []
        for i in range(len(options_undecided)):
            result = execute_options(options_required + options_undecided[:i] + options_undecided[i+1:])
            if result == result_initial:
                log.write(f'Not required: {options_undecided[i]}\n')
            else:
                log.write(f'Required: {options_undecided[i]}\n')
                options_remaining.append(options_undecided[i])

        log.write('Verifying leave one out work inferences work in combination...\n')
        result = execute_options(options_required + options_remaining)
        if result != result_initial:
            _fail('Leave one out assumption for headers failed! A cause of this could be expired cookies.')
        
        options_undecided = options_remaining

    return to_arguments(options_required + options_undecided)