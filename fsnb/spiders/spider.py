import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import FfsnbItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'
base = 'https://fsnb.net/category/news/page/{}/'

class FfsnbSpider(scrapy.Spider):
	name = 'fsnb'
	page = 1
	start_urls = [base.format(page)]

	def parse(self, response):
		post_links = response.xpath('//h2/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		if len(post_links) == 12:
			self.page += 1
			yield response.follow(base.format(self.page), self.parse)

	def parse_post(self, response):
		date = response.xpath('//span[@class="updated rich-snippet-hidden"]/text()').get().split('T')[0]
		title = response.xpath('//h1/text()').get() + ' ' + response.xpath('//h3/text()').get()
		content = response.xpath('//div[@class="fusion-text fusion-text-2"]//text()[not (ancestor::p[@class="wp-caption-text"])]|//div[@class="fusion-text fusion-text-1"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=FfsnbItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
