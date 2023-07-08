from .test_runner import TestRunnerFiltersEnum
from ..openapi import OpenAPIParser
from pprint import pprint as print


class TestGenerator:
    """
    Class to generate API test checks.

    This class provides methods to generate API test checks for various scenarios.

    Attributes:
        None

    Methods:
        check_unsupported_http_methods: Checks whether endpoint supports undocumented/unsupported HTTP methods.
        sqli_fuzz_params: Performs SQL injection (SQLi) parameter fuzzing based on the provided OpenAPIParser instance.
    
    # Examples:
    #     generator = TestGenerator()
    #     check1 = generator.generate_check1()
    #     check2 = generator.generate_check2()
        
    """
    def __init__(self,  headers:dict=None) -> None:
        """
        Initializes an instance of the TestGenerator class.

        Args:
            headers (dict, optional): A dictionary of headers to be set for the instance. Defaults to None.

        Returns:
            None

        Example:
            headers = {"Content-Type": "application/json", "Authorization": "Bearer xyz123"}
            tester = TestGenerator(headers)
        """
        self._headers = headers


    def check_unsupported_http_methods(
            self,
            base_url:str,
            endpoints:list[tuple],
            success_codes:list[int]=[200,301],
            *args,
            **kwargs    
        ):
        '''Checks whether endpoint supports undocumented/unsupported HTTP methods
        
        Args:
            base_url (str): The base URL to check for unsupported HTTP methods.
            endpoints (list[tuple]): A list of tuples representing the endpoints to check. Each tuple should contain the endpoint path and the corresponding supported HTTP methods.
            success_codes (list[int], optional): A list of HTTP success codes to consider as successful responses. Defaults to [200, 301].
            *args: Variable-length positional arguments.
            **kwargs: Arbitrary keyword arguments.
    
        Returns:
            None
        
        Raises:
            Any exceptions raised during the execution.
        '''
        tasks = []

        for endpoint, methods_allowed in endpoints:
            http_methods:set = {'get', 'post', 'put', 'delete', 'options'}
            restricted_methods = http_methods - set(methods_allowed)

            for restricted_method in restricted_methods:
                
                tasks.append({
                    'test_name':'UnSupported HTTP Method Check',
                    'url': f'{base_url}{endpoint}',
                    'endpoint': endpoint,
                    'method': restricted_method.upper(),
                    'args': args,
                    'kwargs': kwargs,
                    'success_codes':success_codes,
                    'response_filter': TestRunnerFiltersEnum.STATUS_CODE_FILTER
                })

        return tasks
    

    def sqli_fuzz_params(
            self,
            openapi_parser:OpenAPIParser,
            success_codes:list[int]=[500],
            *args,
            **kwargs
    ):
        '''Performs SQL injection (SQLi) parameter fuzzing based on the provided OpenAPIParser instance.
    
        Args:
            openapi_parser (OpenAPIParser): An instance of the OpenAPIParser class containing the parsed OpenAPI specification.
            success_codes (list[int], optional): A list of HTTP success codes to consider as successful SQLi responses. Defaults to [500].
            *args: Variable-length positional arguments.
            **kwargs: Arbitrary keyword arguments.
        
        Returns:
            None
        
        Raises:
            Any exceptions raised during the execution.
        '''
        base_url:str = openapi_parser.base_url
        request_response_params:dict = openapi_parser.request_response_params
        basic_sqli_payloads = [
            "' OR 1=1 --",
            "' UNION SELECT 1,2,3 -- -",
            "' OR '1'='1",
            "' AND (SELECT * FROM (SELECT(SLEEP(5)))abc)",
            "' AND SLEEP(5) --",
        ]

        # APPROACH: first send sqli in all params, if error is generated
        # then enumerate one by one or ask user to pentest manually using
        # sqlmap
        tasks = []

        # TODO: handle path params in future
        # NOTE: skip paths containing in path variables and no body params for now!!.
        request_response_params = list(filter(lambda x: len(x.get('path_params',[]))==0 and len(x.get('request_params',[]))>0, request_response_params))
        print(request_response_params)


        # for 

        # tasks.append({
        #     'test_name':'UnSupported HTTP Method Check',
        #     'url': f'{base_url}{endpoint}',
        #     'endpoint': endpoint,
        #     'method': restricted_method.upper(),
        #     'args': args,
        #     'kwargs': kwargs,
        #     'success_codes':success_codes,
        #     'response_filter': TestRunnerFiltersEnum.STATUS_CODE_FILTER
        # })



        return tasks