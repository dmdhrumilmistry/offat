from .logger import create_logger


logger = create_logger(__name__)


def validate_config_file_data(test_config_data:dict):
    if not isinstance(test_config_data, dict):
        logger.warning('Invalid data format')
        return False
    
    if test_config_data.get('error', False):
        logger.warning(f'Error Occurred While reading file: {test_config_data}')
        return False
    
    if not test_config_data.get('actors', ):
        logger.warning('actors are required')
        return False
    
    if not test_config_data.get('actors', [])[0].get('actor1',None):
        logger.warning('actor1 is required')
        return False
    
    logger.info('User provided data will be used for generating test cases')
    return test_config_data