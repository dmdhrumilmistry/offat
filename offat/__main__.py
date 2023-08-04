from argparse import ArgumentParser
from .openapi import OpenAPIParser
from .tester.tester_utils import generate_and_run_tests
from .utils import get_package_version, headers_list_to_dict


def start():
    '''Starts cli tool'''
    parser = ArgumentParser(prog='offat')
    parser.add_argument('-f','--file', dest='fpath', type=str, help='path of openapi/swagger specification file', required=True)
    parser.add_argument('-v','--version', action='version', version=f'%(prog)s {get_package_version()}')
    parser.add_argument('-rl', '--rate-limit', dest='rate_limit', help='API requests rate limit. -dr should be passed in order to use this option', type=int, default=None, required=False)
    parser.add_argument('-dr', '--delay-rate', dest='delay_rate', help='API requests delay rate in seconds. -rl should be passed in order to use this option', type=float, default=None, required=False)
    parser.add_argument('-pr','--path-regex', dest='path_regex_pattern', type=str, help='run tests for paths matching given regex pattern', required=False, default=None)
    parser.add_argument('-o', '--output', dest='output_file', type=str, help='path to store test results in json format', required=False, default=None)
    parser.add_argument('-H', '--headers', dest='headers', type=str, help='HTTP requests headers that should be sent during testing eg: User-Agent: offat,Authorization: Bearer yourToken', required=False, default=None, action='append', nargs='*')
    args = parser.parse_args()


    # convert req headers str to dict
    headers_dict:dict = headers_list_to_dict(args.headers)

    # handle rate limiting options
    rate_limit = args.rate_limit
    delay_rate = args.delay_rate

    # if any is not set, then set both to None
    if (rate_limit and not delay_rate) or (not rate_limit and delay_rate):
        rate_limit = None
        delay_rate = None

    # parse args and run tests
    api_parser = OpenAPIParser(args.fpath)
    generate_and_run_tests(
        api_parser=api_parser,
        regex_pattern=args.path_regex_pattern,
        output_file=args.output_file,
        req_headers=headers_dict,
        rate_limit=rate_limit,
        delay=delay_rate,
    )

if __name__ == '__main__':
    start()