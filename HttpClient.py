import cookielib, urllib, urllib2, socket, time, os, logging


class HttpClient:
    __cookie = cookielib.LWPCookieJar('cookie/cookie.data')
    # replace line 9 with line 7 and 8 will enable the request report of urllib
    # logprint=urllib2.HTTPHandler(debuglevel=1)
    # __req = urllib2.build_opener(urllib2.HTTPCookieProcessor(__cookie),logprint)
    __req = urllib2.build_opener(urllib2.HTTPCookieProcessor(__cookie))
    __req.addheaders = [
        ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'),
        ('User-Agent',
         "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36"),
        ('Referer', 'http://s.web2.qq.com/proxy.html?v=20130916001&callback=1&id=1')
    ]
    urllib2.install_opener(__req)

    def __init__(self):
        if not os.path.isdir("./cookie"):
            os.mkdir("./cookie")
        try:
            self.__cookie.load(ignore_discard=True,ignore_expires=True)
        except Exception:
            self.__cookie.save(ignore_discard=True,ignore_expires=True)

    def getTimeStamp(self):
        return str(int(time.time()*1000))

    def Get(self, url, refer=None):
        try:
            req = urllib2.Request(url)
            if refer is None:
                req.add_header('Referer', 'http://s.web2.qq.com/proxy.html?v=20130916001&callback=1&id=1')
            else:
                req.add_header('Referer', refer)
            tmp_req = urllib2.urlopen(req)
            self.__cookie.save('cookie/cookie.data',ignore_discard=True,ignore_expires=True)
            return tmp_req.read()
        except urllib2.HTTPError, e:
            return e.read()

    def Post(self, url, data, refer=None):
        try:
            req = urllib2.Request(url, urllib.urlencode(data))
            if refer is None:
                req.add_header('Referer', 'http://d1.web2.qq.com/proxy.html?v=20151105001&callback=1&id=2')
            else:
                req.add_header('Referer', refer)
            # logging.DEBUG("REQUEST requesting {url} with header:\t{header}\tdata:\t{data}".format(
            #     header = req.headers,
            #     url = str(url),
            #     data = str(data),
            # ))
            try:
                tmp_req = urllib2.urlopen(req, timeout=180)
            except:
                raise IOError
            self.__cookie.save('cookie/cookie.data',ignore_discard=True,ignore_expires=True)
            return tmp_req.read()
        except urllib2.HTTPError, e:
            return e.read()

    def Download(self, url, file):
        output = open(file, 'wb')
        output.write(urllib2.urlopen(url).read())
        output.close()

    #  def urlencode(self, data):
    #    return urllib.quote(data)

    def dumpCookie(self):
        for c in self.__cookie:
            print c.name,'=',c.value

    def getCookie(self, key):
        for c in self.__cookie:
            if c.name == key:
                return c.value
        return ''

    def setCookie(self, key, val, domain):
        ck = cookielib.Cookie(version=0, name=key, value=val, port=None, port_specified=False, domain=domain,
                              domain_specified=False, domain_initial_dot=False, path='/', path_specified=True,
                              secure=False, expires=None, discard=True, comment=None, comment_url=None,
                              rest={'HttpOnly': None}, rfc2109=False)
        self.__cookie.set_cookie(ck)
        self.__cookie.save(ignore_discard=True,ignore_expires=True)
        # self.__cookie.clear() clean cookie
        # vim : tabstop=2 shiftwidth=2 softtabstop=2 expandtab
