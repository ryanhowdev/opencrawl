## OpenCrawl SEO Spider

OpenCrawl is a web crawling API built with FastAPI and Celery, designed to allow users to initiate and monitor web crawls. It uses Celery workers to run asynchronous tasks such as web crawling. The results can be retrieved and tracked through API endpoints.

### Features

- **FastAPI**: For handling web requests and providing a REST API.
- **Celery**: For handling asynchronous web crawling tasks.
- **Redis**: Used as a message broker and result backend for Celery.
- **PostgreSQL**: Used as the main database for storing data (currently optional).
- **Docker**: Containerized development using Docker and Docker Compose.
- **Postman**: Test API endpoints to start and monitor crawl tasks.

---

### Prerequisites

- **Python 3.9+**
- **Docker** and **Docker Compose**
- **Postman** for testing the API (optional)

---

### Installation and Setup

#### 1. Clone the Repository

```bash
git clone https://github.com/your-username/OpenCrawl-SEOSpider.git
cd OpenCrawl-SEOSpider
```

#### 2. Set Up the Environment

Create a virtual environment for Python dependencies:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 3. Install Python Dependencies

Install the project dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
```

#### 4. Build and Run with Docker

Build and run the project using Docker and Docker Compose:

```bash
docker-compose up --build
```

This will start the following services:
- **FastAPI** server running on `http://localhost:8000`
- **Redis** on port `6379` for task messaging
- **PostgreSQL** (optional for future task data persistence)
- **Celery worker** for handling web crawls asynchronously

#### 5. Running Celery (Standalone)

To start Celery standalone (useful for local testing):

```bash
docker-compose up celery_worker
```

---

### API Documentation

The following endpoints are available for managing crawl tasks:

#### 1. **Start a Crawl**

- **Endpoint**: `POST /start-crawl/`
- **Description**: Starts a web crawling task by providing the URL to crawl.
- **Request**:
  - URL: `http://localhost:8000/start-crawl/`
  - Method: `POST`
  - Body:
    ```json
    {
      "url": "https://example.com"
    }
    ```
- **Response**:
  ```json
  {
    "task_id": "67ad9b21-e57d-4e53-bc44-0a1eec4a2781",
    "message": "Crawl started"
  }
  ```

#### 2. **Check the Status of a Crawl**

- **Endpoint**: `GET /status/{task_id}`
- **Description**: Returns the status of the crawl task.
- **Request**:
  - URL: `http://localhost:8000/status/{task_id}`
  - Method: `GET`
- **Response**:
  - **In Progress**:
    ```json
    {
      "task_id": "67ad9b21-e57d-4e53-bc44-0a1eec4a2781",
      "status": "Crawl in progress"
    }
    ```
  - **Completed**:
    ```json
    {
      "task_id": "67ad9b21-e57d-4e53-bc44-0a1eec4a2781",
      "status": "Crawl completed",
      "result": {
        "url": "https://example.com",
        "status": "Crawling completed"
      }
    }
    ```
  - **Failed**:
    ```json
    {
      "task_id": "67ad9b21-e57d-4e53-bc44-0a1eec4a2781",
      "status": "Crawl failed",
      "error": "Error message here"
    }
    ```

---

### Using Postman

1. **Start a Crawl**:
   - Method: `POST`
   - URL: `http://localhost:8000/start-crawl/`
   - Body: 
     ```json
     {
       "url": "https://example.com"
     }
     ```

2. **Check the Status**:
   - Method: `GET`
   - URL: `http://localhost:8000/status/{task_id}`

Replace `{task_id}` with the task ID from the response of the `start-crawl` request.

---

### Celery Task Example

In **`app/crawling/tasks.py`**, we define a simple Celery task for crawling:

```python
from celery import shared_task
import time

@shared_task
def crawl_website(url):
    time.sleep(10)  # Simulate a crawl delay
    return {"url": url, "status": "Crawling completed"}
```

The task is triggered when the `/start-crawl/` endpoint is called, and the status can be checked via the `/status/{task_id}` endpoint.

---

### Development Workflow

1. **API Development**: You can test the API endpoints using Postman.
2. **Task Management**: Celery runs the tasks asynchronously, allowing you to scale crawls across multiple workers.
3. **Monitoring**: Use the `/status/{task_id}` endpoint to track the progress of your tasks.
4. **Persistence (optional)**: You can expand the project to store crawl results in PostgreSQL for future querying.

---

### Known Issues

- **Error Handling**: The current setup has basic error handling for failed tasks. Future improvements can include more detailed error logging and retries for failed crawls.
- **Celery Broker**: Redis is used as the message broker. For large-scale applications, consider using RabbitMQ or another message broker for better reliability.

---

### Future Enhancements

- **Task Persistence**: Store crawl results and task statuses in a database (e.g., PostgreSQL) for more advanced querying.
- **Authentication**: Add OAuth2 or API token-based authentication for enhanced security.
- **Web Interface**: Build a web interface to interact with the API and display crawl results in a user-friendly manner.

---

### Conclusion

OpenCrawl SEO Spider is a scalable, flexible web crawling API using FastAPI and Celery. With support for asynchronous tasks, it is designed to handle large-scale crawling jobs. Use Postman to start crawls and monitor their progress.

Feel free to contribute or raise issues to improve the project!
