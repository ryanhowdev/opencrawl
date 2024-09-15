import scrapy
from scrapy.crawler import CrawlerProcess

class MySpider(scrapy.Spider):
    name = "my_spider"
    
    def __init__(self, url=None, depth=1, user_agent="CrawlBot", *args, **kwargs):
        """
        Initializes the spider with the provided URL, depth, and user agent.
        """
        super(MySpider, self).__init__(*args, **kwargs)
        self.start_urls = [url]
        self.custom_settings = {
            'DEPTH_LIMIT': depth,  # Limit crawling depth
            'USER_AGENT': user_agent  # Custom user agent
        }

    def parse(self, response):
        """
        Parse the response for relevant data and follow links if needed.
        """
        # Extract the page title and meta description
        title = response.css('title::text').get()
        meta_description = response.css('meta[name="description"]::attr(content)').get()
        links = response.css('a::attr(href)').getall()

        # Log or process the results (can be saved to a database or returned via a callback)
        print(f"Crawled URL: {response.url}")
        print(f"Title: {title}")
        print(f"Meta Description: {meta_description}")
        print(f"Found {len(links)} links")

        # Yield the extracted data
        yield {
            'url': response.url,
            'title': title,
            'meta_description': meta_description,
            'links': links
        }

        # Follow links if within depth limit
        for link in links:
            if link.startswith("http"):
                yield response.follow(link, self.parse)

# Function to run the spider
def run_spider(url: str, depth: int, user_agent: str):
    """
    Starts the Scrapy spider with the provided URL and depth.
    This function can be called from the Celery task or directly for testing.
    """
    process = CrawlerProcess({
        'LOG_LEVEL': 'INFO',  # Adjust log level as needed
    })

    # Start the spider with custom parameters
    process.crawl(MySpider, url=url, depth=depth, user_agent=user_agent)
    process.start()  # This will block until the crawling is finished
