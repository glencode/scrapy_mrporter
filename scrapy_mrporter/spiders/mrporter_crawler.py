import scrapy
from scrapy.http import Request
import csv
import os
from selectorlib import Extractor
import re 

class MrporterCrawlerSpider(scrapy.Spider):
    name = 'Mrporter_crawler'
    allowed_domains = ['mrporter.com']
    start_urls = ['https://www.mrporter.com/en-ke/mens/clothing']
    extractor = Extractor.from_yaml_file(os.path.join(os.path.dirname(__file__), "../resources/search_results2.yml"))
    max_pages = 5

    def start_requests(self):
        """Read keywords from keywords file amd construct the search URL"""

        with open(os.path.join(os.path.dirname(__file__), "../resources/keywords.csv")) as search_keywords:
            for keyword in csv.DictReader(search_keywords):
                search_text=keyword["keyword"]
                url="https://www.mrporter.com/en-ke/mens/search/{}".format(
                    search_text)
                # The meta is used to send our search text into the parser as metadata
                yield scrapy.Request(url, callback = self.parse, meta = {"search_text": search_text})


    def parse(self, response):
        data = self.extractor.extract(response.text,base_url=response.url)
        for product in data['desc, price']:
            yield product
        
        # Try paginating if there is data
        if data['desc, price']:
            if '&page=' not in response.url and self.max_pages>=2:
                yield Request(response.request.url+"&page=2")
            else:
                url = response.request.url
                current_page_no = re.findall('page=(\d+)',url)[0]
                next_page_no = int(current_page_no)+1
                url = re.sub('(^.*?&page\=)(\d+)(.*$)',rf"\g<1>{next_page_no}\g<3>",url)
                if next_page_no <= self.max_pages:
                    yield Request(url,callback=self.parse)
