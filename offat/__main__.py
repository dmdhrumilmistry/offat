from argparse import ArgumentParser
from asyncio import run
# from pprint import pprint as print
from .openapi import OpenAPIParser
from .tester.test_generator import TestGenerator
from .tester.test_runner import TestRunner
from .tester.test_results import TestResultTable
from .logger import create_logger

logger = create_logger(__name__)

def start():
    '''Starts cli tool'''
    parser = ArgumentParser(prog='offat')
    parser.add_argument('-f','--file', dest='fpath', type=str, help='path of openapi/swagger specification file', required=True)
    
    args = parser.parse_args()

    api_parser = OpenAPIParser(args.fpath)

    # create tester objs
    test_runner = TestRunner()
    test_table_generator = TestResultTable()
    test_generator = TestGenerator()

    
    # test for unsupported http methods
    logger.info('Checking for Unsupported HTTP methods:')
    unsupported_http_endpoint_tests = test_generator.check_unsupported_http_methods(api_parser.base_url, api_parser._get_endpoints())
    test_results = run(test_runner.run_tests(unsupported_http_endpoint_tests))
    results = test_table_generator.generate_result_table(test_results)
    print(results)

    # sqli fuzz test
    logger.info('Checking for SQLi vulnerability:')
    sqli_fuzz_tests = test_generator.sqli_fuzz_params(api_parser)
    test_results = run(test_runner.run_tests(sqli_fuzz_tests))
    results = test_table_generator.generate_result_table(test_results)
    print(results)

    # generate results

if __name__ == '__main__':
    start()