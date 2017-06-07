# -*- coding: utf-8 -*-
from six.moves import http_cookiejar as cookielib
import time
import os
import json
def json_loads(text):
    return json.loads(text)

import requests
from requests import exceptions as excps


from smart_qq_bot.config import (
    SMART_QQ_REFER,
    COOKIE_FILE,
    SSL_VERIFY,
)
from smart_qq_bot.logger import logger


def _get_cookiejar(cookie_file):
    return cookielib.LWPCookieJar(cookie_file)


class HttpClient(object):

    # urllib2.install_opener(_req)

    def __init__(self, load_cookie=False, cookie_file=COOKIE_FILE):
        if not os.path.isdir(os.path.dirname(cookie_file)):
            os.mkdir(os.path.dirname(cookie_file))
        self._cookie_file = cookie_file
        self._cookies = _get_cookiejar(cookie_file)
        if load_cookie:
            self.load_cookie()
        self.session = requests.session()
        self.session.cookies = self._cookies

    @staticmethod
    def _get_headers(headers):
        """
        :type headers: dict
        :rtype: dict
        """
        _headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36",
            'Referer': 'http://s.web2.qq.com/proxy.html?v=20130916001&callback=1&id=1',
        }
        _headers.update(headers)
        return _headers

    def load_cookie(self):
        try:
            self._cookies.load(ignore_discard=True, ignore_expires=True)
        except :
            logger.warn("Failed to load cookie file {0}".format(self._cookie_file))
        finally:
            self._cookies.save(ignore_discard=True, ignore_expires=True)

    @staticmethod
    def get_timestamp():
        return str(int(time.time()*1000))

    def load(self, url, data=None, refer=None, parser=json_loads, validator=None, retries=5):
        while True:
            try:
                if data:
                    logger.debug("POST {} with data {}".format(url, data))
                    resp = self.session.post(
                        url,
                        data,
                        headers=self._get_headers({'Referer': refer or SMART_QQ_REFER}),
                        verify=SSL_VERIFY,
                    )
                else:
                    logger.debug("GET {}".format(url))
                    resp = self.session.get(
                        url,
                        headers=self._get_headers({'Referer': refer or SMART_QQ_REFER}),
                        verify=SSL_VERIFY,
                    )
                self._cookies.save(COOKIE_FILE, ignore_discard=True, ignore_expires=True)
                resp = resp.text
                logger.debug("response: {}".format(resp))

                if parser:
                    resp = parser(resp)
                if validator:
                    validator(resp)
                return resp
            except requests.exceptions.SSLError:
                logger.exception("SSL连接验证失败，请检查您所在的网络环境。如果需要禁用SSL验证，请修改config.py中的SSL_VERIFY为False")
                raise
            except Exception as e:
                logger.exception(e)
                retries -= 1
                if retries == 0:
                    raise

            logger.error("request failed, retrying in 2 seconds")
            time.sleep(2)

    def load_result(self, url, *args, **kwargs):
        validator = kwargs["validator"] if "validator" in kwargs else None
        def result_validator(response):
            assert 'retcode' in response and response['retcode'] == 0 \
                or 'errCode' in response and response['errCode'] == 0 \
                or 'ec' in response and response['ec'] == 0, repr(response)
            assert 'result' in response, repr(response)
            if validator:
                validator(response['result'])
        kwargs["validator"] = result_validator
        response = self.load(url, *args, **kwargs)
        return response['result']

    def get_cookie(self, key):
        for c in self._cookies:
            if c.name == key:
                return c.value
        return ''

    def download(self, url, fname):
        with open(fname, "wb") as o_file:
            try:
                resp = self.session.get(url, stream=True, verify=SSL_VERIFY)
            except requests.exceptions.SSLError:
                logger.exception("SSL连接验证失败，请检查您所在的网络环境。如果需要禁用SSL验证，请修改config.py中的SSL_VERIFY为False")
            except (excps.ConnectTimeout, excps.HTTPError):
                error_msg = "Failed to send request to `{0}`".format(
                    url
                )
                logger.exception(error_msg)
                return error_msg
            else:
                self._cookies.save(COOKIE_FILE, ignore_discard=True, ignore_expires=True)
                o_file.write(resp.raw.read())
