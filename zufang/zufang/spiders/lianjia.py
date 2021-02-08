import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from urllib import parse


class LianjiaSpider(CrawlSpider):
    name = 'lianjia'
    allowed_domains = ['lianjia.com']
    start_urls = ['https://gz.lianjia.com/zufang']

    rules = (
        Rule(LinkExtractor(allow=r'https://gz.lianjia.com/zufang/pg\d+'), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        div_list = response.xpath("//div[@class='content__list']/div")
        for div in div_list:
            item = {}
            item["title"] = div.xpath(".//a[@class='content__list--item--aside']/@title").extract_first()
            item["href"] = parse.urljoin(response.url, div.xpath(".//a[@class='content__list--item--aside']/@href").extract_first())
            item["money"] = div.xpath(".//span[@class='content__list--item-price']/em/text()").extract_first()
            yield item
