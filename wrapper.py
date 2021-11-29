from dataclasses import dataclass
import hashlib
import json
import re
import shlex
import sys
import subprocess
from typing import Dict, List, Optional
from functools import reduce

@dataclass
class CurlResult:
    """Result of running a curl command"""
    arguments: List[str]
    status: int
    body_digest: str

    def __eq__(self, other: 'CurlResult') -> bool:
        return self.status == other.status and self.body_digest == other.body_digest

    def __str__(self):
        return f"CurlResult(status={self.status}, body_digest={self.body_digest})"

def execute(arguments: List[str]) -> CurlResult:
    cmd = ['curl', '-v', '-s'] + arguments
    if '-v' not in cmd:
        cmd.append('-v')
    if '-s' not in cmd:
        cmd.append('-s')
        
    # print(f"Running: {shlex.join(cmd)}")
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout = proc.stdout.read().decode('utf-8')
    stderr = proc.stderr.read().decode('utf-8')

    if '* SSL certificate problem: self signed certificate' in stderr:
        print("Server SSL certificate is self-signed. Add --insecure curl argument if it's safe to continue.", file=sys.stderr)
        exit(1)

    status_match = re.search(r'^< HTTP/[0-9.]+ ([0-9]+)', stderr, re.MULTILINE)
    if not status_match:
        raise Exception(f"No status found in response for: {shlex.join(cmd)}")
    
    # TODO check for location header as well

    status = int(status_match[1])
    body_digest = hashlib.sha256(stdout).hexdigest()

    result = CurlResult(arguments, status, body_digest)

    # print('-->', status, body_digest)

    return result

# TODO memoize this?
def _option_definitions() -> Dict[str, dict]:
    with open('curl_options.json', 'r') as f:
        options = json.load(f)
        option_definitions = {}
        for option in options:
            option_definitions[option['option']] = option
            if option['alias'] is not None:
                option_definitions[option['alias']] = option
    
    return option_definitions

@dataclass
class CurlOption:
    """Semantic option for curl command-line"""
    name: str
    argument: Optional[str] = None

    def to_arguments(self):
        if self.argument is None:
            return [self.name]
        else:
            return [self.name, self.argument]

    def to_component_options(self):
        """Split option into component, stand-alone options"""
        if self.name in ['-H', "--header"]:
            m = re.match(r'^Cookie: (.*)$', self.argument)
            if m:
                return [
                    CurlOption(self.name, f'Cookie: {value}')
                    for value in m[1].split('; ')
                ]

        return [self]

    def __str__(self):
        return shlex.join(self.to_arguments())

def to_options(arguments: List[str]) -> List[CurlOption]:
    option_definitions = _option_definitions()

    options = []
    i = 0
    while i < len(arguments):
        option_name = arguments[i]
        i += 1

        if option_name not in option_definitions:
            if option_name.startswith("-"):
                print(f"WARNING: unrecognized curl option: {option_name}")
            options.append(CurlOption(name=option_name))
        else:
            if option_definitions[option_name]['argument'] is None:
                options.append(CurlOption(name=option_name))
            else:
                if i < len(arguments):
                    options.append(CurlOption(name=option_name, argument=arguments[i]))
                    i += 1
                else:
                    raise Exception(f"Missing argument for curl option {option_name}")

    return options

def to_arguments(options: List[CurlOption]) -> List[CurlOption]:
    return reduce(lambda acc, option: acc + option.to_arguments(), options, [])

def execute_options(options: List[CurlOption]) -> CurlResult:
    arguments = to_arguments(options)

    return execute(arguments)

