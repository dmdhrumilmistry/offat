from copy import deepcopy
from .data_exposure import detect_data_exposure
from .fuzzer import fill_params
from .test_runner import TestRunnerFiltersEnum
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
                    'response_filter': TestRunnerFiltersEnum.STATUS_CODE_FILTER
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
        malicious_params = []
        request_params = self.__get_request_params_list(request_params)

        # filter params with string value 
        # TODO: we're missing out required params here, 
        # required param should be considered
        request_params = list(filter(lambda param: param.get('required')==True or param.get('type')=='string', request_params))

        # inject sqli payload as param value
        for request_param_data in request_params:
            if request_param_data.get('type') == 'string':
                new_request = deepcopy(request_param_data)
                new_request['value'] = sqli_payload
                malicious_params.append(new_request)

        return malicious_params
        

    def sqli_fuzz_params_test(
            self,
            openapi_parser:OpenAPIParser,
            success_codes:list[int]=[403,405,500],
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
        base_url:str = openapi_parser.base_url
        request_response_params:dict = openapi_parser.request_response_params

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

        # TODO: handle path params in future
        # NOTE: skip paths containing in path variables and no body params for now!!.
        request_response_params = list(filter(lambda x: len(x.get('path_params',[]))==0 and len(x.get('request_params',[]))>0, request_response_params))

        # inject SQLi payloads in string variables
        for sqli_payload in basic_sqli_payloads:
            for request_obj in request_response_params:
                request_params = request_obj.get('request_params',[])
                request_path = request_obj.get('path',[])

                malicious_request_params = self.__inject_sqli_payload_in_params(request_params, sqli_payload)

                tasks.append({
                    'test_name':'SQLi Test',
                    'url': f'{base_url}{request_path}',
                    'endpoint': request_path,
                    'method': request_obj.get('http_method').upper(),
                    'body_params':malicious_request_params,
                    'malicious_payload':sqli_payload,
                    'args': args,
                    'kwargs': kwargs,
                    'result_details':{
                        True:'Parameters are not vulnerable to SQLi Payload', # passed
                        False:'One or more parameter is vulnerable to SQL Injection Attack', # failed
                    },
                    'success_codes':success_codes,
                    'response_filter': TestRunnerFiltersEnum.STATUS_CODE_FILTER
                })

        return tasks
    

    def bola_path_test(
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

        # get request params list
        # request_params_list = list(map(lambda x: self.__get_request_params_list(x.get('request_params',[])), request_response_params))

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

            for path_param in path_params:
                path_param_name = path_param.get('name')
                path_param_value = path_param.get('value')
                endpoint_path = endpoint_path.replace('{' + str(path_param_name) + '}', str(path_param_value))

            # TODO: handle request query params
            request_query_params = list(filter(lambda x: x.get('in') == 'query', request_params))
            # print(request_query_params)
            # print('-'*30)

            tasks.append({
                'test_name':'BOLA Path Test',
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
                'response_filter': TestRunnerFiltersEnum.STATUS_CODE_FILTER
            })

        return tasks
    

