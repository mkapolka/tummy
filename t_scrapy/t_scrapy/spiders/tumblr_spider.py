import scrapy
import json

from t_scrapy.items import TumblrPost

class TumblrSpider(scrapy.Spider):
    name = "tumblr"
    start_urls = [
        "http://api.tumblr.com/v2/blog/buck-diddler.tumblr.com/posts?api_key=jrsCWX1XDuVxAFO4GkK147syAoN8BJZ5voz8tS80bPcj26Vc5Z&reblog_info=true",
    ]
    custom_settings = {
        'DEPTH_LIMIT': 2
    }

    def parse(self, response):
        result = json.loads(response.body)
        for post in result['response']['posts']:
            yield TumblrPost(id=post['id'],
                             poster=post['blog_name'],
                             reblogged_from=post.get('reblogged_from_name', None),
                             reblog_post_id=post.get('reblogged_from_id', None),
                             original_poster=post.get('reblogged_root_name', None),
                             original_post_id=post.get('reblogged_root_id', None))
            if post.get('reblogged_from_name', False):
                yield scrapy.Request("http://api.tumblr.com/v2/blog/%s.tumblr.com/posts?api_key=jrsCWX1XDuVxAFO4GkK147syAoN8BJZ5voz8tS80bPcj26Vc5Z&reblog_info=true" % post['reblogged_from_name'])
            if post.get('reblogged_root_name', False):
                yield scrapy.Request("http://api.tumblr.com/v2/blog/%s.tumblr.com/posts?api_key=jrsCWX1XDuVxAFO4GkK147syAoN8BJZ5voz8tS80bPcj26Vc5Z&reblog_info=true" % post['reblogged_root_name'])
