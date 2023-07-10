from asyncio import run
from .test_generator import TestGenerator
from .test_runner import TestRunner
from .test_results import TestResultTable
from ..logger import create_logger
from ..openapi import OpenAPIParser


logger = create_logger(__name__)

# create tester objs
test_runner = TestRunner()
test_table_generator = TestResultTable()
test_generator = TestGenerator()


def run_test(tests:list[dict]):
    '''Run tests and print result on console'''
    global test_runner, test_table_generator
    test_results = run(test_runner.run_tests(tests))
    results = test_table_generator.generate_result_table(test_results)
    print(results)

 
def generate_and_run_tests(api_parser:OpenAPIParser):
    # test for unsupported http methods
    logger.info('Checking for Unsupported HTTP methods:')
    # unsupported_http_endpoint_tests = test_generator.check_unsupported_http_methods(api_parser.base_url, api_parser._get_endpoints())
    # run_test(unsupported_http_endpoint_tests)

    # sqli fuzz test
    logger.info('Checking for SQLi vulnerability:')
    # sqli_fuzz_tests = test_generator.sqli_fuzz_params(api_parser)
    # run_test(sqli_fuzz_tests)
   
    # BOLA path tests
    logger.info('Checking for BOLA in PATH:')
    bola_path_tests = test_generator.bola_path_test(api_parser, success_codes=[200, 201, 301])
    # run_test(bola_path_tests)