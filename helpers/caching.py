import logging
from django.core.cache import cache

logger = logging.getLogger('django')

def set_cache(key: str, value: str, ttl: int) -> bool:
    try:
        cache.set(key, value, timeout=ttl)
        logger.info(f'Successfully set cache: {key} = {value}')
    except Exception as err:
        logger.error(f'Cannot set cache data: {err}')
        return False
    return True

def get_cache(key: str) -> str:
    try:
        value = cache.get(key)
        if value is None:
            logger.warning(f'Cache miss for key: {key}')
        else:
            logger.info(f'Successfully retrieved cache: {key} = {value}')
        return value
    except Exception as err:
        logger.error(f'Cannot get cache data: {err}')
        return None

def delete_cache(key: str) -> bool:
    try:
        cache.delete(key)
        logger.info(f'Successfully deleted cache: {key}')
    except Exception as err:
        logger.error(f'Cannot delete cache data: {err}')
        return False
    return True
