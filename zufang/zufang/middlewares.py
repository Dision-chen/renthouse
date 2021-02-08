# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from .settings import USER_AGENTS
import random


class RandomUserAgentMiddleware:
    def process_request(self, request, spider):
        useragent = random.choice(USER_AGENTS)
        request.headers["User-Agent"] = useragent



