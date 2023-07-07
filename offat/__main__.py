from argparse import ArgumentParser
from asyncio import run
from pprint import pprint as print
from .openapi import OpenAPIParser
from .tester.test_generator import TestGenerator
from .tester.test_runner import TestRunner
from .tester.test_results import TestResultTable


def start():
    '''Starts cli tool'''
    parser = ArgumentParser(prog='offat')
    parser.add_argument('-f','--file', dest='fpath', type=str, help='path of openapi/swagger specification file', required=True)
    
    args = parser.parse_args()

    api_parser = OpenAPIParser(args.fpath)

    # create test objs
    test_runner = TestRunner()
    test_table_generator = TestResultTable()

    # test for unsupported http methods
    test_generator = TestGenerator()
    # unsupported_http_endpoint_tests = test_generator.check_unsupported_http_methods(api_parser.base_url, api_parser._get_endpoints())


    # for sqli test
    request_respone_params = api_parser._get_request_response_params()
    print(request_respone_params)
    # test_generator.sqli_fuzz_params(api_parser.base_url, request_respone_params)

    # run tests
    # test_results = run(test_runner.run_tests(unsupported_http_endpoint_tests))

    # generate results
    # results = test_table_generator.generate_result_table(test_results)
    # print(results)

if __name__ == '__main__':
    start()