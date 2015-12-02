# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DmozItem(scrapy.Item):
    title = scrapy.Field()
    link = scrapy.Field()
    desc = scrapy.Field()

class TumblrPost(scrapy.Item):
    id = scrapy.Field()
    poster = scrapy.Field()
    reblogged_from = scrapy.Field()
    reblog_post_id = scrapy.Field()
    original_poster = scrapy.Field()
    original_post_id = scrapy.Field()
    tags = scrapy.Field()
