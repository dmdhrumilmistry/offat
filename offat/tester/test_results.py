from tabulate import tabulate

class TestResultTable:
    def __init__(self, tablefmt:str='heavy_outline', headers:str='keys',*args, **kwargs) -> None:
        self.tablefmt = tablefmt
        self.headers = headers
        self.args = args
        self.kwargs = kwargs

    def generate_result_table(self, results:list, filter_passed_results:bool=True):
        return tabulate(self._sanitize_results(results, filter_passed_results), headers=self.headers, tablefmt=self.tablefmt, *self.args, **self.kwargs)
    
    def _sanitize_results(self, results:list, filter_passed_results:bool=True, is_leaking_data:bool=False):
        if filter_passed_results:
            results = list(filter(lambda x: not x.get('result') or x.get('data_leak'), results))

        # remove args, kwargs and other unrequired keys for results
        for result in results:
            if result['result']:
                result['result'] = u"\u2713"
            else:
                result['result'] = u"\u00d7"

            if not is_leaking_data:
                del result['response_headers']
                del result['response_body']

            if not result.get('data_leak'):
                del result['data_leak']

            del result['url']
            del result['args']
            del result['kwargs']
            del result['test_name']
            del result['response_filter']
            del result['success_codes']
            del result['body_params']
            del result['malicious_payload']
            del result['request_headers']
            del result['redirection']
            
        return results
