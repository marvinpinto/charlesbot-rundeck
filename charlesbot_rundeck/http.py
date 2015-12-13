import asyncio
import aiohttp
import logging
log = logging.getLogger(__name__)

@asyncio.coroutine
def http_post_request(url, headers):
    response = yield from aiohttp.post(url, headers=headers)
    if not response.status == 200:
        text = yield from response.text()
        log.error("URL: %s" % url)
        log.error("Response status code was %s" % str(response.status))
        log.error(response.headers)
        log.error(text)
        response.close()
        return ""
    return (yield from response.text())

@asyncio.coroutine
def http_get_request(url, headers, params={}):
    response = yield from aiohttp.get(url, headers=headers, params=params)
    if not response.status == 200:
        text = yield from response.text()
        log.error("URL: %s" % url)
        log.error("Response status code was %s" % str(response.status))
        log.error(response.headers)
        log.error(text)
        response.close()
        return ""
    return (yield from response.text())
