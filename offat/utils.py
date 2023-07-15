from json import loads as json_load, JSONDecodeError
from os.path import isfile
from yaml import safe_load, YAMLError
from pkg_resources import get_distribution


def get_package_version():
    '''Returns package current version
    
    Args:
        None

    Returns:
        String: current package version
    '''
    return get_distribution('offat').version    


def read_yaml(file_path:str) -> dict:
    '''Reads YAML file and returns as python dict. 
    returns file not found or yaml errors as dict.

    Args:
        file_path (str): path of yaml file

    Returns:
        dict: YAML contents as dict else returns error 
    '''
    if not isfile(file_path):
        return {"error":"File Not Found"}
    
    with open(file_path) as f:
        try:
            return safe_load(f.read())
        except YAMLError:
            return {"error": "YAML error"}
        

def read_json(file_path:str) -> dict:
    '''Reads JSON file and returns as python dict. 
    returns file not found or JSON errors as dict.

    Args:
        file_path (str): path of yaml file

    Returns:
        dict: YAML contents as dict else returns error 
    '''
    if not isfile(file_path):
        return {"error":"File Not Found"}
    
    with open(file_path) as f:
        try:
            return json_load(f.read())
        except JSONDecodeError:
            return {"error": "JSON error"}
        

def read_openapi_file(file_path:str) -> dict:
    '''Returns Open API Documentation file contents as json
    returns file not found or yaml errors as dict.

    Args:
        file_path (str): path of openapi file

    Returns:
        dict: YAML contents as dict else returns error 
    '''
    if not isfile(file_path):
        return {"error":"File Not Found"}
    
    file_ext = file_path.split('.')[-1]
    match file_ext:
        case 'json':
            return read_json(file_path)
        case 'yaml':
            return read_yaml(file_path)
        case _:
            return {"error":"Invalid file extension"}
