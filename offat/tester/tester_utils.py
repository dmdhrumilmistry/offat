from asyncio import run
from copy import deepcopy
from re import search as regex_search
from .test_generator import TestGenerator
from .test_runner import TestRunner
from .test_results import TestResultTable
from ..logger import create_logger
from ..openapi import OpenAPIParser
from ..utils import write_json_to_file


logger = create_logger(__name__)

# create tester objs
test_runner = TestRunner()
test_table_generator = TestResultTable()
test_generator = TestGenerator()


def run_test(tests:list[dict], regex_pattern:str=None) -> list:
    '''Run tests and print result on console'''
    global test_runner, test_table_generator

    # filter data if regex is passed
    if regex_pattern:
        tests = list(
            filter(
                lambda x: regex_search(regex_pattern, x.get('endpoint','')),
                tests 
            ) 
        )

    test_results = run(test_runner.run_tests(tests))
    results = test_table_generator.generate_result_table(deepcopy(test_results))
    print(results)
    return test_results

 
def generate_and_run_tests(api_parser:OpenAPIParser, regex_pattern:str=None, output_file:str=None):
    global test_runner, test_table_generator, logger

    results:list = []

    # test for unsupported http methods
    logger.info('Checking for Unsupported HTTP methods:')
    unsupported_http_endpoint_tests = test_generator.check_unsupported_http_methods(api_parser.base_url, api_parser._get_endpoints())
    results += run_test(tests=unsupported_http_endpoint_tests, regex_pattern=regex_pattern)

    # sqli fuzz test
    logger.info('Checking for SQLi vulnerability:')
    sqli_fuzz_tests = test_generator.sqli_fuzz_params_test(api_parser)
    results += run_test(tests=sqli_fuzz_tests, regex_pattern=regex_pattern)
   
    # BOLA path tests
    logger.info('Checking for BOLA in PATH:')
    bola_path_tests = test_generator.bola_path_test(api_parser, success_codes=[200, 201, 301])
    results += run_test(tests=bola_path_tests, regex_pattern=regex_pattern)

    if output_file:
        write_json_to_file(
            json_data={
                'results':results
            }, 
            file_path=output_file
        )
