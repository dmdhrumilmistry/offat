from urllib.parse import urljoin
from .test_runner import TestRunnerFiltersEnum


class TestGenerator:
    '''Class to generate API test checks'''
    def __init__(self,  headers:dict=None) -> None:
        self._headers = headers

    def check_unsupported_http_methods(
            self,
            base_url:str,
            endpoints:list[tuple],
            success_codes:list[int]=[200,301],
            *args,
            **kwargs):
        '''Checks whether endpoint supports undocumented/unsupported HTTP methods'''
        tasks = []

        for endpoint, methods_allowed in endpoints:
            endpoint = urljoin(base_url,endpoint)
            http_methods:set = {'get', 'post', 'put', 'delete', 'options'}
            restricted_methods = http_methods - set(methods_allowed)

            for restricted_method in restricted_methods:
                
                tasks.append({
                    'test_name':'UnSupported HTTP Method Check',
                    'url': endpoint,
                    'method': restricted_method.upper(),
                    'args': args,
                    'kwargs': kwargs,
                    'success_codes':success_codes,
                    'response_filter': TestRunnerFiltersEnum.STATUS_CODE_FILTER
                })

        return tasks