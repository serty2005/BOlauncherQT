import requests

from core.config import get_config_value


def requests_get(config, url, **kwargs):
    with requests_session(config) as session:
        return session.get(url, **kwargs)


def requests_session(config):
    session = requests.Session()
    session.trust_env = get_config_value(config, 'Settings', 'UseProxyEnvironment', default=True, type_cast=bool)
    return session
