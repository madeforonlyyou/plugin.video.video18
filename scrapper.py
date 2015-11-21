from xbmcswift2 import logger
from xbmcswift2 import Plugin
from xml.dom import minidom
import re
import os
import requests
from requests.utils import urlparse, urlunparse
from urlparse import parse_qs
from BeautifulSoup import BeautifulSoup


plugin = Plugin()

headers = {'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:41.0) Gecko/20100101 Firefox/41.0',
           'Accept-Encoding': 'identity, deflate'}

class Scrapper(object):
    def __init__(self):
        self.req = requests.session()
        self.req.headers.update(headers)


    def download_page(self, url, **kwargs):
        """ uses to get the xml source from website """
        res = self.req.get(url, **kwargs)
        return (res.status_code, res.text)


class IG(Scrapper):
    def __init__(self):
        super(IG, self).__init__()
        self.site = 'http://indiangilma.com'
        self.config_url = ("http://www.indiangilma.com/media/nuevo/config.php?"
                           "key=%s-1-1")

    def get_next_page(self, url, bs):
        ul = bs.findAll('ul', {'class': 'pagination pagination-lg'})
        page = ul[0].findAll('li',
                             {'class': 'active'},
                             limit=1)[0]('span')[0].text
        next_page_no = int(page) + 1
        parsed_url = urlparse(url)
        pqs = parse_qs(parsed_url.query)
        pqs['page'] = [str(next_page_no)]
        query_list = []
        for k,v in pqs.items():
            query_list.append('%s=%s' % (k,v[0]))
        return parsed_url._replace(query="&".join(query_list))


    def index_page(self, url):
        items = []
        code, page = self.download_page(url)
        bs = BeautifulSoup(page)
        divs = bs.findAll('div', {'class': "col-sm-6 col-md-4 col-lg-4"})
        for div in divs:
            items.append({'label': div('a')[0]('img')[0]['title'],
                          'path': self.site + div('a')[0]['href'],
                          'thumbnail': self.site + div('a')[0]('img')[0]['src'],
                          'is_playable': False})
        return items, urlunparse(self.get_next_page(url, bs))


    def get_download_url(self, text):
        """ gets the url from the xml"""
        try:
            xmldoc = minidom.parseString(text)
            src = xmldoc.getElementsByTagName('file')
            thumb = xmldoc.getElementsByTagName('thumb')
            title = xmldoc.getElementsByTagName('title')
        except:
            plugin.log.debug('Cannot download video: config.php error')
            return []
        item = {'path': src[0].firstChild.data,
                'thumbnail': thumb[0].firstChild.data,
                'label': title[0].firstChild.data,
                'is_playable': True,
                }
        return item

    def get_id(self,url):
        """ Gets the video id from  the url

        Sample url:
        http://www.indiangilma.com/video/1257/mumbai-juhu-beach-teen
        """
        l = url.split('/')
        l.reverse()
        try:
            int(l[1])
            return l[1]
        except ValueError:
            plugin.log.debug("Problem with the url. Unsupported site?")
            return None

class PFay(IG):
    def __init__(self):
        super(PFay, self).__init__()
        self.config_url = ("http://pornfay.com/media/nuevo/config.php?"
                           "key=%s-1-1")
        self.site = 'http://pornfay.com'

class MShare(IG):
    def __init__(self):
        super(MShare, self).__init__()
        self.site = 'http://mastishare.com/'
        self.config_url = 'http://www.mastishare.com/media/nuevo/playlist.php?key=%s'

    def get_download_url(self, text):
        """ gets the url from the xml"""
        try:
            xmldoc = minidom.parseString(text)
            src = xmldoc.getElementsByTagName('file')
            thumb = xmldoc.getElementsByTagName('image')
            title = xmldoc.getElementsByTagName('title')
            title = title[0].firstChild.data
        except Exception as e:
            plugin.log.debug('Cannot download video: config.php error: %s', e)
            return []
        item = {'path': src[0].firstChild.data,
                'thumbnail': thumb[0].firstChild.data,
                'label': title,
                'is_playable': True,
                }
        plugin.log.debug(item)
        return item



    def get_next_page(self, url, bs):
        span = bs.findAll('span', {'class': 'currentpage'})
        page_next  = int(span[0].text) + 1
        next_page_no = int(page_next) + 1
        parsed_url = urlparse(url)
        pqs = parse_qs(parsed_url.query)
        pqs['page'] = [str(next_page_no)]
        query_list = []
        for k,v in pqs.items():
            query_list.append('%s=%s' % (k,v[0]))
        return parsed_url._replace(query="&".join(query_list))

        page_next_url = '/page/%s/' % page_next
        page_next = self.site + page_next_url
        return page_next

    def index_page(self, url):
        items = []
        code, page = self.download_page(url)
        bs = BeautifulSoup(page)
        divs = bs.findAll('div', {'class': 'video_box'})
        for div in divs:
            items.append({'label': div('a')[0]('img')[0]['title'],
                          'path': self.site + div('a')[0]['href'],
                          'thumbnail': self.site + div('a')[0]('img')[0]['src'],
                          'is_playable': False})
        return items, urlunparse(self.get_next_page(url, bs))


class ISMMS(Scrapper):
    def __init__(self):
        super(ISMMS, self).__init__()
        self.site = 'http://indiansexmms.co/'

    def get_next_page(self, url, bs):
        span = bs.findAll('span', {'class': 'current'})
        page_next  = int(span[0].text) + 1
        page_next_url = '/page/%s/' % page_next
        page_next = self.site + page_next_url
        return page_next

    def index_page(self, url):
        items = []
        code, page = self.download_page(url)
        bs = BeautifulSoup(page)
        divs_post = bs.findAll('div', {'class': 'post'})
        for div in divs_post:
            item = {'path': div('a')[0]['href'],
                    'thumbnail': div('img')[0]['src'],
                    'label': div('a')[0]['title'],
                    'is_playable': False,
                    }
            items.append(item)
        return items, self.get_next_page(url, bs)


    def get_download_url(self, source):
        plugin.log.debug("Getting download url %s" % source)
        code, page = self.download_page(source)
        iframe_url = None
        if code != 200:
            plugin.log.debug("cannot download page: %s" % source)
            return (None, None)
        try:
            item = {}
            bs = BeautifulSoup(page)
            for iframe in bs('iframe'):
                if re.search(r'^http://up2stream.com/view', iframe['src']):
                    iframe_url = iframe['src']
            item['label'] = bs('title')[0].text.split('|')[0]
            if iframe_url:
                code, iframe_text = self.download_page(iframe_url, allow_redirects=False)
            else:
                plugin.log.debug("Could not find iframe url from page")
                return (None, None)
            if code != 302:
                plugin.log.debug("Unexpected redirect with code: %s for url %s" % (code, iframe_text))
                return (None, None)
            bs = BeautifulSoup(iframe_text)
            item['thumbnail'] = bs.findAll('video')[0]['poster']
            for source in bs('source'):
                if hasattr(source, 'src'):
                    item['path'] = source['src'].strip()
            item['is_playable'] = True
            return item
        except AttributeError as e:
            plugin.log.debug(e)
            return None


def download_index_page(url):
    ig = None
    if (re.search(r'^http://www.indiangilma.com/', url) or
        re.search(r'^http://indiangilma.com/', url)):
        ig = IG()
    elif (re.search(r'^http://pornfay.com', url) or
          re.search(r'^http://www.pornfay.com', url)):
        ig = PFay()
    elif (re.search(r'^http://mastishare.com', url) or
          re.search(r'^http://www.mastishare.com', url)):
        ig = MShare()
    if ig:
        return ig.index_page(url)
    else:
        ismms = ISMMS()
        return ismms.index_page(url)

def download_video_page(url):
    ig = None
    if (re.search(r'^http://www.indiangilma.com/', url) or
        re.search(r'^http://indiangilma.com/', url)):
        ig = IG()
    elif (re.search(r'^http://pornfay.com', url) or
          re.search(r'^http://www.pornfay.com', url)):
        ig = PFay()
    elif (re.search(r'^http://mastishare.com', url) or
          re.search(r'^http://www.mastishare.com', url)):
        ig = MShare()
    if ig:
        vid = ig.get_id(url)
        if vid:
            source = ig.config_url % str(vid)
            code, text = ig.download_page(source)
            durl = ig.get_download_url(text)
            return [durl]
    else:
        ismms = ISMMS()
        try:
            return [ismms.get_download_url(url)]
        except TypeError as e:
            print e

