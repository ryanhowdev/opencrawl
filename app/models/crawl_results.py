from sqlalchemy import Column, Integer, String, Text
from database.session import Base

class CrawlResult(Base):
    __tablename__ = "crawl_results"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, index=True)
    title = Column(String)
    meta_description = Column(Text, nullable=True)
    links = Column(Text, nullable=True)

    def __init__(self, url, title, meta_description, links):
        self.url = url
        self.title = title
        self.meta_description = meta_description
        self.links = links
