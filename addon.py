from xbmcswift2 import Plugin
from xbmcswift2 import logger
from scrapper import download_video_page, download_index_page, get_categories


SUPPORTED_SITES = ['pornfay.com', 'indiangilma.com',
                   'http://indiansexmms.co/', 'naughtymachinima.com']
plugin = Plugin()

if plugin.get_setting('enable_debug', bool):
    plugin.log.setLevel(level=logger.logging.DEBUG)


@plugin.route('/')
def index():
    item = []
    for site in SUPPORTED_SITES:
        item.append({'label': site,
                     'path': plugin.url_for('show_sites', website=site),
                     'is_playable': False
                     })
    return item


@plugin.route('/sites/<website>/')
def show_sites(website):
    items = get_site_category(website)
    return plugin.finish(items)


@plugin.route('/category/<cat>')
def show_category(cat):
    print "Category: %s" % cat
    plugin.log.debug(cat)
    items, next_page = download_index_page(cat)
    for item in items:
        item['path'] = plugin.url_for('show_video',
                                      vidpage=item['path'].encode('utf-8'))
    if next_page:
        next_page_item = {'label': 'Next page',
                          'path': plugin.url_for('show_category',
                                                 cat=next_page)}
        items.append(next_page_item)
    return plugin.finish(items)


@plugin.route('/video/<vidpage>')
def show_video(vidpage):
    item = download_video_page(vidpage)
    plugin.log.debug(item)
    if item:
        plugin.play_video(item)


def get_generes(site):
    items = []
    category_index_url = 'http://www.%s/categories' % site
    items = get_categories(category_index_url)
    if items:
        for item in items:
            item['path'] = plugin.url_for('show_category', cat=item['path'])
    return items


def get_site_category(site):
    cat = []
    if (site == 'indiangilma.com' or site == 'pornfay.com' or
            site == 'mastishare.com' or site == 'naughtymachinima.com'):
        categories = {'Most Recent': 'http://www.%s/videos?o=mr' % site,
                      'Being Watched': 'http://%s/videos?o=bw' % site,
                      'Most viewed': 'http://www.%s/videos?o=mv' % site,
                      'Longest': 'http://www.%s/videos?o=lg' % site,
                      'Top Favorites': 'http://www.%s/videos?o=tf' % site,
                      'Top Rated': 'http://www.%s/videos?o=tr' % site}

        for label, path in categories.items():
            cat.append({'label': label,
                        'path': plugin.url_for('show_category', cat=path),
                        'is_playable': False})
        items = get_generes(site)
        cat = cat + items
    elif site == 'http://indiansexmms.co/':
        items, next_page = download_index_page(site)
        for item in items:
            cat.append({'label': item['label'],
                        'path': plugin.url_for('show_video',
                                               vidpage=item['path']),
                        'thumbnail': item['thumbnail'],
                        'is_playable': False})
        next_page_item = {'label': 'Next Page',
                          'path': plugin.url_for('show_category',
                                                 cat=next_page),
                          'is_playable': False
                          }
        cat.append(next_page_item)

    return cat


if __name__ == '__main__':
    plugin.run()
