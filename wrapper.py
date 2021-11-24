from dataclasses import dataclass
import hashlib
import re
import subprocess
from typing import List

@dataclass
class CurlResult:
    """Result of running a curl command"""
    arguments: List[str]
    status: int
    body_digest: str

    def __str__(self):
        return f"CurlResult(status={self.status}, body_digest={self.body_digest})"

def execute(arguments: List[str]) -> (str, str):
    cmd = ['curl', '-v', '-s'] + arguments
    if '-v' not in cmd:
        cmd.append('-v')
    if '-s' not in cmd:
        cmd.append('-s')
        
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout = proc.stdout.read()
    stderr = proc.stderr.read()

    status_match = re.search(r'^< HTTP/[0-9.]+ ([0-9]+)', stderr.decode('utf-8'), re.MULTILINE)
    if not status_match:
        raise Exception(f"No status found in response for: {' '.join(cmd)}")
    
    # TODO check for location header as well

    status = int(status_match[1])
    body_digest = hashlib.sha256(stdout).hexdigest()

    # print(status, digest)

    return CurlResult(arguments, status, body_digest)
