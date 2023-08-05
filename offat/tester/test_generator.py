from copy import deepcopy
from pprint import pprint
from .fuzzer import fill_params
from .test_runner import TestRunnerFiltersEnum
from .fuzzer import generate_random_int
from ..openapi import OpenAPIParser


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
                    'malicious_payload':[],
                    'args': args,
                    'kwargs': kwargs,
                    'result_details':{
                        True: 'Endpoint does not perform any HTTP method which is not documented', # passed
                        False: 'Endpoint performs HTTP method which is not documented', # failed
                    },
                    'body_params':[],
                    'success_codes':success_codes,
                    'response_filter': TestRunnerFiltersEnum.STATUS_CODE_FILTER.name
                })

        return tasks
    

    def __get_request_params_list(self, request_params:list[dict]):
        '''Get list of request parameters
        '''
        payload_data  = []
        for request_param in request_params:
            param_pos = request_param.get('in')
            param_schema = request_param.get('schema')

            if param_schema:
                props:dict = param_schema.get('properties',{})
                required_params:list = param_schema.get('required',[])

                for prop in props.keys():
                    # TODO: handle arrays differently to
                    # extract their internal params
                    prop_type = props[prop].get('type')
                    payload_data.append({
                        'in':param_pos,
                        'name':prop,
                        'type':prop_type,
                        'required': prop in required_params,
                    })

        return payload_data
    
    def __fuzz_request_params(self, openapi_parser:OpenAPIParser) -> list[dict]:
        """
        Fuzzes Request params available in different positions and returns a list
        of tasks

        Args:
            openapi_parser (OpenAPIParser): An instance of the OpenAPIParser class
            containing the parsed OpenAPI specification.

        Returns:
            list: returns list of dict (tasks) for API testing with fuzzed request params
        """
        base_url:str = openapi_parser.base_url
        request_response_params:list[dict] = openapi_parser.request_response_params

        tasks = []
        for path_obj in request_response_params:
            # handle path params from request_params
            request_params = path_obj.get('request_params',[])
            request_params = fill_params(request_params)

            # get params based on their position in request
            request_body_params = list(filter(lambda x: x.get('in') == 'body', request_params))
            request_query_params = list(filter(lambda x: x.get('in') == 'query', request_params))
            path_params_in_body = list(filter(lambda x: x.get('in') == 'path', request_params))
            

            # handle path params from path_params
            # and replace path params by value in 
            # endpoint path
            endpoint_path:str = path_obj.get('path')
            path_params = path_obj.get('path_params',[])
            path_params += path_params_in_body
            path_params = fill_params(path_params)
            # print(path_params)
            # print('-'*30)


            for path_param in path_params:
                path_param_name = path_param.get('name')
                path_param_value = path_param.get('value')
                endpoint_path = endpoint_path.replace('{' + str(path_param_name) + '}', str(path_param_value))


            tasks.append({
                'test_name':'BOLA Path Test with Fuzzed Params',
                'url': f'{base_url}{endpoint_path}',
                'endpoint': path_obj.get('path'),
                'method': path_obj.get('http_method').upper(),
                'body_params':request_body_params,
                'query_params':request_query_params,
                # 'malicious_payload':path_params,
                
            })

        return tasks
    

    def __inject_sqli_payload_in_params(self, request_params:list[dict], sqli_payload:str):
        """
        Injects SQL injection (SQLi) payload into the request parameters.

        This method modifies the provided request parameters by injecting the SQLi payload.

        Args:
            request_params (list[dict]): A list of dictionaries representing the request parameters.
            sqli_payload (str): The SQL injection payload to be injected into the request parameters.

        Returns:
            list: returns list of sqli injection parameters for API testing
        """
        request_params = deepcopy(request_params)
    
        # inject sqli payload as param value
        for request_param_data in request_params:
            # TODO: inject sqli payloads in other data types as well
            if request_param_data.get('type') == 'string':
                request_param_data['value'] = sqli_payload

        return request_params
        

    def sqli_fuzz_params_test(
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
            List: List of dictionaries containing tests for SQLi
        
        Raises:
            Any exceptions raised during the execution.
        '''

        # APPROACH: first send sqli in all params, if error is generated
        # then enumerate one by one or ask user to pentest manually using
        # sqlmap
        tasks = []
        basic_sqli_payloads = [
            "' OR 1=1 ;--",
            "' UNION SELECT 1,2,3 -- -",
            "' OR '1'='1--",
            "' AND (SELECT * FROM (SELECT(SLEEP(5)))abc)",
            "' AND SLEEP(5) --",
        ]

        fuzzed_request_list = self.__fuzz_request_params(openapi_parser)

        # inject SQLi payloads in string variables
        for sqli_payload in basic_sqli_payloads:
            for request_obj in fuzzed_request_list:
                # handle body request params
                body_request_params = request_obj.get('body_params',[])
                malicious_body_request_params = self.__inject_sqli_payload_in_params(body_request_params, sqli_payload)

                # handle query request params
                query_request_params = request_obj.get('query_params',[])
                malicious_query_request_params = self.__inject_sqli_payload_in_params(query_request_params, sqli_payload)

                request_obj['test_name'] = 'SQLi Test'
                
                request_obj['body_params'] = malicious_body_request_params
                request_obj['query_params'] = malicious_query_request_params
                request_obj['args'] = args
                request_obj['kwargs'] = kwargs
                
                request_obj['malicious_payload'] = sqli_payload
                
                request_obj['result_details'] = {
                    True:'Parameters are not vulnerable to SQLi Payload', # passed
                    False:'One or more parameter is vulnerable to SQL Injection Attack', # failed
                }
                request_obj['success_codes'] = success_codes
                request_obj['response_filter'] = TestRunnerFiltersEnum.STATUS_CODE_FILTER.name
                tasks.append(deepcopy(request_obj))

        return tasks
    

    def bola_fuzz_path_test(
            self,
            openapi_parser:OpenAPIParser,
            success_codes:list[int]=[200, 201, 301],
            *args,
            **kwargs
    ):
        '''Generate Tests for BOLA in endpoint path
        
        Args:
            openapi_parser (OpenAPIParser): An instance of the OpenAPIParser class containing the parsed OpenAPI specification.
            success_codes (list[int], optional): A list of HTTP success codes to consider as successful BOLA responses. Defaults to [200, 201, 301].
            *args: Variable-length positional arguments.
            **kwargs: Arbitrary keyword arguments.
        
        Returns:
            list[dict]: list of dict containing test case for endpoint
        
        Raises:
            Any exceptions raised during the execution.
        '''
        base_url:str = openapi_parser.base_url
        request_response_params:list[dict] = openapi_parser.request_response_params

        # filter path containing params in path
        endpoints_with_param_in_path = list(filter(lambda path_obj: '/{' in path_obj.get('path'), request_response_params))

        tasks = []
        for path_obj in endpoints_with_param_in_path:
            # handle path params from request_params
            request_params = path_obj.get('request_params',[])
            request_params = fill_params(request_params)

            # get request body params
            request_body_params = list(filter(lambda x: x.get('in') == 'body', request_params))
            

            # handle path params from path_params
            # and replace path params by value in 
            # endpoint path
            endpoint_path:str = path_obj.get('path')

            path_params = path_obj.get('path_params',[])
            path_params_in_body = list(filter(lambda x: x.get('in') == 'path', request_params))
            path_params += path_params_in_body
            path_params = fill_params(path_params)
            # print(path_params)
            # print('-'*30)

            for path_param in path_params:
                path_param_name = path_param.get('name')
                path_param_value = path_param.get('value')
                endpoint_path = endpoint_path.replace('{' + str(path_param_name) + '}', str(path_param_value))

            # TODO: handle request query params
            request_query_params = list(filter(lambda x: x.get('in') == 'query', request_params))
            # print(request_query_params)
            # print('-'*30)

            tasks.append({
                'test_name':'BOLA Path Test with Fuzzed Params',
                'url': f'{base_url}{endpoint_path}',
                'endpoint': path_obj.get('path'),
                'method': path_obj.get('http_method').upper(),
                'body_params':request_body_params,
                'query_params':request_query_params,
                'malicious_payload':path_params,
                'args': args,
                'kwargs': kwargs,
                'result_details':{
                    True:'Endpoint is not vulnerable to BOLA', # passed
                    False:'Endpoint might be vulnerable to BOLA', # failed
                },
                'success_codes':success_codes,
                'response_filter': TestRunnerFiltersEnum.STATUS_CODE_FILTER.name
            })

        return tasks
    

    def bola_fuzz_trailing_slash_path_test(
            self,
            openapi_parser:OpenAPIParser,
            success_codes:list[int]=[200, 201, 301],
            *args,
            **kwargs
    ):
        '''Generate Tests for BOLA in endpoint path
        
        Args:
            openapi_parser (OpenAPIParser): An instance of the OpenAPIParser class containing the parsed OpenAPI specification.
            success_codes (list[int], optional): A list of HTTP success codes to consider as successful BOLA responses. Defaults to [200, 201, 301].
            *args: Variable-length positional arguments.
            **kwargs: Arbitrary keyword arguments.
        
        Returns:
            list[dict]: list of dict containing test case for endpoint
        
        Raises:
            Any exceptions raised during the execution.
        '''
        base_url:str = openapi_parser.base_url
        request_response_params:list[dict] = openapi_parser.request_response_params

        tasks = []
        for path_obj in request_response_params:
            # handle path params from request_params
            request_params = path_obj.get('request_params',[])
            request_params = fill_params(request_params)

            # get params based on their position in request
            request_body_params = list(filter(lambda x: x.get('in') == 'body', request_params))
            request_query_params = list(filter(lambda x: x.get('in') == 'query', request_params))
            path_params_in_body = list(filter(lambda x: x.get('in') == 'path', request_params))
            

            # handle path params from path_params
            # and replace path params by value in 
            # endpoint path
            endpoint_path:str = path_obj.get('path')
            path_params = path_obj.get('path_params',[])
            path_params += path_params_in_body
            path_params = fill_params(path_params)
            # print(path_params)
            # print('-'*30)


            for path_param in path_params:
                path_param_name = path_param.get('name')
                path_param_value = path_param.get('value')
                endpoint_path = endpoint_path.replace('{' + str(path_param_name) + '}', str(path_param_value))

            # generate URL for BOLA attack
            url = f'{base_url}{endpoint_path}'
            if url.endswith('/'):
                url = f'{url}{generate_random_int()}'
            else:
                url = f'{url}/{generate_random_int()}'
            

            tasks.append({
                'test_name':'BOLA Path Trailing Slash Test',
                'url': url,
                'endpoint': path_obj.get('path'),
                'method': path_obj.get('http_method').upper(),
                'body_params':request_body_params,
                'query_params':request_query_params,
                'path_params':path_params,
                'args': args,
                'kwargs': kwargs,
                'result_details':{
                    True:'Endpoint might not vulnerable to BOLA', # passed
                    False:'Endpoint might be vulnerable to BOLA', # failed
                },
                'success_codes':success_codes,
                'response_filter': TestRunnerFiltersEnum.STATUS_CODE_FILTER.name
            })

        return tasks