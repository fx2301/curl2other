from optparse import OptionGroup, OptionParser
import sys

from transformations.curl2min import minimal_curl_args

parser = OptionParser(usage="usage: %prog [options] curl [curl_options]")

transformations_group = OptionGroup(parser, "Transformations")

transformations_group.add_option(
    "--minimal-curl", "--curl", "--min",
    action="store_true", dest="minimal_curl",
    help="Remove all the curl options that have no effect on the response.")

parser.add_option_group(transformations_group)

try:
    curl_start = sys.argv.index('curl')
except ValueError:
    print("curl statement missing", file=sys.stderr)
    parser.print_help(file=sys.stderr)
    exit(1)

main_args = sys.argv[1:curl_start]
curl_args = sys.argv[curl_start+1:]

(options, remainder_args) = parser.parse_args(args=main_args)

if len(remainder_args) > 0:
    print(f"Unexpected argument(s) before curl statement: {' '.join(remainder_args)}", file=sys.stderr)
    parser.print_help(file=sys.stderr)
    exit(1)

if not(options.minimal_curl):
    print(f"Expected at least one transformation option.", file=sys.stderr)
    parser.print_help(file=sys.stderr)
    exit(1)

if options.minimal_curl:
    curl_args = minimal_curl_args(curl_args)

# TODO quote command for safe usage in bash e.g. -H 'Host: foo'
print(' '.join(['curl']+curl_args))
