import openmeteo_requests
import requests_cache
from retry_requests import retry

def get_client(cache_path: str = ".cache", expire_after: int = 3600):
    cache = requests_cache.CachedSession(cache_path, expire_after=expire_after)
    retry_session = retry(cache, retries=5, backoff_factor=0.2)
    return openmeteo_requests.Client(session=retry_session)