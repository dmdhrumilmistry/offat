from prance import ResolvingParser
from .logger import create_logger


logger = create_logger(__name__)


class OpenAPIParser:
    ''''''
    def __init__(self, fpath:str) -> None:
        self._parser = ResolvingParser(fpath, backend = 'openapi-spec-validator')
        if self._parser.valid:
            logger.info('Specification file is valid')
        else:
            logger.error('Specification file is invalid!')

        self._spec = self._parser.specification
        self.base_url = f"http://{self._spec.get('host')}{self._spec.get('basePath','')}"


    def _get_endpoints(self):
        '''Returns list of endpoint paths along with HTTP methods allowed'''
        endpoints = []

        for endpoint in self._spec.get('paths', {}).keys():
            methods = list(self._spec['paths'][endpoint].keys())
            methods.remove('parameters')
            endpoints.append((endpoint, methods))

        return endpoints

    

