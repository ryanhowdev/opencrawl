from celery import Celery
from crawling.spider import run_spider
from database.session import SessionLocal
from models.crawl_results import CrawlResult
import logging
from core.config import settings

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
