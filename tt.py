from bs4 import BeautifulSoup
from collections import defaultdict
import pytumblr
import re
import requests
from py2neo import Graph, Node, Relationship

OAUTH_CONSUMER_KEY = '0sFnDqbRllQnFElwbHtZspHwuYUHhXdbT1kg72dO0RmzchYPMw'
OAUTH_CONSUMER_SECRET = 'agMPypO9iiddKKNpCWVSrcVXQl82xKPMKXmoIgbCDvFaxxBi4N'
CLIENT_TOKEN = 'WMwwkDGAbKBUbdiS8lo2kRg4Kcj5ZdHD60qKWZaQqVyygRVXEF'
CLIENT_SECRET = 'RwY9xJ1B6vbVhAGkeyXgZ7tn2gb6nxyM6zt9eTD8WzYmhTwoN1'

client = pytumblr.TumblrRestClient(
  OAUTH_CONSUMER_KEY,
  OAUTH_CONSUMER_SECRET,
  CLIENT_TOKEN,
  CLIENT_SECRET,
)

def __reblogs_from_html(soup):
    reblogs = []
    for action in soup.find_all('li', class_='reblog'):
        if 'original_post' not in action.attrs['class']:
            reblog = {}
            reblog['reblogger'] = action.find('a', class_='tumblelog').text
            reblogged_from = action.find('a', class_='source_tumblelog')
            if reblogged_from:
                reblog['reblogged_from'] = reblogged_from.text
            reblogs.append(reblog)
    return reblogs

def __find_notes_key(soup):
    """ Find the mysterious note key, necessary to hit the <blog>/notes/<post_id> endpoint """
    return re.search('/notes/\d+/(.+)\?', str(soup.find('a', class_='more_notes_link'))).group(1)

def __find_notes_from_c(soup):
    """ return the 'from_c' param, used for pagination... """
    return re.search('from_c=(\d+)', str(soup.find('a', class_='more_notes_link'))).group(1)

def __find_next_page_url(soup, blog_url, note_id):
    try:
        return 'http://%s.tumblr.com/notes/%s/%s?from_c=%s' % (blog_url, note_id, __find_notes_key(soup), __find_notes_from_c(soup))
    except AttributeError:
        return None

def find_reblogs(post):
    soup = BeautifulSoup(requests.get(post['post_url']).text)
    # Get the initial page reblogs
    reblogs = __reblogs_from_html(soup)

def reblogs_from_tony_abbot():
    soup = BeautifulSoup(requests.get("http://killtonyabbott.tumblr.com/post/121568201181").text)
    reblogs = []
    reblogs.extend(__reblogs_from_html(soup))

    next_url = __find_next_page_url(soup, 'killtonyabbott', 121568201181)
    while next_url is not None:
        soup = BeautifulSoup(requests.get(next_url).text)
        new_reblogs = __reblogs_from_html(soup)
        reblogs.extend(new_reblogs)
        next_url = __find_next_page_url(soup, 'killtonyabbott', 121568201181)
        print next_url, new_reblogs
    return reblogs

def stringies(reblogs):
    everyone = set()
    for reblog in reblogs:
        everyone.add(reblog['reblogger'])
        everyone.add(reblog['reblogged_from'])

    everyone_ids = {}
    for n, person in enumerate(everyone):
        everyone_ids[person] = n

    s = "\n".join([
        "{id: %d, label: '%s'}," % (n, name)
        for name, n in everyone_ids.items()
    ])

    # Edges
    s = "\n".join([
        "{from: %d, to: %d}," % (everyone_ids[rb['reblogger']], everyone_ids[rb['reblogged_from']])
        for rb in reblogs
    ])

def reblogs_into_neo4j(reblogs):
    graph = Graph()
    everyone = set()
    for reblog in reblogs:
        everyone.add(reblog['reblogger'])
        everyone.add(reblog['reblogged_from'])
    nodes = {
        name: Node("User", name=name)
        for name in everyone
    }
    for reblog in reblogs:
        print("Creating (%s)-[:RBF]->(%s)" % (reblog['reblogger'], reblog['reblogged_from']))
        reblogger = nodes[reblog['reblogger']]
        reblogged_from = nodes[reblog['reblogged_from']]
        cxn = Relationship(reblogger, "REBLOGGED_FROM", reblogged_from)
        graph.create(cxn)
