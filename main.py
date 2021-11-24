from optparse import OptionParser
import sys

from wrapper import execute

parser = OptionParser(usage="usage: %prog [options] curl [curl_options]")

try:
    curl_start = sys.argv.index('curl')
except ValueError:
    print("curl statement missing", file=sys.stderr)
    parser.print_help(file=sys.stderr)
    exit(1)

main_args = sys.argv[1:curl_start]
curl_args = sys.argv[curl_start+1:]

print('main_args', main_args)
print('curl_args', curl_args)

print(execute(curl_args))