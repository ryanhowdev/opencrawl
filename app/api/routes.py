from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from celery.result import AsyncResult
from database.session import get_db, SessionLocal
from models.crawl_results import CrawlResult, CrawlTask
from crawling.tasks import seo_crawler_task
from api.dependencies import verify_token
import uuid

# Create a router instance
router = APIRouter()

# Dependency for database session
async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()

# Request model for starting a crawl
class CrawlRequest(BaseModel):
    url: str
    depth: int = 1  # Depth level to crawl
    user_agent: str = "CrawlBot"  # Ideally get this from config

# Endpoint to start a crawl
@router.post("/start_crawl")
async def start_crawl(request: CrawlRequest, token: str = Depends(verify_token), db: AsyncSession = Depends(get_db)):
    """
    Initiates a new crawl with the given URL and depth.
    """
    # Generate a unique task ID
    task_id = str(uuid.uuid4())
    
    # Store the new crawl task in the database
    new_task = CrawlTask(id=task_id, url=request.url, depth=request.depth, status="pending")
    db.add(new_task)
    await db.commit()

    # Call the Celery task to start the SEO crawl
    seo_crawler_task.delay(task_id, request.url, request.depth, request.user_agent)

    # Call the Celery task to start the crawl
    # start_crawl_task.delay(task_id, request.url, request.depth, request.user_agent)

    return {"message": f"Crawl initiated for {request.url}", "task_id": task_id}

# Endpoint to get the status of a crawl
@router.get("/status/{task_id}")
async def get_status(task_id: str, db: AsyncSession = Depends(get_db), token: str = Depends(verify_token)):
    """
    Retrieves the status of the crawl by task_id.
    """
    # Query the task status from the database
    task = await db.get(CrawlTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return {"task_id": task_id, "status": task.status}

# Endpoint to stop a crawl (future implementation)
@router.post("/stop_crawl/{task_id}")
async def stop_crawl(task_id: str, token: str = Depends(verify_token), db: AsyncSession = Depends(get_db)):
    """
    Stops an ongoing crawl with the given task_id.
    """
    task = await db.get(CrawlTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.status = "stopped"
    await db.commit()

    return {"message": f"Crawl {task_id} has been stopped."}

# Get a single crawl result by ID
@router.get("/crawl_result/{id}")
async def get_crawl_result(id: str, db: AsyncSession = Depends(get_db), token: str = Depends(verify_token)):
    """
    Retrieves a single crawl result by its ID.
    """
    crawl_result = await db.get(CrawlResult, id)
    if not crawl_result:
        raise HTTPException(status_code=404, detail="Crawl result not found")

    return {
        "id": crawl_result.id,
        "url": crawl_result.url,
        "title": crawl_result.title,
        "meta_description": crawl_result.meta_description,
        "links": crawl_result.links.split(',')  # Assuming links are stored as comma-separated strings
    }

# Get all crawl results with pagination
@router.get("/crawl_results")
async def get_all_crawl_results(limit: int = 10, offset: int = 0, db: AsyncSession = Depends(get_db), token: str = Depends(verify_token)):
    """
    Retrieves all crawl results from the database with pagination.
    """
    results = await db.execute(
        "SELECT * FROM crawl_results LIMIT :limit OFFSET :offset",
        {"limit": limit, "offset": offset}
    )
    crawl_results = results.fetchall()

    return [
        {
            "id": result.id,
            "url": result.url,
            "title": result.title,
            "meta_description": result.meta_description,
            "links": result.links.split(',')
        }
        for result in crawl_results
    ]

# Get the result of a specific task by task_id
@router.get("/task_result/{task_id}")
async def get_task_result(task_id: str, db: AsyncSession = Depends(get_db), token: str = Depends(verify_token)):
    """
    Get the result of a specific crawl task.
    """
    # Retrieve task result using Celery's AsyncResult
    result = AsyncResult(task_id)

    if result.state == 'PENDING':
        return {"task_id": task_id, "status": "pending"}
    elif result.state == 'STARTED':
        return {"task_id": task_id, "status": "in progress"}
    elif result.state == 'SUCCESS':
        return {"task_id": task_id, "status": "completed", "result": result.result}
    elif result.state == 'FAILURE':
        return {"task_id": task_id, "status": "failed", "error": str(result.info)}
    else:
        raise HTTPException(status_code=404, detail="Task not found")
