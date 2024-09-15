from celery import Celery, shared_task
from crawling.spider import run_spider
from database.session import SessionLocal
from models.crawl_results import CrawlResult, CrawlTask
from core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import time

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from crawling.seo_spider import SEOSpider  # Custom spider


# Set up logging
logger = logging.getLogger(__name__)

# Create a Celery instance
celery_app = Celery(
    "crawler_app",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

@celery_app.task
def start_crawl_task(url: str, depth: int, user_agent: str):
    """
    Celery task that initiates the web crawl.
    This task runs asynchronously in the background.
    """
    # Create a new database session
    db = SessionLocal()

    try:
        logger.info(f"Starting crawl for URL: {url} with depth: {depth}")

        # Start the crawl and collect the data
        for result in run_spider(url, depth, user_agent):
            # Store the crawl result in the database
            crawl_result = CrawlResult(
                url=result['url'],
                title=result['title'],
                meta_description=result['meta_description'],
                links=','.join(result['links'])  # You can serialize links differently
            )
            db.add(crawl_result)
            db.commit()
            db.refresh(crawl_result)
            logger.info(f"Stored crawl result for URL: {result['url']}")
    
    except Exception as e:
        logger.error(f"Error during crawl: {str(e)}")
        db.rollback()
        raise  # Re-raise the error after logging
    
    finally:
        db.close()

    return {"message": f"Crawl completed for {url}"}

# Start a web crawl (simulated for now)
@shared_task
def crawl_website(task_id: str, url: str):
    # Start a new database session
    db: AsyncSession = SessionLocal()

    try:
        # Update task to "in progress"
        task = db.query(CrawlTask).filter(CrawlTask.id == task_id).first()
        task.status = "in progress"
        db.commit()

        # Simulate crawling (delay)
        time.sleep(10)  # Simulate crawl delay

        # Update the task with the result
        task.result = f"Crawl completed for {url}"
        task.status = "completed"
        db.commit()

    except Exception as e:
        # Handle error and update the task as failed
        task.status = "failed"
        task.result = str(e)
        db.commit()

    finally:
        db.close()


@shared_task
def seo_crawler_task(task_id: str, url: str, depth: int, user_agent: str):
    """
    This task runs the SEO Crawler for a given URL.
    """
    # Set up Scrapy settings and configure the spider
    process = CrawlerProcess(settings={
        "USER_AGENT": user_agent,
        "DEPTH_LIMIT": depth,
        "LOG_ENABLED": False  # You can enable logging for debugging
    })

    # Run the Scrapy spider
    process.crawl(SEOSpider, project_id=task_id, start_urls=[url])
    process.start()

    return {"task_id": task_id, "status": "completed"}
