from tabulate import tabulate

class TestResultTable:
    def __init__(self, tablefmt:str='heavy_outline', headers:str='keys',*args, **kwargs) -> None:
        self.tablefmt = tablefmt
        self.headers = headers
        self.args = args
        self.kwargs = kwargs

    def generate_result_table(self, results:list, filter_passed_results:bool=True):
        return tabulate(self._sanitize_results(results, filter_passed_results), headers=self.headers, tablefmt=self.tablefmt, *self.args, **self.kwargs)
    
    def _sanitize_results(self, results:list, filter_passed_results:bool=True):
        if filter_passed_results:
            results = list(filter(lambda x: not x.get('result'), results))

        # remove args, kwargs and other unrequired keys for results
        for result in results:
            if result['result']:
                result['result'] = u"\u2713"
            else:
                result['result'] = u"\u00d7"

            del result['url']
            del result['args']
            del result['kwargs']
            del result['test_name']
            del result['response_filter']
            del result['success_codes']
            del result['body_params']
            
        return results
