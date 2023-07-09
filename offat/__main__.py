from argparse import ArgumentParser
from .openapi import OpenAPIParser
from .tester.tester_utils import generate_and_run_tests


def start():
    '''Starts cli tool'''
    parser = ArgumentParser(prog='offat')
    parser.add_argument('-f','--file', dest='fpath', type=str, help='path of openapi/swagger specification file', required=True)
    args = parser.parse_args()

    # parse and run tests
    api_parser = OpenAPIParser(args.fpath)
    generate_and_run_tests(api_parser)

if __name__ == '__main__':
    start()