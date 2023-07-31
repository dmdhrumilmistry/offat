from argparse import ArgumentParser
from .openapi import OpenAPIParser
from .tester.tester_utils import generate_and_run_tests
from .utils import get_package_version


def start():
    '''Starts cli tool'''
    parser = ArgumentParser(prog='offat')
    parser.add_argument('-f','--file', dest='fpath', type=str, help='path of openapi/swagger specification file', required=True)
    parser.add_argument('-v','--version', action='version', version=f'%(prog)s {get_package_version()}')
    parser.add_argument('-pr','--path-regex', dest='path_regex_pattern', type=str, help='run tests for paths matching given regex pattern', required=False, default=None)
    args = parser.parse_args()

    # parse and run tests
    api_parser = OpenAPIParser(args.fpath)
    generate_and_run_tests(api_parser, args.path_regex_pattern)

if __name__ == '__main__':
    start()