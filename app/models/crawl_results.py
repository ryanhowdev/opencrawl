from sqlalchemy import Column, Integer, String, Text, DateTime, func
from database.session import Base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from database.session import Base
import uuid

class CrawlResult(Base):
    __tablename__ = "crawl_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), nullable=False)
    url = Column(String(255), nullable=False)
    title = Column(String(255), nullable=True)
    meta_description = Column(Text, nullable=True)
    word_count = Column(Integer, nullable=True)
    internal_links = Column(Integer, nullable=True)
    external_links = Column(Integer, nullable=True)
    seo_evaluation = Column(Text, nullable=True)
    seo_score = Column(Integer, nullable=True)
    raw_html = Column(Text, nullable=True)
    load_time = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CrawlTask(Base):
    __tablename__ = "crawl_tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    url = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False, default="pending")
    result = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
