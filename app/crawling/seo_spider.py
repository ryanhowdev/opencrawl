import time
import sqlite3
import scrapy
from collections import defaultdict

class SEOSpider(scrapy.Spider):
    name = "seo_spider"
    start_urls = ['https://ryanlhoward.com']  # Replace with the target URL

    custom_settings = {
        'ITEM_PIPELINES': {'howdev_seo_spider.pipelines.HowdevSEOPipeline': 300},
        'REDIRECT_ENABLED': True,
        'REDIRECT_MAX_TIMES': 5,
    }

    def __init__(self, project_id=1, *args, **kwargs):
        super(SEOSpider, self).__init__(*args, **kwargs)
        self.project_id = int(project_id)  # Set project ID for crawl, change this dynamically for multiple projects

    def parse(self, response):
        # Track the start time for load_time calculation
        start_time = time.time()

        # Initialize SEO data
        seo_data = defaultdict(lambda: "No Issues")

        # Calculate word count
        content_text = response.xpath("//body//text()").getall()
        word_count = len(' '.join(content_text).split())
        seo_data['word_count'] = word_count

        # Extract internal links (only internal links will be crawled)
        internal_links = []
        for link in response.css('a::attr(href)').getall():
            full_url = response.urljoin(link)
            if self.is_internal_link(full_url, response.url):
                internal_links.append(full_url)
                # Yield a new request for internal links only
                yield scrapy.Request(url=full_url, callback=self.parse, meta={'project_id': self.project_id})

        seo_data['internal_links'] = len(internal_links)
        seo_data['external_links'] = len(response.css('a::attr(href)').getall()) - len(internal_links)

        # Extract SEO-related information
        seo_data['url'] = response.url
        seo_data['title'] = response.xpath('//title/text()').get() or "Missing Title"
        seo_data['meta_description'] = response.xpath('//meta[@name="description"]/@content').get() or "Missing Meta Description"

        # Extract H1 to H6 tags
        seo_data['H1'] = ', '.join(response.xpath('//h1/text()').getall()) or "No H1"
        seo_data['H2'] = ', '.join(response.xpath('//h2/text()').getall()) or "No H2"
        seo_data['H3'] = ', '.join(response.xpath('//h3/text()').getall()) or "No H3"
        seo_data['H4'] = ', '.join(response.xpath('//h4/text()').getall()) or "No H4"
        seo_data['H5'] = ', '.join(response.xpath('//h5/text()').getall()) or "No H5"
        seo_data['H6'] = ', '.join(response.xpath('//h6/text()').getall()) or "No H6"

        # Extract alt text from images
        seo_data['alt_texts'] = response.xpath('//img/@alt').getall()

        # Save raw HTML for future analysis
        seo_data['raw_html'] = response.text

        # Calculate page load time
        load_time = time.time() - start_time
        seo_data['load_time'] = load_time

        # Perform SEO evaluation and scoring
        seo_data['seo_evaluation'], seo_data['seo_score'] = self.perform_seo_evaluation(response)

        # Insert crawl data into the database
        self.insert_crawl_data(seo_data)

    def is_internal_link(self, url, base_url):
        base_domain = self.get_domain(base_url)
        link_domain = self.get_domain(url)
        return base_domain == link_domain

    def get_domain(self, url):
        from urllib.parse import urlparse
        parsed_uri = urlparse(url)
        domain = parsed_uri.netloc
        return domain

    def perform_seo_evaluation(self, response):
        seo_issues = []
        score = 100

        # Example SEO evaluation logic for title
        title = response.xpath('//title/text()').get()
        if not title:
            seo_issues.append('Missing Title (Critical Issue)')
            score -= 25
        elif len(title) > 60:
            seo_issues.append('Title Too Long (Minor Issue)')
            score -= 5
        elif len(title) < 30:
            seo_issues.append('Title Too Short (Minor Issue)')
            score -= 5

        # SEO evaluation for meta description
        meta_description = response.xpath('//meta[@name="description"]/@content').get()
        if not meta_description:
            seo_issues.append('Missing Meta Description (Critical Issue)')
            score -= 25
        elif len(meta_description) > 160:
            seo_issues.append('Meta Description Too Long (Minor Issue)')
            score -= 5
        elif len(meta_description) < 50:
            seo_issues.append('Meta Description Too Short (Minor Issue)')
            score -= 5

        # H1 tag evaluation
        h1_tags = response.xpath('//h1/text()').getall()
        if len(h1_tags) > 1:
            seo_issues.append('Multiple H1 Tags (Moderate Issue)')
            score -= 15
        elif not h1_tags:
            seo_issues.append('Missing H1 Tag (Critical Issue)')
            score -= 25

        # Add more SEO evaluation criteria as needed...

        return ", ".join(seo_issues) if seo_issues else "No Issues", score

    def insert_crawl_data(self, seo_data):
        conn = sqlite3.connect('seo_crawler.db')
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO crawls (
                project_id, url, title, meta_description, canonical, H1, H2, H3, H4, H5, H6,
                alt_texts, seo_evaluation, seo_score, word_count, internal_links, external_links,
                broken_links, load_time, raw_html
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            self.project_id,
            seo_data.get('url'),
            seo_data.get('title'),
            seo_data.get('meta_description'),
            seo_data.get('canonical'),
            seo_data.get('H1'),
            seo_data.get('H2'),
            seo_data.get('H3'),
            seo_data.get('H4'),
            seo_data.get('H5'),
            seo_data.get('H6'),
            ', '.join(seo_data.get('alt_texts', [])),
            seo_data.get('seo_evaluation'),
            seo_data.get('seo_score'),
            seo_data.get('word_count'),
            seo_data.get('internal_links'),
            seo_data.get('external_links'),
            seo_data.get('broken_links', 0),  # Default value for broken_links
            seo_data.get('load_time'),
            seo_data.get('raw_html')
        ))

        conn.commit()
        conn.close()
