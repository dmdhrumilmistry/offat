from tabulate import tabulate

class TestResultTable:
    def __init__(self, tablefmt:str='heavy_outline', headers:str='keys',*args, **kwargs) -> None:
        self.tablefmt = tablefmt
        self.headers = headers
        self.args = args
        self.kwargs = kwargs

    def generate_result_table(self, results:list):
        return tabulate(self._sanitize_results(results), headers=self.headers, tablefmt=self.tablefmt, *self.args, **self.kwargs)
    
    def _sanitize_results(self, results:list, filter_passed_results:bool=True):
        # remove args, kwargs and url keys
        for result in results:
            del result['url']
            del result['args']
            del result['kwargs']
            del result['test_name']
            del result['response_filter']

        if filter_passed_results:
            results = filter(lambda x: not x.get('result'), results)

        return results
        