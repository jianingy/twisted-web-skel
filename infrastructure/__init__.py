from yaml import load as yaml_load
from twisted.python import log as twisted_log
import codecs
import logging

__all__ = ["configure", "get_value", "build_server",
           "debug", "log", "error", "fatal"]

__config__ = dict()
__config_cache__ = dict()


def configure(filename):
    """

    Arguments:
    - `filename`:
    """

    global __config__

    with codecs.open(filename, "r", encoding="utf-8") as f:
        __config__ = yaml_load(f.read())


def get_value(key, default=None):
    if key in __config_cache__:
        return __config_cache__[key]

    item = __config__
    for subkey in key.strip("/").split("/"):
        if subkey not in item:
            return default
        item = item[subkey]

    __config_cache__[key] = item

    return item


def build_server(site_root):

    server_port = get_value("/server/port", 8080)

    from twisted.web import server as web_server
    site = web_server.Site(site_root)

    from twisted.application.internet import TCPServer as tcp_server
    server = tcp_server(server_port, site)

    return server


def debug(message):
    twisted_log.msg(message, level=logging.DEBUG)


def log(message):
    twisted_log.msg(message, level=logging.INFO)


def warn(message):
    twisted_log.msg(message, level=logging.WARNING)


def error(message):
    twisted_log.msg(message, level=logging.ERROR)


def fatal(message):
    twisted_log.msg(message, level=logging.CRITICAL)
    from twisted import reactor
    reactor.stop()
