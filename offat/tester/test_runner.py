from asyncio import ensure_future, gather
from enum import Enum
from ..http import AsyncRequests, AsyncRLRequests
from ..logger import create_logger

logger = create_logger(__name__)


class TestRunnerFiltersEnum(Enum):
    STATUS_CODE_FILTER = 0
    # reserved for future use


class TestRunner:
    def __init__(self, rate_limit:int=None, delay:float=None, headers:dict=None) -> None:
        if rate_limit and delay:
            self._client = AsyncRLRequests(rate_limit=rate_limit, delay=delay, headers=headers)
        else:
            self._client = AsyncRequests(headers=headers)


    async def status_code_filter_request(self, test_task):
        url = test_task.get('url')
        http_method = test_task.get('method')
        success_codes = test_task.get('success_codes', [200, 301])
        args = test_task.get('args')
        kwargs = test_task.get('kwargs')

        try:
            response = await self._client.request(url=url, method=http_method, *args, **kwargs)
        except ConnectionRefusedError:
            logger.error('Connection Failed! Server refused Connection!!')

        test_result = test_task
        if isinstance(response, dict) and response.get('status') in success_codes:
            test_result['result'] = False
            test_result['result_detail'] = 'Endpoint performs HTTP method which is not documented'

        return test_result


    async def run_tests(self, test_tasks:list):
        '''run tests generated from test generator module'''
        tasks = []

        for test_task in test_tasks:
            match test_task.get('response_filter', None):
                case _: # default filter 
                    task_filter = self.status_code_filter_request

            tasks.append(
                ensure_future(
                    task_filter(test_task)
                )
            )

        return await gather(*tasks)