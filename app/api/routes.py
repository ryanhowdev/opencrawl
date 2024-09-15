from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.session import get_db
from models.crawl_results import CrawlResult
from pydantic import BaseModel
from crawling.tasks import start_crawl_task
from api.dependencies import verify_token

# Create a router instance
router = APIRouter()

# Request model for starting a crawl
class CrawlRequest(BaseModel):
    url: str
    depth: int = 1  # Depth level to crawl
    user_agent: str = "CrawlBot"

# Sample data structure for storing job statuses
jobs = {}

# Endpoint to start a crawl
@router.post("/start_crawl")
async def start_crawl(request: CrawlRequest, token: str = Depends(verify_token), db: Session = Depends(get_db)):
    """
    Initiates a new crawl with the given URL and depth.
    """
    job_id = f"crawl_{len(jobs) + 1}"  # Simple job ID generator
    jobs[job_id] = {"status": "pending", "url": request.url, "depth": request.depth}
    
    # Call the Celery task to start the crawl
    start_crawl_task.delay(request.url, request.depth, request.user_agent)
    
    return {"message": f"Crawl initiated for {request.url}", "job_id": job_id}

# Endpoint to get the status of a crawl
@router.get("/status/{job_id}")
async def get_status(job_id: str, token: str = Depends(verify_token)):
    """
    Retrieves the status of the crawl by job_id.
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return jobs[job_id]

# Endpoint to stop a crawl (future implementation)
@router.post("/stop_crawl/{job_id}")
async def stop_crawl(job_id: str, token: str = Depends(verify_token)):
    """
    Stops an ongoing crawl with the given job_id (to be implemented).
    """
    # Placeholder functionality for now
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    jobs[job_id]["status"] = "stopped"
    
    return {"message": f"Crawl {job_id} has been stopped."}

# New: Get a single crawl result by ID
@router.get("/crawl_result/{id}")
async def get_crawl_result(id: int, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """
    Retrieves a single crawl result by its ID.
    """
    crawl_result = db.query(CrawlResult).filter(CrawlResult.id == id).first()
    if not crawl_result:
        raise HTTPException(status_code=404, detail="Crawl result not found")
    return {
        "id": crawl_result.id,
        "url": crawl_result.url,
        "title": crawl_result.title,
        "meta_description": crawl_result.meta_description,
        "links": crawl_result.links.split(',')  # Assuming links are stored as comma-separated strings
    }

# New: Get all crawl results
@router.get("/crawl_results")
async def get_all_crawl_results(db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """
    Retrieves all crawl results from the database.
    """
    crawl_results = db.query(CrawlResult).all()
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
