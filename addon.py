from xbmcswift2 import Plugin
from xbmcswift2 import logger
from scrapper import download_video_page, download_index_page


SUPPORTED_SITES = ['pornfay.com', 'indiangilma.com', 'mastishare.com',
                   'http://indiansexmms.co/']
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
        item['path'] = plugin.url_for('show_video', vidpage=item['path'])
    next_page_item = {'label': 'Next page',
                      'path': plugin.url_for('show_category',
                                             cat=next_page)}
    items.append(next_page_item)
    return plugin.finish(items)


@plugin.route('/video/<vidpage>')
def show_video(vidpage):
    item = download_video_page(vidpage)
    if item:
        return plugin.finish(item)


def get_site_category(site):
    cat = []
    if (site == 'indiangilma.com' or site == 'pornfay.com' or
        site == 'mastishare.com'):
        categories = {'Most Recent': 'http://www.%s/videos?o=mr' % site,
                      'Top Favs': 'http://www.%s/videos?o=tf' % site,
                      'Longest': 'http://www.%s/videos?o=lg' % site}

        for label, path in categories.items():
            cat.append({'label': label,
                        'path': plugin.url_for('show_category', cat=path),
                        'is_playable': False})
    elif site == 'http://indiansexmms.co/':
        items, next_page = download_index_page(site)
        for item in items:
            cat.append({'label': item['label'],
                        'path': plugin.url_for('show_video', vidpage=item['path']),
                        'thumbnail': item['thumbnail'],
                        'is_playable': False})
        next_page_item = {'label': 'Next Page',
                          'path': plugin.url_for('show_category',cat=next_page),
                          'is_playable': False
                          }
        cat.append(next_page_item)

    return cat



if __name__ == '__main__':
    plugin.run()
